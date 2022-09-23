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

# Create your views here.

def error_404_view(request, exception):

    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, 'tracer/firstInterface/404.html', {})

def home(request):
    context = {}
    return render(request, 'tracer/firstInterface/landingPage.html', context)


@unauthenticated_user
def registerPage(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.graduate = True
            form.save()
            return redirect('welcomeMsg')
        else:
            messages.info(
                request, 'The email you used is taken already.')

    context = {'form': form}
    return render(request, 'tracer/firstInterface/register.html', context)


@unauthenticated_user
def loginPage(request):
    user = request.user

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if request.user.approved:
                return redirect('DashboardUser')
            elif request.user.is_admin_sao:
                return redirect('DashboardAdmin')
            elif request.user.is_approver_admin:
                return redirect('admindash')
            else:
                return HttpResponse('You are not authorized to view this page')
        else:
            messages.info(
                request, 'The email/password you’ve entered is incorrect.')

    context = {}
    return render(request, 'tracer/firstInterface/login.html', context)


def logoutUSer(request):
    logout(request)
    return redirect('login')


def welcomeMsg(request):
    return render(request, 'tracer/firstInterface/welcomeMsg.html')


@login_required(login_url='login')
@allowed_users(allowed_roles=['is_graduate'])
def DashboardUser(request):
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by('-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by('-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)
    context = {
                'announcements': announcements,
                'jobs': jobs,
                'job_categories': job_categories,
                'top_notif_announcements': top_notif_announcements,
                'top_notif_jobs': top_notif_jobs,
                'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
                'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
                'user_announcement_notifications_counter': user_announcement_notifications_counter,
                'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
                'user_job_request_notifications_counter': user_job_request_notifications_counter,
                'user_job_category_notif_counter': user_job_category_notif_counter,
    }
    return render(request, 'tracer/user/dashboard.html', context)


def available_jobs(request):
    ads = Advertise.objects.all().order_by('-id')
    query_title = []
    query_category = []
    query_salary = []

    for ad in ads:
        if ad.title not in query_title:
            query_title.append(ad.title)
        if ad.job_category not in query_category:
            query_category.append(ad.job_category)
        if ad.salary not in query_salary:
            query_salary.append(ad.salary)

    count_employed = User.objects.filter(employed=True).count()
    count_unemployed = User.objects.filter(unemployed=True).count()
    count_job_requests = JobRequest.objects.all().count()
    count_jobs_advertised = Advertise.objects.all().count()
    job_categories = JobCategory.objects.all().order_by('-id')

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(title__icontains=query) | Q(description__icontains=query)
                           | Q(date_created__icontains=query))
        if query:
            ads = Advertise.objects.filter(multiple_query)

        else:
            ads = Advertise.objects.all().order_by('-id')
    else:
        ads = Advertise.objects.all().order_by('-id')

    context = {'ads': ads,
               'query_title': query_title,
               'query_category': query_category,
               'query_salary': query_salary,
               'job_categories': job_categories,
               'count_jobs_advertised': count_jobs_advertised,
               'count_employed': count_employed,
               'count_unemployed': count_unemployed,
               'count_job_requests': count_job_requests
               }
    return render(request, 'tracer/user/jobs_available.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['is_graduate'])
def DisplayGradInfo(request):
    grad_infos = User.objects.all
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'grad_infos': grad_infos
               }
    return render(request, 'tracer/user/DisplayInfo.html', context)

# edit information


