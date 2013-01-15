from django.conf import settings
from django.db.models import *
from django_countries import CountryField
from django.contrib.localflavor.us.models import USStateField
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
from django.utils.timezone import utc
import os, sys, pytz, uuid, random
from datetime import *
import time
from tradeschool.widgets import *

def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


class Base(Model):
    """
    Base model for all of the models in ts.  
    """
    class Meta:
        abstract = True
                    
    created     = DateTimeField(auto_now_add=True, editable=False)
    updated     = DateTimeField(auto_now=True, editable=False)
    is_active   = BooleanField(default=1)        
        
    def __unicode__ (self):
        if hasattr(self, "title") and self.title:
            return self.title
        else:
            return "%s" % (type(self))
            

class Location(Base):
    """
    Abstract for location based models: branch & venue.     
    """
    class Meta:
        abstract = True

    title   = CharField(max_length=100, help_text="The name of the space")
    phone   = CharField(max_length=20, blank=True, null=True, help_text="Optional.")
    city    = CharField(max_length=100)
    state   = USStateField(null=True, blank=True, verbose_name="State", help_text="If in the US.")
    country = CountryField()


class Branch(Location):
    """
    A branch is a ts organization in a specific location (usually city/region).
    The branch slug should be used to point to the individual branch app functionality.
    All dates and times in the branch's view templates should reflect the branch's timezone.   
    """    
    
    class Meta:
        verbose_name_plural = "Branches"
        
    COMMON_TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    
    slug        = SlugField(max_length=120, help_text="This is the part that comes after 'http://tradeschool.coop/' in the URL")
    email       = EmailField(max_length=100)
    timezone    = CharField(max_length=100, choices=COMMON_TIMEZONE_CHOICES)
    site        = OneToOneField(Site)

    objects = Manager()
    on_site = CurrentSiteManager()    
    
    def populate_notifications(self):
        "resets branch notification templates from the global branch notification templates"
        
        from notifications.models import DefaultEmailContainer, BranchEmailContainer
        
        # delete existing branch emails
        branch_emails = BranchEmailContainer.objects.filter(branch=self).delete()
            
        # copy branch notification from the branch notification templates
        default_email_container = DefaultEmailContainer.objects.all()[0]
        
        branch_email_container = BranchEmailContainer(branch=self, site=self.site)
        
        for fieldname, email_obj in default_email_container.emails.iteritems():
            new_email = copy_model_instance(email_obj)
            new_email.save()
            setattr(branch_email_container, fieldname, new_email)
        branch_email_container.save()
    
    # def files(self):
    #         """ the branch's custom files """
    #         return ('base.html', 'subpage.html', 'site.css')
    #         
    #     def folder(self):
    #         """ the folder in which to store the branch's files """        
    #         return settings.BRANCH_FILES + '/%s/' % (self.slug) 
    #         
    #     def create_branch_files(self):
    #         """ create the branch's files in the branch's folder """
    #         for filename in self.files():
    #             filename = self.folder() + filename
    #             if not storage.exists(filename):
    #                 storage.save(filename, ContentFile(''))
    #                     
    #     def delete_branch_files(self):
    #         """ delete files & folder """
    #         for filename in self.files():
    #             filename = self.folder() + filename
    #             if storage.exists(filename):
    #                 storage.delete(filename)
    #         os.rmdir(self.folder())
    #                 
    #     def save (self, *args, **kwargs):
    #         """ save and then create branch files """
    #         super(Branch, self).save(*args, **kwargs)
    #         self.create_branch_files()
    #     
    #     def delete(self):
    #         """ delete and then remove branch files """                        
    #         super(Branch, self).delete()
    #         self.delete_branch_files()


