#from django.contrib.auth.views import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import password_change as auth_password_change
from django.contrib.admin.sites import AdminSite
from openipam.core.models import FeatureRequest
from openipam.core.forms import ProfileForm, FeatureRequestForm


def index(request):
    if not request.user.get_full_name() or not request.user.email:
        return redirect('profile')
    else:
        return AdminSite().index(request)


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


def password_forgot(request):
    pass


class FeatureRequestView(CreateView):
    form_class = FeatureRequestForm
    model = FeatureRequest
    success_url = reverse_lazy('feature_request_complete')

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                FeatureRequest.objects.create(
                    type=request.POST.get('type'),
                    comment=request.POST.get('comment'),
                    user=request.user
                )
                return HttpResponse(1)
            except:
                return HttpResponse(0, status=500)
        else:
            return super(FeatureRequestView, self).post(request, *args, **kwargs)