@login_required(login_url='login')
@allowed_users(allowed_roles=['is_graduate'])
def UpdateGradInfo(request, pk):
    user = User.objects.get(id=pk)
    grad_info = GraduateForm(instance=user)

    if request.method == 'POST':
        profile_picture = request.FILES.get('profile')
        grad_info = GraduateForm(request.POST, instance=user)
        if profile_picture:
            if grad_info.is_valid():
                fs = FileSystemStorage()
                user.profile_picture = fs.save(profile_picture.name, profile_picture)
                grad_info.save()
                return redirect('DisplayGradInfo')
        else:
            if grad_info.is_valid():
                grad_info.save()
                return redirect('DisplayGradInfo')

    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'user': user,
               'grad_info': grad_info
               }

    return render(request, "tracer/user/UpdateInfo.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['is_graduate'])
def GradProfilePicture(request):
   user = request.user
   grad_info = Profile(instance=user)

   if request.method == 'POST':
       profile_picture = request.FILES['profile']
       grad_info = Profile(request.POST, instance=user)
       if grad_info.is_valid():
           fs = FileSystemStorage()
           user.profile_pic = fs.save(profile_picture.name, profile_picture)
           grad_info.save()
           return redirect('DashboardUser')

   jobs = Advertise.objects.all().order_by('-date_created')
   job_categories = JobCategory.objects.all().order_by('-id')
   announcements = Announcement.objects.all().order_by('-date_created')

   top_notif_announcements = Announcement.objects.all().order_by(
       '-date_created').filter(announcement_notif_counter=False)[:3]
   top_notif_jobs = Advertise.objects.all().order_by(
       '-date_created').filter(job_advertise_notif_counter=False)[:3]

   user = request.user
   user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
   user_top_nav_notifications_counter = top_nav_notifications_counter(user)

   user_announcement_notifications_counter = announcement_notifications_counter(
       user)
   user_job_advertise_notifications_counter = job_advertise_notifications_counter(
       user)
   user_job_request_notifications_counter = job_request_notifications_counter(
       user)
   user_job_category_notif_counter = job_category_notifications_counter(user)

   context = {'announcements': announcements,
              'jobs': jobs,
              'job_categories': job_categories,
              'top_notif_announcements': top_notif_announcements,
              'top_notif_jobs': top_notif_jobs,
              'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
              'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
              'user_announcement_notifications_counter': user_announcement_notifications_counter,
              'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
              'user_job_request_notifications_counter': user_job_request_notifications_counter,
              'user_job_category_notif_counter': user_job_category_notif_counter,
              'grad_info': grad_info
              }

   return render(request, "tracer/user/profile.html", context)

def view_ads(request, pk):
    ad = Advertise.objects.get(id=pk)

    context = {'ad': ad}
    return render(request, 'tracer/user/view_ads.html', context)


# views for adding or editing job experiences
@login_required(login_url='login')
@allowed_users(allowed_roles=['is_graduate'])
def HomeJobExperience(request):
    JobExperience = WorkExperiences.objects.filter(graduateUser=request.user)
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'JobExperience': JobExperience
               }

    return render(request, 'tracer/user/JobExperience/homeJobExp.html', context)


def categorized_job(request, category):
    job_category = JobCategory.objects.filter(id=category)

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(title__icontains=query) | Q(description__icontains=query)
                           | Q(date_created__icontains=query))
        if query:
            ads = Advertise.objects.filter(multiple_query)

        else:
            ads = Advertise.objects.all().order_by('-id')
    else:
        ads = Advertise.objects.all().order_by('-id')

    context = {'ads': ads,
               'category': category,
               'job_category': job_category,
               }
    return render(request, 'tracer/user/categorized_job.html', context)


def AddJobExperience(request):
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'values': request.POST,
               }
    if request.method == 'GET':
        return render(request, 'tracer/user/JobExperience/AddExperience.html', context)

# COMPANY NAME
    if request.method == 'POST':
        company_name = request.POST['company_name']

        if not company_name:
            messages.error(request, 'COMPANY NAME IS REQUIRED!!!')
            return render(request, 'tracer/user/JobExperience/AddExperience.html', context)

# ADDRESS
    if request.method == 'POST':
        address = request.POST['address']

        if not address:
            messages.error(request, 'ADDRESS IS REQUIRED!!!')
            return render(request, 'tracer/user/JobExperience/AddExperience.html', context)
