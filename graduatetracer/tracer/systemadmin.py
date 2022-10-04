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
@allowed_users(allowed_roles=['is_system_admin'])
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
    return render(request, 'tracer/systemadmin/admindash.html', context)


def create_user_management(request):
    adform = RegisterAdminForm()
    if request.method == 'POST':
        adform = RegisterAdminForm(request.POST)
        if adform.is_valid():
            adform.save()
            messages.success(
                request, 'New Account Created Successfully!')
            return redirect('display_user_management')
        else:
            messages.info(
                request, 'The email you used is taken already.')

    context = {'adform': adform}
    return render(request, 'tracer/systemadmin/create_user_management.html', context)

def display_user_management(request):
    ad_info = User.objects.all
    context = {
               'ad_info': ad_info
               }
    return render(request, 'tracer/systemadmin/display_user_management.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['is_system_admin'])
def usersGraduates(request):
    graduateAcctsLists = User.objects.all()

    context = {'graduateAcctsLists': graduateAcctsLists}
    return render(request, 'tracer/systemadmin/user.html', context)


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

    return render(request, 'tracer/systemadmin/user.html', context)


def userinformations(request, pk):
    user_info = User.objects.get(id=pk)

    context = {'user_info': user_info}
    return render(request, 'tracer/systemadmin/userinformations.html', context)

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
    return render(request, 'tracer/systemadmin/adprof.html', context)

def school_report(request):
    context = {}
    return render(request, 'tracer/systemadmin/school_report.html', context)

def displaycoursesArgao(request):
    context = {}
    return render(request, 'tracer/systemadmin/courses.html', context)
