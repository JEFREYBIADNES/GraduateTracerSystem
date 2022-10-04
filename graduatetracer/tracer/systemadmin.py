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


def user_graduates(request):
    user_info = User.objects.all().order_by('-id')
    query_IDNum = []
    query_school = []
    query_employment_status = []

    for user_info in user_info:
        if user_info.IDNum not in query_IDNum:
            query_IDNum.append(user_info.IDNum)
        if user_info.school not in query_school:
            query_school.append(user_info.school)
        if user_info.employment_status not in query_employment_status:
            query_employment_status.append(user_info.employment_status)

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(first_name__icontains=query) | Q(middle_name__icontains=query)| Q(last_name__icontains=query)
                           | Q(email__icontains=query))
        if query:
            user_info = User.objects.filter(multiple_query)

        else:
            user_info = User.objects.all().order_by('-id')
    else:
        user_info = User.objects.all().order_by('-id')

    context = {
                'user_info': user_info,
                'query_IDNum': query_IDNum,
                'query_school': query_school,
                'query_employment_status': query_employment_status,
                }
    return render(request, 'tracer/systemadmin/user_graduates.html', context)

def usergrad_informations(request, pk):
    user_info = User.objects.get(id=pk)

    context = {'user_info': user_info}
    return render(request, 'tracer/systemadmin/usergrad_info.html', context)

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


def school_record(request):
    context = {}
    return render(request, 'tracer/systemadmin/school_record.html', context)