# POSITION
    if request.method == 'POST':
        position = request.POST['position']

        if not position:
            messages.error(request, 'POSITION IS REQUIRED!!!')
            return render(request, 'tracer/user/JobExperience/AddExperience.html', context)

# DESCRIPTION
    if request.method == 'POST':
        description = request.POST['description']

        if not description:
            messages.error(request, 'DESCRIPTION IS REQUIRED!!!')
            return render(request, 'tracer/user/JobExperience/AddExperience.html', context)

# DATE STARTED
    if request.method == 'POST':
        experienceStartDate = request.POST['experienceStartDate']

        if not experienceStartDate:
            messages.error(request, 'DATE STARTED IS REQUIRED!!!')
            return render(request, 'tracer/user/JobExperience/AddExperience.html', context)

# DATE LEAVED
    if request.method == 'POST':
        experienceEndDate = request.POST['experienceEndDate']

        if not experienceEndDate:
            messages.error(request, 'DATE LEAVED IS REQUIRED!!!')
            return render(request, 'tracer/user/JobExperience/AddExperience.html', context)

        WorkExperiences.objects.create(graduateUser=request.user, company_name=company_name,
                                       address=address, position=position,
                                       description=description,
                                       experienceStartDate=experienceStartDate,
                                       experienceEndDate=experienceEndDate)

        messages.success(request, "Job Experience Added Successfully!")

        return redirect('HomeJobExperience')


def edit_experience(request, id):
    JobExperiences = WorkExperiences.objects.get(pk=id)
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'JobExperiences': JobExperiences,
               'values': JobExperiences,
               }

    if request.method == 'GET':
        return render(request, 'tracer/user/JobExperience/EditExperience.html', context)
    # COMPANY NAME
    if request.method == 'POST':
        company_name = request.POST['company_name']
        address = request.POST['address']
        position = request.POST['position']
        description = request.POST['description']
        experienceStartDate = request.POST['experienceStartDate']
        experienceEndDate = request.POST['experienceEndDate']

        JobExperiences.graduateUser = request.user
        JobExperiences.company_name = company_name
        JobExperiences.address = address
        JobExperiences.position = position
        JobExperiences.description = description
        JobExperiences.experienceStartDate = experienceStartDate
        JobExperiences.experienceEndDate = experienceEndDate

        JobExperiences.save()
        messages.success(request, "Job Experience UPDATED Successfully!")

        return redirect('HomeJobExperience')


def delete_experience(request, id):
    JobExperiences = WorkExperiences.objects.get(pk=id)
    JobExperiences.delete()
    messages.success(request, 'Work Experience has been deleted.')
    return redirect('HomeJobExperience')


# views for adding friends


@login_required(login_url='login')
@allowed_users(allowed_roles=['is_graduate'])
def FriendsList(request):
    grad_infos = User.objects.all
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'grad_infos': grad_infos
               }
    return render(request, 'tracer/user/friendlist.html', context)


def NewsFeeds(request):
    return render(request, 'tracer/user/dashboard.html')


def AboutView(request):
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               }
    return render(request, 'tracer/user/about.html', context)


