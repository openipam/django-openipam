#from django.contrib.auth.views import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import password_change as auth_password_change
from django.contrib.admin.sites import AdminSite
from django.views.decorators.csrf import requires_csrf_token
from django.template import RequestContext, loader
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.contrib.auth.views import login as auth_login
from django.core.exceptions import ValidationError

from openipam.core.models import FeatureRequest
from openipam.core.forms import ProfileForm, FeatureRequestForm
from openipam.user.forms import IPAMAuthenticationForm

import os
import random
import sys

User = get_user_model()


def index(request):
    if not request.user.get_full_name() or not request.user.email:
        return redirect('profile')
    else:
        context = {
            'email': getattr(settings, 'IPAM_EMAIL_ADDRESS', ''),
            'legacy_domain': getattr(settings, 'IPAM_LEGACY_DOAMIN', ''),
        }
        return AdminSite().index(request, extra_context=context)


def login(request, **kwargs):
    return auth_login(request, authentication_form=IPAMAuthenticationForm, **kwargs)


def mimic(request):
    if request.user.is_ipamadmin:
        mimic_pk = request.POST.get('mimic_pk')
        if mimic_pk:
            try:
                mimic_user = User.objects.get(pk=mimic_pk)
            except User.DoesNotExist:
                pass
            request.session['mimic_user'] = mimic_user.pk
    else:
        if 'mimic_user' in request.session:
            del request.session['mimic_user']

    return redirect('index')


def profile(request):
    """Profile view used with accounts"""

    form = ProfileForm(
        request.POST or None,
        instance=request.user,
    )

    groups = request.user.groups.all()

    # if len(form.initial) < 3:
    #     profile_complete = False
    # else:
    #     for key in form.initial:
    #         if not form.initial[key]:
    #             profile_complete = False
    #             break
    #         else:
    #             profile_complete = True

    if form.is_valid():
        form.save()

        messages.add_message(request, messages.INFO, 'Your profile has been updated.')
        return redirect('profile')

    context = {
        'title': 'Profile for %s' % request.user.get_full_name(),
        'groups': groups,
        'form': form,
    }

    return render(request, 'registration/profile.html', context)


def password_change(request, *args, **kwargs):
    if request.user.has_usable_password():
        return auth_password_change(request, *args, **kwargs)
    else:
        return redirect('admin:index')


@requires_csrf_token
def page_not_found(request, template_name='404.html'):
    kitty_dir = os.path.dirname(os.path.realpath(__file__)) + '/static/core/img/error_cats'
    kitty = random.choice(os.listdir(kitty_dir))
    template = loader.get_template(template_name)
    context = {
        'request_path': request.path,
        'kitty': kitty,
        'email': getattr(settings, 'IPAM_EMAIL_ADDRESS', ''),
        'legacy_domain': getattr(settings, 'IPAM_LEGACY_DOAMIN', ''),
        'request_path': request.path
    }
    body = template.render(RequestContext(request, context))
    return HttpResponseNotFound(body, content_type='text/html')


@requires_csrf_token
def server_error(request, template_name='500.html'):
    kitty_dir = os.path.dirname(os.path.realpath(__file__)) + '/static/core/img/error_cats'
    kitty = random.choice(os.listdir(kitty_dir))
    template = loader.get_template(template_name)
    error_list = []

    try:
        exc_type, exc_value, tb = sys.exc_info()
    except:
        exc_type, exc_value, tb = None, None, None

    if exc_type == ValidationError:
        if hasattr(exc_value, 'error_dict'):
            for key, errors in exc_value.message_dict.items():
                for error in errors:
                    error_list.append(error)
        else:
            error_list.append(exc_value.message)

    if error_list:
        error_list.append('Please try again.')
        messages.error(request, mark_safe('<br />'.join(error_list)))
        return HttpResponseRedirect(request.path)

    context = {
        'request_path': request.path,
        'kitty': kitty,
        'email': getattr(settings, 'IPAM_EMAIL_ADDRESS', ''),
        'legacy_domain': getattr(settings, 'IPAM_LEGACY_DOAMIN', ''),
        'request_path': request.path,
        'error_list': error_list,
    }
    body = template.render(RequestContext(request, context))
    return HttpResponseServerError(body, content_type='text/html')


class FeatureRequestView(CreateView):
    form_class = FeatureRequestForm
    model = FeatureRequest
    success_url = reverse_lazy('feature_request_complete')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.is_complete = False
        self.object.save()
        if self.request.is_ajax():
            return HttpResponse(1)
        else:
            return HttpResponseRedirect(self.get_success_url())


