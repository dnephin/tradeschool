import ast
from django.utils import timezone, translation
from django.core.urlresolvers import resolve
from tradeschool.models import *


def reset_translation_cache():
    from django.utils.translation import trans_real
    from django.conf import settings
    import gettext
    if settings.USE_I18N:
        try:
            # Reset gettext.GNUTranslation cache.
            gettext._translations = {}

            # Reset Django by-language translation cache.
            trans_real._translations = {}

            # Delete Django current language translation cache.
            trans_real._default = None

        except AttributeError:
            pass


class BranchMiddleware(object):
    def process_request(self, request):

        reset_translation_cache()

        try:
            url = resolve(request.path)

            # normal requests to branch URLs will have a branch_slug URL param
            branch_slug = url.kwargs.get('branch_slug')

            # ajax requests, however, contain the branch_slug
            # in the the POST data, as part of the Dajaxice arguments
            if (branch_slug is None and
               request.method == 'POST' and
               request.is_ajax()):

                # the incoming data from Dajaxice looks like
                # a Python dictionary, but it's a string.
                # We're parsing it using the ast library
                ajax_dict = ast.literal_eval(request.POST.dict()['argv'])

                # after that we can get the branch_slug value,
                # like from any other dictionary
                branch_slug = ajax_dict['branch_slug']

            try:
                if (branch_slug is None and
                   (url.app_name == 'admin' or url.app_name == 'rosetta') and
                   request.user.is_staff):

                    # translate the admin & rosetta backends
                    # to the language set by the logged in user
                    translation.activate(request.user.language)

                    if request.user.branches.count() > 0:
                        if request.user.default_branch is not None \
                                and request.user.branches_organized.count() > 0:
                            branch = request.user.default_branch
                        else:
                            branch = Branch.objects.filter(
                                organizers=request.user)[0]
                        timezone.activate(branch.timezone)
                    else:
                        pass

                branch = Branch.objects.get(slug=branch_slug)

                timezone.activate(branch.timezone)

                # translate the frontend to the language set in the branch
                translation.activate(branch.language)

            except Branch.DoesNotExist:
                pass
        except ImproperlyConfigured:
            pass