class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        login_in_user = request.user
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form,
        }

        return render(request, 'tracer/user/post_list.html', context)

    def post(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-id')
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

        jobs = Advertise.objects.all().order_by('-date_created')
        job_categories = JobCategory.objects.all().order_by('-id')
        announcements = Announcement.objects.all().order_by('-date_created')

        top_notif_announcements = Announcement.objects.all().order_by(
            '-date_created').filter(announcement_notif_counter=False)[:3]
        top_notif_jobs = Advertise.objects.all().order_by(
            '-date_created').filter(job_advertise_notif_counter=False)[:3]

        user = request.user
        user_chat_bot_notifications_count = chat_bot_notifications_counter(
            user)
        user_top_nav_notifications_counter = top_nav_notifications_counter(
            user)

        user_announcement_notifications_counter = announcement_notifications_counter(
            user)
        user_job_advertise_notifications_counter = job_advertise_notifications_counter(
            user)
        user_job_request_notifications_counter = job_request_notifications_counter(
            user)
        user_job_category_notif_counter = job_category_notifications_counter(
            user)

        context = {'announcements': announcements,
                   'jobs': jobs,
                   'job_categories': job_categories,
                   'top_notif_announcements': top_notif_announcements,
                   'top_notif_jobs': top_notif_jobs,
                   'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
                   'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
                   'user_announcement_notifications_counter': user_announcement_notifications_counter,
                   'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
                   'user_job_request_notifications_counter': user_job_request_notifications_counter,
                   'user_job_category_notif_counter': user_job_category_notif_counter,
                   'post_list': posts,
                   'form': form,
                   }

        return render(request, 'tracer/user/post_list.html', context)


class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-id')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'tracer/user/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        comments = Comment.objects.filter(post=post).order_by('-id')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'tracer/user/post_detail.html', context)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'tracer/user//post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'tracer/user//post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'tracer/user//comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)

        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            post.likes.remove(request.user)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)

        if is_dislike:
            post.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
 

#Local Functions


def display_announcement_notification(request, pk):
    notification = Announcement.objects.get(id=pk)
    notification.announcement_notif_counter = True
    notification.save()
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'notification': notification
               }

    return render(request, 'tracer/user/notification_announcements.html', context)


def display_job_advertised_notification(request, pk):
    notification = Advertise.objects.get(id=pk)
    notification.job_advertise_notif_counter = True
    notification.save()
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'notification': notification
               }
    return render(request, 'tracer/user/notification_job_advertise.html', context)


def display_job_request_notification(request, pk):
    notification = JobRequest.objects.get(id=pk)
    notification.job_request_notif_counter = True
    notification.save()
    jobs = Advertise.objects.all().order_by('-date_created')
    job_categories = JobCategory.objects.all().order_by('-id')
    announcements = Announcement.objects.all().order_by('-date_created')

    top_notif_announcements = Announcement.objects.all().order_by(
        '-date_created').filter(announcement_notif_counter=False)[:3]
    top_notif_jobs = Advertise.objects.all().order_by(
        '-date_created').filter(job_advertise_notif_counter=False)[:3]

    user = request.user
    user_chat_bot_notifications_count = chat_bot_notifications_counter(user)
    user_top_nav_notifications_counter = top_nav_notifications_counter(user)

    user_announcement_notifications_counter = announcement_notifications_counter(
        user)
    user_job_advertise_notifications_counter = job_advertise_notifications_counter(
        user)
    user_job_request_notifications_counter = job_request_notifications_counter(
        user)
    user_job_category_notif_counter = job_category_notifications_counter(user)

    context = {'announcements': announcements,
               'jobs': jobs,
               'job_categories': job_categories,
               'top_notif_announcements': top_notif_announcements,
               'top_notif_jobs': top_notif_jobs,
               'user_chat_bot_notifications_count': user_chat_bot_notifications_count,
               'user_top_nav_notifications_counter': user_top_nav_notifications_counter,
               'user_announcement_notifications_counter': user_announcement_notifications_counter,
               'user_job_advertise_notifications_counter': user_job_advertise_notifications_counter,
               'user_job_request_notifications_counter': user_job_request_notifications_counter,
               'user_job_category_notif_counter': user_job_category_notif_counter,
               'notification': notification
               }
    return render(request, 'tracer/user/notification_job_request.html', context)


def display_job_category_notification(request, pk):
    job_category = JobCategory.objects.filter(id=pk)
    notification = JobCategory.objects.get(id=pk)
    notification.job_category_notif_counter = True
    notification.save()

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(title__icontains=query) | Q(description__icontains=query)
                           | Q(date_created__icontains=query))
        if query:
            ads = Advertise.objects.filter(multiple_query)

        else:
            ads = Advertise.objects.all().order_by('-id')
    else:
        ads = Advertise.objects.all().order_by('-id')

    context = {'ads': ads,
               'job_category': job_category,
               'notification': notification,
               }
    return render(request, 'tracer/user/notification_job_catigories.html', context)