class Venue(Location):
    """
    Each branch has venues in which classes take place.
    *   Normal venues are displayed on the front page calendar.
        Alternative venues are created specifically for classes that require a one-time special location.
        For example, a cooking class has to take place in a kitchen,
        but the kitchen is not open for other classses.
    *   The venue's color is a css hex color that is used in the calendars.
    """

    TYPE_CHOICES = ((0, 'Normal'), (1, 'Alternative'))

    def random_color():
        colorValue = random.randint(0, 16777215)
        return "#%x" % colorValue

    venue_type  = SmallIntegerField(max_length=1, choices=TYPE_CHOICES, default=0)
    address_1   = CharField(max_length=50, verbose_name="Street")
    address_2   = CharField(max_length=100, blank=True, null=True)
    capacity    = SmallIntegerField(max_length=4, default=20, help_text="How many people fit in the space?")     
    resources   = TextField(null=True, default="Chairs, Tables", help_text="What resources are available at the space?")
    color       = CharField(max_length=7, default=random_color)
    site        = ForeignKey(Site, default=Site.objects.get_current(), help_text="What TS is this space related to?")

    objects = Manager()
    on_site = CurrentSiteManager()    

class PersonManager(Manager):
    def get_query_set(self):
        return super(PersonManager, self).get_query_set().annotate(
            registration_count  =Count('registrations', distinct=True), 
            courses_taught_count=Count('courses_taught', distinct=True)
        )

class Person(Base):
    """
    Person in the tradeschool system is either a teacher or a student.
    A person submitting a class as a teacher will have to supply a bio as well.
    Hash is used in public urls that involve teachers editing classes & students unregistering
    """
    
    class Meta:
        verbose_name_plural = "People"
            
    fullname    = CharField(max_length=100, verbose_name="your name", help_text="This will appear on the site.")
    email       = EmailField(max_length=100, verbose_name="Email address", help_text="Used only for us to contact you.")
    phone       = CharField(max_length=20, blank=False, null=True, verbose_name="Cell phone number", help_text="Used only for us to contact you.")
    bio         = TextField(blank=True, verbose_name="A few sentences about you", help_text="For prospective students to see on the website")
    website     = URLField(max_length=200, blank=True, null=True, verbose_name="Your website / blog URL", help_text="Optional.")
    hashcode    = CharField(max_length=32, unique=True, default=uuid.uuid1().hex)
    slug        = SlugField(max_length=120, verbose_name="URL Slug", help_text="This will be used to create a unique URL for each person in TS.")
    site        = ManyToManyField(Site, null=True, default=str(Site.objects.get_current().id))
    
    objects = Manager()
    on_site = CurrentSiteManager()
    
    def __unicode__ (self):
        return self.fullname
            

class TeacherManager(PersonManager):
    def get_query_set(self):
        return super(TeacherManager, self).get_query_set().filter(courses_taught_count__gt=0)


class Teacher(Person):
    class Meta:
        proxy = True
        
    objects = TeacherManager()


class StudentManager(PersonManager):
    def get_query_set(self):
        return super(StudentManager, self).get_query_set().filter(registration_count__gt=0)


class Student(Person):
    class Meta:
        proxy = True
 
    objects = StudentManager()
 
            
class Course(Base):
    """
    The Course class
    """

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    CATEGORIES = (
        (0, 'Arts'),
        (1, 'Etc'),
        (2, 'Food'),
        (3, 'Info'),
        (4, 'Lit'),
        (5, 'Music'),
        (6, 'Org')
    )

    teacher         = ForeignKey(Person, limit_choices_to = {'site': Site.objects.get_current()}, related_name='courses_taught')
    category        = SmallIntegerField(max_length=1, choices=CATEGORIES, default=random.randint(0, 6))    
    max_students    = IntegerField(max_length=4, verbose_name="Maximum number of students in your class")
    title           = CharField(max_length=140, verbose_name="class title")    
    slug            = SlugField(max_length=120,blank=False, null=True, verbose_name="URL Slug")
    description     = TextField(blank=False, verbose_name="Class description")
    site       	 	= ManyToManyField(Site, null=True,  default=str(Site.objects.get_current().id))
    
    objects = Manager()
    on_site = CurrentSiteManager()    

