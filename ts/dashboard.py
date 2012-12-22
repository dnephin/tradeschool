"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'tradeschool.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name
from django.conf import settings


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        # tradeschool.coop admin displays all apps        
        if settings.SITE_ID == 1:
            self.children.append(modules.Group(
                title=_('Admin'),
                column=3,
                collapsible=True,
                children= [
                    modules.ModelList(
                        title=_('Everything'),
                        column=1,
                    ),
                ]
            ))
            
        # individual school admin displays only relevant apps
        else:        
            self.children.append(modules.Group(
                _('Trade School'),
                column=1,
                collapsible=True,
                children = [
                    modules.ModelList(
                        title=_('Classes'),
                        column=1,
                        collapsible=True,
                        models=('tradeschool.models.Schedule', 
                                'tradeschool.models.Time',
                                'tradeschool.models.Student',
                                'tradeschool.models.Teacher',
                                'tradeschool.models.Course',
                                'tradeschool.models.Venues'),
                    ),
                    modules.ModelList(
                        title=_('Emails'),
                        column=1,
                        models=('notifications.models.BranchNotificationTemplate', 
                                'notifications.models.BranchNotification',
                                'notifications.models.ScheduleNotification',
                                'mailer.models.MessageLog',
                                'mailer.models.Message'),                    
                    ),
                    modules.ModelList(
                        title=_('Website Content'),
                        column=1,
                        models=('website.models.Photo', 
                                'django.contrib.flatpages.models.FlatPage',),
                    ),   
                    modules.ModelList(
                        title=_('Settings'),
                        column=1,
                        models=('django.contrib.auth.models.Group', 
                                'django.contrib.auth.models.User',),
                    ),
                ]
            ))

        self.children.append(modules.Group(
             title=_('Recent'),
             column=2,
             collapsible=True,
             children = [
        
                # append a feed module for talk.tradeschool.coop posts
                modules.Feed(
                    title=_('Talk TS Posts'),
                    column=1,
                    limit=5,
                    feed_url='http://talk.tradeschool.coop/rss',            
                ),

                # append a recent actions module
                modules.RecentActions(
                    title=_('Recent Actions'),
                    column=1,
                    limit=5,
                )
             ]
        ))        