def advertise(request):

    job_categories = JobCategory.objects.all()
    ads = AdvertiseForm()
    add_job_categories = JobCategoryForm()
    if request.method == 'POST':
        #Advertise
        if request.POST.get('form_type') == 'ads_form':
            image = request.FILES.get('image')
            ads = AdvertiseForm(request.POST, request.FILES)
            if ads.is_valid():
                ads.save()

                # Success Notification
                title = ads.cleaned_data.get('title')
                messages.success(
                    request, 'You have successfully added a new job')

                # Query posted job
                job_title = ads.cleaned_data.get('title')
                job_description = ads.cleaned_data.get('description')
                job_salary = ads.cleaned_data.get('salary')
                job_category = ads.cleaned_data.get('job_category')
                job_date_created = ads.cleaned_data.get('date_created')

                # Users Registered
                graduates = User.objects.all()

                # Sending mail to graduates
                for graduate in graduates:
                    graduate_email_address = graduate.email
                    associated_users = User.objects.filter(
                        Q(email=graduate_email_address))
                    if associated_users.exists():
                        for user in associated_users:
                            subject = "Job Recommendation"
                            email_template_name = "tracer/admin/email_template.html"
                            email_form = {
                                "email": user.email,
                                'first_name': user.first_name,
                                'middle_name': user.middle_name,
                                'last_name': user.last_name,
                                'job_title': job_title,
                                'job_description': job_description,
                                'job_salary': job_salary,
                                'job_category': job_category,
                                'job_date_created': job_date_created,
                                'domain': '127.0.0.1:8000',
                                'site_name': 'CTU-Ginatilan Recommender System',
                                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                                "user": user,
                                'token': default_token_generator.make_token(user),
                                'protocol': 'http',
                            }
                            email = render_to_string(
                                email_template_name, email_form)
                            # print("Email sent to:" + email_form.email)
                            try:
                                send_mail(subject, email, 'admin@example.com',
                                          [user.email], fail_silently=False)
                            except BadHeaderError:
                                return HttpResponse('Invalid header found.')

                return redirect('advertise')
        #Add Job Category
        elif request.POST.get('form_type') == 'add_job_category_form':
            add_job_categories = JobCategoryForm(request.POST)
            if add_job_categories.is_valid():
                add_job_categories.save()
                messages.success(
                    request, 'You have successfully added a new job category')
                return redirect('advertise')
    else:
        ads = AdvertiseForm()

    context = {'ads': ads, 'add_job_categories': add_job_categories,
               'job_categories': job_categories}
    return render(request, 'tracer/admin/advertise.html', context)


def browser(request):
    ads = Advertise.objects.all().order_by('-id')
    query_title = []
    query_category = []
    query_salary = []

    for ad in ads:
        if ad.title not in query_title:
            query_title.append(ad.title)
        if ad.job_category not in query_category:
            query_category.append(ad.job_category)
        if ad.salary not in query_salary:
            query_salary.append(ad.salary)

    count_employed = User.objects.filter(employed=True).count()
    count_unemployed = User.objects.filter(unemployed=True).count()
    count_job_requests = JobRequest.objects.all().count()
    count_jobs_advertised = Advertise.objects.all().count()
    job_categories = JobCategory.objects.all().order_by('-id')

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(title__icontains=query) | Q(description__icontains=query)
                           | Q(date_created__icontains=query))
        if query:
            ads = Advertise.objects.filter(multiple_query)

        else:
            ads = Advertise.objects.all().order_by('-id')
    else:
        ads = Advertise.objects.all().order_by('-id')

    context = {'ads': ads,
               'query_title': query_title,
               'query_category': query_category,
               'query_salary': query_salary,
               'job_categories': job_categories,
               'count_jobs_advertised': count_jobs_advertised,
               'count_employed': count_employed,
               'count_unemployed': count_unemployed,
               'count_job_requests': count_job_requests
               }
    return render(request, 'tracer/admin/browse.html', context)