class Durational(Base):
    """
    Durational is an abstract model for any model that has a start time and an end time.
    In the tradeschool system, these would be the Time and Course models.
    """
    class Meta:
		abstract = True

    start_time  = DateTimeField(default=datetime.now())
    end_time    = DateTimeField(default=datetime.now())

    formfield_overrides = {
        DateTimeField: {'widget': TsAdminSplitDateTime},
    }
    
    
class Time(Durational):
    """
    Time is an open time slot. It is implemented in the frontend alone:
    These slots populate the calendar for teachers submitting a class.
    Times do not affect the admin class schedluing logic.
    """
    
    class Meta:
        verbose_name        = "Time Slot"
        verbose_name_plural = "Time Slots"
		    
    site    = ForeignKey(Site,  default=Site.objects.get_current())
    
    objects = Manager()
    on_site = CurrentSiteManager()    

    def __unicode__ (self):
        return unicode(self.start_time)

class TimeRange(Base):
    """
    """
    class Meta:
        verbose_name        = "Time Slot Range"
        verbose_name_plural = "Time Slot Ranges"

    start_date  = DateField(default=datetime.now())
    end_date    = DateField(default=datetime.now())
    start_time  = TimeField(default=datetime(2008, 1, 31, 18, 00, 00))
    end_time    = TimeField(default=datetime(2008, 1, 31, 19, 30, 00))
    sunday      = BooleanField()
    monday      = BooleanField()
    tuesday     = BooleanField()
    wednesday   = BooleanField()
    thursday    = BooleanField()
    friday      = BooleanField()
    saturday    = BooleanField()

    site    = ForeignKey(Site, default=Site.objects.get_current())
    
    objects = Manager()
    on_site = CurrentSiteManager()
    

class ScheduleManager(Manager):
   def get_query_set(self):
      return super(ScheduleManager, self).get_query_set().annotate(registered_students=Count('students')).prefetch_related('course')

class ScheduleSiteManager(ScheduleManager):
  def get_query_set(self):
     return super(ScheduleSiteManager, self).get_query_set().filter(course__site__id__exact=settings.SITE_ID)

class ScheduleSitePublicManager(ScheduleSiteManager):
    def get_query_set(self):
        now = datetime.utcnow().replace(tzinfo=utc)
        return super(ScheduleSitePublicManager, self).get_query_set().filter(end_time__gte=now, course__is_active=1, course_status=3)
        
class ScheduleSitePublicPastManager(ScheduleSiteManager):
    def get_query_set(self):
        now = datetime.utcnow().replace(tzinfo=utc)
        return super(ScheduleSitePublicPastManager, self).get_query_set().filter(end_time__lte=now, course__is_active=1, course_status=3)


class Schedule(Durational):
    """
    """

    class Meta:
        verbose_name        = 'Class Schedule'
        verbose_name_plural = 'Class Schedules'
        ordering            = ['course_status', 'start_time', '-venue']
		
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Contacted'),
        (2, 'Updated'),
        (3, 'Approved'),
        (4, 'Rejected')
    )

    venue           = ForeignKey(Venue, limit_choices_to = {'site': Site.objects.get_current()}, null=True, blank=True, help_text="Where is this class taking place?")
    course          = ForeignKey(Course, limit_choices_to = {'site': Site.objects.get_current()}, help_text="What class are you scheduling?")
    course_status   = SmallIntegerField(max_length=1, choices=STATUS_CHOICES, default=0, help_text="What is the current status of the class?")
    hashcode        = CharField(max_length=32, default=uuid.uuid1().hex, unique=True)
    students        = ManyToManyField(Person, through="Registration")    
    slug            = SlugField(max_length=120,blank=False, null=True, unique=True, verbose_name="URL Slug")
    

    objects = ScheduleManager()
    on_site = ScheduleSiteManager()    
    public  = ScheduleSitePublicManager()
    past    = ScheduleSitePublicPastManager()

    def populate_notifications(self):
        "resets course notification templates from the branch notification templates"
        
        from notifications.models import BranchEmailContainer, ScheduleEmailContainer
        
        # delete existing branch emails
        schedule_emails = ScheduleEmailContainer.objects.filter(schedule=self).delete()
            
        # copy course notification from the branch notification templates
        branch_email_container = BranchEmailContainer.objects.filter(site__in=self.course.site.all())[0]
        
        schedule_email_container = ScheduleEmailContainer(schedule=self)
        
        for fieldname, email_obj in branch_email_container.emails.iteritems():
            new_email = copy_model_instance(email_obj)
            new_email.save()
            setattr(schedule_email_container, fieldname, new_email)
        schedule_email_container.save()

    def approve_courses(self, request, queryset):
        "approve multiple courses"
        rows_updated = queryset.update(course_status=3)
        if rows_updated == 1:
            message_bit = "1 class was"
        else:
            message_bit = "%s classes were" % rows_updated
            self.message_user(request, "%s successfully approved." % message_bit)        
    approve_courses.short_description = "Approve Classes"

    def save(self, *args, **kwargs):
        """ check if status was changed to approved and email teacher if it has.""" 
        if self.pk is not None:
            original = Schedule.objects.get(pk=self.pk)
            if original.course_status != self.course_status and self.course_status == 3:
                self.emails.email_teacher(self.emails.teacher_class_approval)
        super(Schedule, self).save(*args, **kwargs)

    def __unicode__ (self):
        return "%s" % (self.course.title)


