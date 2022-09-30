from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from .models import *
from .forms import *

from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.contrib import messages

from django.conf import settings

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .decorators import unauthenticated_user, allowed_users
from .forms import RegisterForm, RegisterAdminForm, Profile, GraduateForm, PostForm, CommentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage



# ADMIN
@login_required(login_url='login')
@allowed_users(allowed_roles=['is_approver_admin'])
def admindash(request):
    count_users = User.objects.filter(graduate=True).count()
    count_employed = User.objects.filter(employed=True).count()
    count_unemployed = User.objects.filter(unemployed=True).count()
    count_approved = User.objects.filter(approved=True).count()
    count_pending = User.objects.filter(pending=True).count()

    user = request.user
    context = {
                'count_users': count_users,
                'count_employed': count_employed,
                'count_unemployed': count_unemployed,
                'count_approved': count_approved,
                'count_pending': count_pending,
                }
    return render(request, 'tracer/adminreal/admindash.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['is_approver_admin'])
def pendingaccounts(request):
    gradAccts = User.objects.all()

    context = {'gradAccts': gradAccts}
    return render(request, 'tracer/adminreal/pending.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['is_approver_admin'])
def approvedaccounts(request):
    gradAccts = User.objects.all()

    context = {'gradAccts': gradAccts}
    return render(request, 'tracer/adminreal/approved.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['is_approver_admin'])
def ApprovedUser(request, pk):

    if request.method == 'POST':
        user = User.objects.get(id=pk)
        user.pending = False
        user.approved = True
        user.save()

        template = render_to_string(
                'tracer/firstInterface/emailConfirm_template.html',
                {'name': user.first_name})

        email = EmailMessage(
                             'Confirm To Log In',
                             template,
                             settings.EMAIL_HOST_USER,
                             [user.email],
        )

        email.fail_silently = False
        email.send()

    return redirect('approvedaccounts')


def DisapprovedUser(request, pk):
    user_delete = User.objects.get(id=pk)

    if request.method == 'POST':
        user_delete = User.objects.get(id=pk)
        user_delete.delete()
        return redirect('pendingaccounts')

def displayannounce(request):
    announcements = Announcement.objects.all().order_by('-date_created')
    context = {'announcements': announcements, }
    return render(request, 'tracer/adminreal/displayannounce.html', context)


def addannounce(request):
    announcements = AnnouncementForm()

    if request.method == 'POST':
        image = request.FILES.get('image')
        announcements = AnnouncementForm(request.POST, request.FILES)
        if announcements.is_valid():
            announcements.save()
            messages.success(
                request, 'You have successfully added a new Announcement')
            return redirect('displayannounce')

    context = {'announcements': announcements, }
    return render(request, 'tracer/adminreal/announce.html', context)

def user(request):

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(first_name__icontains=query) | Q(middle_name__icontains=query)
                           | Q(last_name__icontains=query) | Q(job_description__icontains=query) | Q(skill__icontains=query)
                           | Q(date_graduated__icontains=query) | Q(employed__icontains=query) | Q(unemployed__icontains=query))

        if query:
            user_infos = User.objects.filter(multiple_query)
        elif query == None:
            user_infos = User.objects.all()
        elif query == 'Employed' or query == 'employed':
            user_infos = User.objects.filter(employed=True)
        elif query == 'Unemployed' or query == 'unemployed':
            user_infos = User.objects.filter(unemployed=True)
        else:
            user_infos = User.objects.all()
    else:
        user_infos = User.objects.all()
    context = {'user_infos': user_infos}

    return render(request, 'tracer/adminreal/user.html', context)


def userinformation(request, pk):
    user_info = User.objects.get(id=pk)

    context = {'user_info': user_info}
    return render(request, 'tracer/adminreal/userinformation.html', context)

def userinformations(request, pk):
    user_info = User.objects.get(id=pk)

    context = {'user_info': user_info}
    return render(request, 'tracer/adminreal/userinformations.html', context)

def adprof(request, pk):
    user = User.objects.get(id=pk)
    user_info = ProfileForm(instance=user)
    full_name = None
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile')
        user_info = ProfileForm(request.POST, instance=user)
        if profile_picture:
            if user_info.is_valid():
                fs = FileSystemStorage()
                user.profile_picture = fs.save(
                    profile_picture.name, profile_picture)
                user_info.save()
                return redirect('admindash')
        else:
            if user_info.is_valid():
                user_info.save()
                return redirect('admindash')

    context = {'user': user, 'user_info': user_info, 'full_name': full_name}
    return render(request, 'tracer/adminreal/adprof.html', context)