def categorized_jobs(request, category):
    job_category = JobCategory.objects.filter(id=category)

    if 'query' in request.GET:
        query = request.GET['query']
        multiple_query = Q(Q(title__icontains=query) | Q(description__icontains=query)
                           | Q(date_created__icontains=query))
        if query:
            ads = Advertise.objects.filter(multiple_query)

        else:
            ads = Advertise.objects.all().order_by('-id')
    else:
        ads = Advertise.objects.all().order_by('-id')

    context = {'ads': ads,
               'category': category,
               'job_category': job_category,
               }
    return render(request, 'tracer/admin/categorized_jobs.html', context)


def view_ad(request, pk):
    ad = Advertise.objects.get(id=pk)

    context = {'ad': ad}
    return render(request, 'tracer/admin/view_advertise.html', context)


def update_ad(request, pk):
    ad = Advertise.objects.get(id=pk)
    update_ad = AdvertiseForm(instance=ad)

    if request.method == 'POST':
        update_ad = AdvertiseForm(request.POST, request.FILES, instance=ad)
        if update_ad.is_valid():
            update_ad.save()
            messages.success(request, 'Successfully updated')
            return redirect('browser')
    else:
        ads = AdvertiseForm()

    context = {'update_ad': update_ad}
    return render(request, "tracer/admin/update_advertisement.html", context)


def delete_ad(request, pk):
    delete_ad = Advertise.objects.get(id=pk)

    if request.method == 'POST':
        delete_ad = Advertise.objects.get(id=pk)
        delete_ad.delete()
        return redirect('browser')


# Recommeder System - SAO User
def job_requests(request):
    count_job_requests = JobRequest.objects.all().count()

    #voting system
    vote_results = JobRequest.objects.all().order_by('job_category', '-total_vote')

    #job_categories
    job_categories = JobCategory.objects.all()

    #job_category types
    job_requests = JobRequest.objects.all()

    context = {'job_requests': job_requests,
               'count_job_requests': count_job_requests,
               'vote_results': vote_results,
               'job_categories': job_categories,
               }

    return render(request, 'tracer/admin/job_requests.html', context)

#Graduate Tracer - Admin


def add_job_categories(request):

    #job_categories
    job_categories = JobCategory.objects.all()

    #job_category requests
    count_job_requests = JobRequest.objects.all().count()
    job_requests = JobRequest.objects.all()

    #adding job_categories to poll
    add_job_categories = JobCategoryForm()
    if request.method == 'POST':
        add_job_categories = JobCategoryForm(request.POST)
        if add_job_categories.is_valid():
            add_job_categories.save()
            return redirect('add_job_categories')

    context = {'job_requests': job_requests,
               'count_job_requests': count_job_requests,
               'add_job_categories': add_job_categories,
               'job_categories': job_categories
               }

    return render(request, "tracer/admin/add_job_categories.html", context)


def add_category_types(request):

    #job_category types
    category_types = CategoryType.objects.all()

    #job_category requests
    count_job_requests = JobRequest.objects.all().count()
    job_requests = JobRequest.objects.all()

    #adding job_category types to poll
    add_category_types = CategoryTypeForm()
    if request.method == 'POST':
        add_category_types = CategoryTypeForm(request.POST)
        if add_category_types.is_valid():
            add_category_types.save()
            return redirect('add_category_types')

    context = {'job_requests': job_requests,
               'count_job_requests': count_job_requests,
               'add_category_types': add_category_types,
               'category_types': category_types
               }

    return render(request, "tracer/admin/add_category_types.html", context)


def display_job_categories(request):
    job_categories = JobCategory.objects.all()
    job_requests = JobRequest.objects.all()
    count_job_categories = JobCategory.objects.all().count()

    context = {'job_categories': job_categories,
               'job_requests': job_requests,
               'count_job_categories': count_job_categories,
               }
    return render(request, "tracer/admin/display_job_categories.html", context)