class BarterItemSiteManager(Manager):
    def get_query_set(self):
       return super(BarterItemSiteManager, self).get_query_set().filter(schedule__course__site__id__exact=settings.SITE_ID)


class BarterItem(Base):
    """
    Barter items are the items that teachers request for a class they're teaching.
    The items themselves can be requested in various classes, but this model
    keeps track of the items that were requested for a class.
    """

    title       = CharField(max_length=255)
    requested   = IntegerField(max_length=3, default=1)
    schedule    = ForeignKey(Schedule, null=True, blank=False)

    objects = Manager()
    on_site = BarterItemSiteManager()

    def __unicode__ (self):
        registered_count = RegisteredItem.objects.filter(barter_item=self).count()
        return u"%s (%i are bringing)" % (self.title, registered_count)

class RegistrationSiteManager(Manager):
    def get_query_set(self):
       return super(RegistrationSiteManager, self).get_query_set().filter(schedule__course__site__id__exact=settings.SITE_ID)

class Registration(Base):
    """
    Registrations represent connections between students and classes.
    When a student registers to a class a registration row is added.
    We do this because we also want to keep track of students who registered
    and then unregistered from a class.
    """

    REGISTRATION_CHOICES = (('registered', 'Registered'),('unregistered', 'Unregistereed'))
    
    schedule            = ForeignKey(Schedule)
    student             = ForeignKey(Person, related_name='registrations')
    registration_status = CharField(max_length=20, choices=REGISTRATION_CHOICES, default='registered')
    items               = ManyToManyField(BarterItem, through="RegisteredItem", blank=False)
        
    objects = Manager()
    on_site = RegistrationSiteManager()    

    def __unicode__ (self):      
        return "%s: %s" % (self.student.fullname, self.registration_status)


class RegisteredItemSiteManager(Manager):
    def get_query_set(self):
       return super(RegisteredItemSiteManager, self).get_query_set().filter(registration__schedule__course__teacher__site__id__exact=settings.SITE_ID)

class RegisteredItem(Base):
    """

    """

    registration    = ForeignKey(Registration)
    barter_item     = ForeignKey(BarterItem)
    registered      = IntegerField(max_length=3, default=1)
    
    objects = Manager()
    on_site = RegisteredItemSiteManager()
    
    def __unicode__ (self):
        return "%s: %i" % (self.barter_item.title, self.registered)


class Feedback(Base):
    """
    Feedback is collected after courses take place.
    """

    author      = OneToOneField(Person)
    course      = ForeignKey(Schedule)
    content     = TextField()
    

    def __unicode__ (self):
        return "feedback from %s" % (self.author.fullname)


# signals are separated to signals.py 
# just for the sake of organization
import signals