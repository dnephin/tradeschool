from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.admin import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from flatpages_tinymce.admin import FlatPageAdmin
from django.contrib import admin
from admin_enhancer import admin as enhanced_admin
from chunks.models import Chunk
from tradeschool.models import *


class BaseAdmin(enhanced_admin.EnhancedModelAdminMixin, admin.ModelAdmin):
    """Base admin model. Filters objects querysite according to the current branch."""

    # def queryset(self, request):
    #     """Filter the queryset in order to only display objects from the current branch."""
    # 
    #     qs = super(BaseAdmin, self).queryset(request)        
    # 
    #     # superusers get to see all of the data
    #     #if request.user.is_superuser:
    #     #    return qs
    # 
    #     # other users see data filtered by the branch they're associated with
    #     qs = qs.filter(branch__in=request.user.branch_set.all)
    # 
    #     # we need this from the superclass method
    #     ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
    # 
    #     if ordering:
    #         qs = qs.order_by(*ordering)
    #     return qs


class ScheduleInline(admin.TabularInline):
    """Schedule model inline object. 
        Can be used in the Course Admin view in order 
        to allow on the spot scheduling."""
    
    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(ScheduleInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
                    
    model   = Schedule
    extra   = 1
    fields  = ('start_time', 'end_time', 'venue')


class RegistrationInline(admin.TabularInline):
    """Registration model inline object. 
        Used in the Schedule Admin view in order 
        to give an overview of students registered."""

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(RegistrationInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
        
    model   = Registration 
    fields  = ('student', 'registration_status',)
    extra   = 1


class BarterItemInline(admin.TabularInline):
    """BarterItem model inline object. 
        Used in the Schedule Admin view in order 
        to give an overview of the items requested."""

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(BarterItemInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
                    
    model   = BarterItem
    exclude = ('is_active',)    
    extra   = 2


class RegisteredItemInline(admin.TabularInline):
    """RegisteredItem model inline object. 
        Used in the Registration Admin view in order to 
        give an overview of the items checked by each student."""

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(RegisteredItemInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(registration__schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
        
    model   = RegisteredItem
    exclude = ('is_active',)
    extra   = 0


class BranchEmailContainerInline(enhanced_admin.EnhancedAdminMixin, admin.StackedInline):
    """BranchEmailContainer model inline object. 
        Used in the Branch Admin view in order to give 
        an overview of the branch's emails."""

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(BranchEmailContainerInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    model           = BranchEmailContainer
    fields          = ("student_confirmation", "student_reminder", "student_feedback", "teacher_confirmation","teacher_class_approval", "teacher_reminder", "teacher_feedback",)
    extra           = 0
    max_num         = 1
    
    
class ScheduleEmailContainerInline(enhanced_admin.EnhancedAdminMixin, admin.StackedInline):
    """BranchEmailContainer model inline object. 
        Used in the Branch Admin view in order to give 
        an overview of the branch's emails."""

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(ScheduleEmailContainerInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
                    
    model           = ScheduleEmailContainer
    fields          = ("student_confirmation", "student_reminder", "student_feedback", "teacher_confirmation","teacher_class_approval", "teacher_reminder", "teacher_feedback",)
    extra           = 0
    max_num         = 1


class PhotoInline(enhanced_admin.EnhancedAdminMixin, admin.TabularInline):
    """
    """

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(PhotoInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    model               = Photo
    fields              = ('render_image', 'filename', 'position',)
    readonly_fields     = ('render_image',)
    extra               = 0
    sortable_field_name = "position"
    
    def render_image(self, obj):
        return mark_safe("""<img src="%s" class="branch_image"/>""" % obj.filename.url)    
    render_image.short_description = "thumbnail"


class FeedbackInline(enhanced_admin.EnhancedAdminMixin, admin.TabularInline):
    """
    """

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(FeedbackInline, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    
    model   = Feedback
    fields = ('feedback_type', 'content',)
    readonly_fields = ('feedback_type',)
    extra   = 0


class BranchAdmin(BaseAdmin):
    """BranchAdmin lets you add and edit tradeschool branches,
        and reset the email templates for each branch."""
        
    def populate_notifications(self, request, queryset):
        """call the populate_notifications() method in order to reset email templates for the branch."""
        
        for branch in queryset:
            branch.populate_notifications()
    populate_notifications.short_description = "Populate Email Notifications"

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(BranchAdmin, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(pk__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
                   
    actions             = ['populate_notifications']            
    list_display        = ('title', 'slug', 'site', 'city', 'country', 'email', 'is_active')
    list_editable       = ('is_active','site',)
    prepopulated_fields = {'slug': ('title',)}
    inlines             = (BranchEmailContainerInline, PhotoInline)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'site', 'timezone')
        }),
        ('Contact Info', {
            'fields': ('city', 'state', 'country', 'email', 'phone')
        }),
        ('Organizers', {
            'fields': ('organizers',)
        }),        
    )


class VenueAdmin(BaseAdmin):
    """VenueAdmin lets you add and edit venues."""
    
    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(VenueAdmin, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    list_display    = ('title', 'branch', 'address_1', 'city', 'capacity', 'is_active')
    list_editable   = ('branch', 'address_1', 'city', 'capacity', 'is_active',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'branch',)
        }),
        ('Contact Info', {
            'fields': ('address_1', 'city', 'state', 'country', 'phone')
        }),
        ('Additional Info', {
            'fields': ('capacity', 'resources',)
        }),        
    )       


class CourseAdmin(BaseAdmin):
    """CourseAdmin lets you add and edit courses
        and their corresponding schedules."""

    def queryset(self, request):
        """Filter the queryset in order to only display objects from the current branch."""

        qs = super(CourseAdmin, self).queryset(request)        

        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    list_display         = ('title', 'teacher', 'created')
    search_fields        = ('title', 'teacher__fullname')
    inlines              = (ScheduleInline,)
    fields               = ('title', 'slug', 'teacher', 'max_students', 'category', 'description')
    prepopulated_fields  = {'slug': ('title',)}
    
    
class PersonAdmin(BaseAdmin):
    """ PersonAdmin lets you add and edit people in the Trade School system,
        and keep track of the classes they took and taught.
    """ 

    def queryset(self, request):
        """ Annotate the queryset with counts of registrations and courses taught associated with the Person."""
        qs =  super(PersonAdmin, self).queryset(request).annotate(
            registration_count   = Count('registrations', distinct=True), 
            courses_taught_count = Count('courses_taught', distinct=True)
        )
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs        
        
    list_display        = ('fullname', 'email', 'phone', 'courses_taken', 'courses_taught', 'created')    
    search_fields       = ('fullname', 'email', 'phone')
    fields              = ('fullname', 'email', 'phone', 'slug', 'website', 'bio', 'branch')
    prepopulated_fields = {'slug': ('fullname',)}

    def courses_taken(self, obj):
        """ Return registration count from annotated queryset so it can be used in list_display."""
        return obj.registration_count
    courses_taken.short_description = 'Courses Taken'
    courses_taken.admin_order_field = 'registration_count'

    def courses_taught(self, obj):
        """ Return courses taught count from annotated queryset so it can be used in list_display."""        
        return obj.courses_taught_count
    courses_taught.short_description = 'Courses Taught'
    courses_taught.admin_order_field = 'courses_taught_count'


class TeacherAdmin(PersonAdmin):
    """ TeacherAdmin lets you add and edit teachers in the Trade School system,
        A Teacher is a proxy model of Person. The only distinction is that a teacher
        is a person who taught at least 1 class.
    """
    def queryset(self, request):
        """ Filter queryset by the courses taught count, so only people who taught at least one class are returned."""
        qs = super(TeacherAdmin, self).queryset(request).filter(courses_taught_count__gt=0)
       
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs        
            
    list_display = ('fullname', 'email', 'phone', 'courses_taught', 'created')    


class StudentAdmin(PersonAdmin):
    """ StudentAdmin lets you add and edit students in the Trade School system,
        A Student is a proxy model of Person. The only distinction is that a student
        is a person who registered to at least 1 class.
    """    
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(StudentAdmin, self).queryset(request).filter(registration_count__gt=0)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class TimeAdmin(BaseAdmin):
    """ TimeAdmin lets you add and edit time slots in the Trade School system.
    """    
    
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(TimeAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    list_display = ('start_time', 'end_time',)
    fields       = ('start_time', 'end_time', 'branch')


class TimeRangeAdmin(BaseAdmin):
    """ TimeRangeAdmin is a way to create batch time slots. A post save signal adds Time objects.
    """    
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(TimeRangeAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    list_display = ('start_time', 'end_time', 'start_date', 'end_date',)
    fields       = ('start_time', 'end_time', 'start_date', 'end_date', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'branch')


class ScheduleAdmin(BaseAdmin):
    """ ScheduleAdmin lets you add and edit class schedules,
        their barter items, registrations, and email templates.
    """
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(ScheduleAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    def populate_notifications(self, request, queryset):
        """ call the populate_notifications() method in order to reset email templates for the schedule."""        
        for schedule in queryset:
            schedule.populate_notifications()
    populate_notifications.short_description = "Populate Email Notifications"

    def course_title(self, obj):
        """ Return related course title so it can be used in list_display."""
        return obj.course.title

    def teacher_fullname(self, obj):
        """ Return related course's teacher so it can be used in list_display."""        
        return obj.course.teacher.fullname
        
    def teacher_email(self, obj):
        """ Return related course's teacher's email so it can be used in list_display."""
        return obj.course.teacher.email

    list_display    = ('course_title', 'teacher_fullname', 'teacher_email', 'start_time', 'end_time', 'venue', 'course_status', 'created', 'updated')
    list_editable   = ('start_time', 'end_time', 'venue', 'course_status', )
    list_filter     = ('course_status', 'venue__title', 'start_time')
    search_fields   = ('get_course_title', 'get_teacher_fullname')
    inlines         = (BarterItemInline, RegistrationInline, ScheduleEmailContainerInline, FeedbackInline)
    actions         = ('approve_courses', 'populate_notifications')
    fieldsets = (
        ('Class Schedule Info', {
            'fields': ('course', 'slug', 'venue', 'course_status')
        }),
        ('Class Time', {
            'fields': ('start_time', 'end_time',)
        }),
    )
    prepopulated_fields  = {'slug': ('start_time',) }


class RegistrationAdmin(BaseAdmin):
    """ RegistrationAdmin lets you add and edit the student registrations
        as well as the items each student signed up to bring.
    """
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(RegistrationAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    fields = ()
    inlines = (RegisteredItemInline,)


class RegisteredItemAdmin(BaseAdmin):
    """ RegisteredItemAdmin is used mostly for introspection. 
        Editing RegisteredItem should be done within the related Registration or Schedule.
    """
    
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(RegisteredItemAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(registration__schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    fields = ('barter_item', 'registration', 'registered')


class BarterItemAdmin(BaseAdmin):
    """ BarterItemAdmin is used mostly for introspection. 
        Editing BarterItem should be done within the related Schedule.
    """
    
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(BarterItemAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(registration__schedule__course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
            
    list_display    = ('title', 'requested',)    
    list_filter     = ('requested',)
    search_fields   = ('title',)
    fields          = ('title', 'requested')


class SiteChunkAdmin(BaseAdmin):
    """ 
    """     
    pass


class PhotoAdmin(BaseAdmin):
    """ 
    """
    
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(PhotoAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
              
    list_display    = ('get_thumbnail', 'filename', 'position', 'branch')
    
    def get_thumbnail(self, obj):
        """ """
        return obj.thumbnail() 
    get_thumbnail.short_description = 'thumbnail'
    get_thumbnail.allow_tags = True        


class BranchEmailContainerAdmin(enhanced_admin.EnhancedModelAdminMixin, admin.ModelAdmin):
    """
    """
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(BranchEmailContainerAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
                
    list_display = ('branch',)
    fields       = ("student_confirmation", "student_reminder", "student_feedback", "teacher_confirmation","teacher_class_approval", "teacher_reminder", "teacher_feedback",)


class ScheduleEmailContainerAdmin(enhanced_admin.EnhancedModelAdminMixin, admin.ModelAdmin):
    """
    """
    def queryset(self, request):
        """ Filter queryset by the registration count, so only people who took at least one class are returned."""        
        qs = super(ScheduleEmailContainerAdmin, self).queryset(request)
      
        # other users see data filtered by the branch they're associated with
        qs = qs.filter(course__branch__in=request.user.branch_set.all)

        # we need this from the superclass method
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)

        if ordering:
            qs = qs.order_by(*ordering)
        return qs
                
    list_display  = ('schedule',)
    fields        = ("student_confirmation", "student_reminder", "student_feedback", "teacher_confirmation","teacher_class_approval", "teacher_reminder", "teacher_feedback",)


class BranchPageForm(FlatpageForm):
    class Meta:
        model = BranchPage
  

class BranchPageAdmin(FlatPageAdmin):
    """ """
    form = BranchPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'branch')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'branch', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title') 

# register admin models
admin.site.register(Branch, BranchAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Time, TimeAdmin)
admin.site.register(TimeRange, TimeRangeAdmin)
admin.site.register(BarterItem, BarterItemAdmin)
admin.site.register(RegisteredItem, RegisteredItemAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Feedback)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(SiteChunk, SiteChunkAdmin)

admin.site.unregister(FlatPage)
admin.site.register(BranchPage, BranchPageAdmin)

admin.site.register(DefaultEmailContainer)
admin.site.register(BranchEmailContainer, BranchEmailContainerAdmin)
admin.site.register(ScheduleEmailContainer, ScheduleEmailContainerAdmin)

admin.site.register(StudentConfirmation)
admin.site.register(StudentReminder)
admin.site.register(StudentFeedback)
admin.site.register(TeacherConfirmation)
admin.site.register(TeacherClassApproval)
admin.site.register(TeacherReminder)
admin.site.register(TeacherFeedback)