def update_job_category(request, pk):
    job_category = JobCategory.objects.get(id=pk)
    update_job_category = JobCategoryForm(instance=job_category)

    if request.method == 'POST':
        update_job_category = JobCategoryForm(
            request.POST, instance=job_category)
        if update_job_category.is_valid():
            update_job_category.save()
            messages.success(request, 'Successfully updated')
            return redirect('advertise')
    else:
        category = JobCategoryForm()

    context = {'update_job_category': update_job_category, }
    return render(request, "tracer/admin/update_job_category.html", context)


def delete_job_category(request, pk):
    delete_job_category = JobCategory.objects.get(id=pk)

    if request.method == 'POST':
        delete_job_category = JobCategory.objects.get(id=pk)
        delete_job_category.delete()
        return redirect('advertise')


def display_category_types(request):
    category_types = CategoryType.objects.all()
    count_category_types = CategoryType.objects.all().count()

    return render(request, "tracer/admin/display_category_types.html", {'category_types': category_types, 'count_category_types': count_category_types})


def update_category_type(request, pk):
    category_type = CategoryType.objects.get(id=pk)
    update_category_type = CategoryTypeForm(instance=category_type)

    if request.method == 'POST':
        update_category_type = CategoryTypeForm(
            request.POST, instance=category_type)
        if update_category_type.is_valid():
            update_category_type.save()
            messages.success(request, 'Successfully updated')
            return redirect('display_category_types')
    else:
        category_types = CategoryTypeForm()

    context = {'update_category_type': update_category_type}
    return render(request, "tracer/admin/update_category_type.html", context)


def delete_category_type(request, pk):
    delete_category_type = CategoryType.objects.get(id=pk)

    if request.method == 'POST':
        delete_category_type = CategoryType.objects.get(id=pk)
        delete_category_type.delete()
        return redirect('display_category_types')

# Graduate Tracer - User


def job_category(request):

    #job_categories
    job_categories = JobCategory.objects.all()
    user = request.user
    #job_category request
    job_requests = JobRequestForm()
    if request.method == 'POST':
        job_requests = JobRequestForm(request.POST)
        if job_requests.is_valid():
            instance = job_requests.save(commit=False)
            instance.user = user
            job_requests.save()
            return redirect('dashboard')
    context = {'job_categories': job_categories, 'job_requests': job_requests}
    return render(request, "tracer/admin/job_categories.html", context)


def delete_job_request(request, pk):
    delete_job_request = JobRequest.objects.get(id=pk)

    if request.method == 'POST':
        delete_job_request = JobRequest.objects.get(id=pk)
        delete_job_request.delete()
        return redirect('job_requests')


def category_type(request, pk):

    #number of users
    count_users = User.objects.all().count()
    #job_category types
    display_category_types = JobRequest.objects.all()
    #vote results
    vote_results = JobRequest.objects.all().order_by('job_category', '-total_vote')

    #voting job_category types
    job_requests = get_object_or_404(JobCategory, pk=pk)
    if request.method == "POST":

        temp = ControlVote.objects.get_or_create(
            user=request.user, job_category=job_requests)[0]

        if temp.status == False:
            temp2 = JobRequest.objects.get(
                pk=request.POST.get(job_requests.title))
            temp2.total_vote += 1
            temp2.save()
            temp.status = True
            temp.save()
            return redirect('job_category')
        else:
            messages.success(
                request, 'you have already been voted this job_category.')
            return render(request, 'tracer/admin/category_types.html',
                          {'display_category_types': display_category_types, 'job_requests': job_requests, 'vote_results': vote_results, 'count_users': count_users})
    else:
        return render(request, 'tracer/admin/category_types.html',
                      {'display_category_types': display_category_types, 'job_requests': job_requests, 'vote_results': vote_results, 'count_users': count_users})
