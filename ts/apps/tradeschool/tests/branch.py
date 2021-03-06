from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from datetime import *
import shutil
import os
import os.path
from tradeschool.models import *


class BranchTestCase(TestCase):
    """ Test the process of setting up a new branch.
    """
    fixtures = ['email_initial_data.json',
                'teacher-info.json',
                'sample_data.json'
                ]

    def setUp(self):
        """ Create a Site and an admin User for testing.
        """
        # test in english so we count html strings correctly
        settings.LANGUAGE_CODE = 'en'

        self.site = Site(
            domain='http://test.tradeschool.coop',
            name='test site',
            id=2
        )
        self.site.save()

        self.password = 'testts123!'
        self.admin = Person.objects.create_superuser(
            username='test_admin',
            fullname="test admin",
            email='tester@tradeschool.coop',
            password=self.password,
        )

        self.branch_add_url = '/admin/tradeschool/branch/add/'
        self.branch_data = {
            'title': 'test branch',
            'city': 'test city',
            'country': 'US',
            'slug': 'test-branch',
            'email': 'test@tradeschool.coop',
            'timezone': 'America/New_York',
            'language': 'en',
            'site': self.site.pk,
            'header_copy': 'header',
            'intro_copy': 'intro text',
            'footer_copy': 'footer text',
            'organizers': self.admin.pk,
            'photo_set-TOTAL_FORMS': 0,
            'photo_set-INITIAL_FORMS': 0,
            'photo_set-MAX_NUM_FORMS': 1000,
        }
        self.empty_form = {
            'photo_set-TOTAL_FORMS': 0,
            'photo_set-INITIAL_FORMS': 0,
            'photo_set-MAX_NUM_FORMS': 1000,
        }
        self.branch = Branch(
            title=self.branch_data['title'],
            city=self.branch_data['city'],
            country=self.branch_data['country'],
            slug=self.branch_data['slug'],
            email=self.branch_data['email'],
            timezone=self.branch_data['timezone'],
            language=self.branch_data['language'],
            site=self.site,
            header_copy=self.branch_data['header_copy'],
            intro_copy=self.branch_data['intro_copy'],
            footer_copy=self.branch_data['footer_copy'],
        )

    def test_branch_creation(self):
        """
        Test valid and invalid branch form submission from admin.
        """
        # Login
        self.client.login(username=self.admin.username, password=self.password)

        # submit an empty form
        response = self.client.post(self.branch_add_url, data=self.empty_form)

        # check that the same template is displayed (form + errors)
        self.assertTemplateUsed('admin/change_form.html')

        # an empty form should return 10 errors for the required fields
        self.assertContains(response, 'This field is required', count=10)

        # now submit valid form
        response = self.client.post(
            self.branch_add_url,
            follow=True,
            data=self.branch_data
        )

        # check that the branch was created successfully, following a redirect
        # self.assertRedirects(
        #     response,
        #     response.redirect_chain[0][0],
        #     response.redirect_chain[0][1]
        # )
        self.assertTemplateUsed('admin/change_list.html')
        self.assertEqual(response.status_code, 200)

    def test_branch_emails(self):
        """ Test that copies of the email templates were created
            When a new branch is saved.
        """
        # save branch
        self.branch.save()

        # verify that the BranchEmailContainer has all 7 Email objects
        self.assertEqual(self.branch.emails.__len__(), 7)

        # store this object in a variable for convenience
        dec = DefaultEmailContainer.objects.all()[0]

        # iterate over the emails in the branch's BranchEmailContainer
        for email_name, branch_email_obj in self.branch.emails.items():
            # find the same email type in the DefaultEmailContainer,
            # where the branch emails were copied from
            default_email = getattr(dec, email_name)

            # verify that the email was copied correctly
            self.assertEqual(branch_email_obj.subject, default_email.subject)
            self.assertEqual(branch_email_obj.content, default_email.content)

    def test_branch_files(self):
        """ Test that the branch-specific files are
            created properly when a new branch is saved.
        """
        # save a new branch
        self.branch.branch_status = 'in_session'
        self.branch.save()

        # check that all branch templates and files were created
        branch_files_dir = os.path.join(
            settings.BRANCH_TEMPLATE_DIR, self.branch.slug)

        default_files_count = len([f for f in os.listdir(settings.DEFAULT_BRANCH_TEMPLATE_DIR) if os.path.isfile(os.path.join(settings.DEFAULT_BRANCH_TEMPLATE_DIR, f))])
        branch_files_count = len([f for f in os.listdir(branch_files_dir) if os.path.isfile(os.path.join(branch_files_dir, f))])

        self.assertEqual(default_files_count, branch_files_count)

    def test_branch_on_homepage(self):
        """ Tests whether a new branch appears on the homepage.
        """
        # render the homepage
        response = self.client.get(reverse('branch-list'))

        # make sure the view loads with the correct template
        self.assertTemplateUsed('hub/branch_list.html')
        self.assertEqual(response.status_code, 200)

        # check that the branch is not there (sanity check)
        self.assertNotContains(response, self.branch_data['slug'])

        # save a new branch
        self.branch.save()

        # render the homepage again
        response = self.client.get(reverse('branch-list'))

        # check that the branch is nor there unless its branch_status
        # is set explicitly to not 'pending'
        self.assertNotContains(response, self.branch_data['slug'])

        # update the branch_status field
        self.branch.branch_status = 'in_session'
        self.branch.save()

        # render the homepage again
        response = self.client.get(reverse('branch-list'))

        # check that the branch is there now
        self.assertContains(response, self.branch_data['slug'])

    def test_branch_templates_loading(self):
        """ Tests whether the branch-specific template files
            are rendered in the various branch views.
        """
        # save a new branch
        self.branch.save()

        # course-list view
        response = self.client.get(reverse(
            'course-list',
            kwargs={'branch_slug': self.branch.slug, })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.branch.slug + '/course_list.html')

    def test_branch_language(self):
        """ Tests that the templates are rendered
            with the branch's language settings.
            Language is one of the fields in the Branch model.
        """
        # get a branch
        branch = Branch.objects.all()[0]
        url = reverse(
            'course-list',
            kwargs={'branch_slug': branch.slug, }
        )

        # verify that all languages that are defined
        # in the base.py settings file
        # can be loaded correctly
        for language_code, language_name in settings.LANGUAGES:
            # save language in branch
            branch.language = language_code
            branch.save()

            # load a page to check the language setting
            response = self.client.get(url)

            self.assertEqual(
                branch.language.lower(),
                response.context['LANGUAGE_CODE']
            )

    def test_branch_timezone(self):
        """ Tests that the timezone stored with the branch
            is used to calculate dates both on the frontend and backend.
        """
        # get a branch
        branch = Branch.objects.all()[0]
        url = reverse(
            'course-list',
            kwargs={'branch_slug': branch.slug, }
        )

        # load a page to check the timezone setting
        response = self.client.get(url)

        # verify the branch's timezone is in the context
        self.assertEqual(response.context['TIME_ZONE'], branch.timezone)

        # login to admin
        self.client.login(username=self.admin.username, password=self.password)

        # get an admin page
        response = self.client.get(self.branch_add_url)

        # verify the branch's timezone is in the context
        self.assertEqual(response.context['TIME_ZONE'], branch.timezone)

    def test_branch_cluster(self):
        """
        """
        # save a cluster
        cluster = Cluster(name='test cluster', slug='test-cluster')
        cluster.save()

        # url for cluster-list view
        url = reverse('cluster-list', kwargs={'slug': cluster.slug, })

        # load the page
        response = self.client.get(url)

        # verify the template loads
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('hub/cluster_list.html')

        # verify the branch is not listed
        self.assertNotContains(response, self.branch.slug)

        # make sure the branch is not pending
        self.branch.branch_status = 'in session'

        self.branch.save()

        # add the branch to the cluster
        self.branch.clusters.add(cluster)

        # reload the page
        response = self.client.get(url)

        # verify the branch is in the view
        self.assertContains(response, self.branch.slug)

    def tearDown(self):
        """ Delete branch files in case something went wrong
            and the files weren't deleted.
        """
        directory = os.path.join(settings.BRANCH_TEMPLATE_DIR, 'test-branch')

        if os.path.exists(directory):
            shutil.rmtree(directory)

        # delete branches' files
        for branch in Branch.objects.all():
            branch.delete_files()
