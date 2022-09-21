from django.urls import path
from .import views
from .import approver
from django.contrib.auth import views as auth_views
from .views import PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, AddLike, AddDislike
urlpatterns = [

    # All
    path('', views.home, name="home"),
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUSer, name="logout"),
    path('welcomemessage/', views.welcomeMsg, name="welcomeMsg"),




    # graduate User  URLs ...

    path('userdashboard/', views.DashboardUser, name="DashboardUser"),
    path('graduate/display-info/',
         views.DisplayGradInfo, name="DisplayGradInfo"),
    path('graduate/update-information/<str:pk>/',
         views.UpdateGradInfo, name='UpdateGradInfo'),
    path('graduates/profile/', views.GradProfilePicture, name="GradProfilePicture"),

    path('graduate/index/job/experiences/',
         views.HomeJobExperience, name="HomeJobExperience"),
    path('graduates/AddJobExperience/',
         views.AddJobExperience, name="AddJobExperience"),
    path('graduates/EDITJobExperience/<int:id>',
         views.edit_experience, name="edit_experience"),
    path('graduates/DELETEJobExperience/<int:id>',
         views.delete_experience, name="delete_experience"),
    path('friendlist/', views.FriendsList, name="friendlist"),
    path('About/', views.AboutView, name="about"),


    # admin URLs ...
    path('admindashboard/', views.DashboardAdmin, name="DashboardAdmin"),
    path('adminApprover/profile/', views.AdminProfilePicture,
         name="AdminProfilePicture"),
    path('display/pending/', views.AdminDisplayPendingAccts,
         name='AdminDisplayPendingAccts'),
    path('display/approved/', views.AdminDisplayApprovedAccts,
         name='AdminDisplayApprovedAccts'),
    path('approve/user/<int:pk>/', views.ApproveUser, name='approveUser'),
    path('disapproved/user/<int:pk>/', views.DeleteUser, name='deleteUser'),





    # User Password Reset
    path('reset_password/',
         auth_views.PasswordResetView.as_view(
             template_name="tracer/firstInterface/password/password_reset.html"),
         name="reset_password"),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="tracer/firstInterface/password/password_reset_sent.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="tracer/firstInterface/password/password_reset_form.html"),
         name="password_reset_confirm"),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="tracer/firstInterface/password/password_reset_done.html"),
         name="password_reset_complete"),


    # URLs for posting updates

    path('newsfeed', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/',
         CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like', AddLike.as_view(), name='like'),
    path('post/<int:pk>/dislike', AddDislike.as_view(), name='dislike'),

    path('notification-job-announcement/<int:pk>/',
         views.display_announcement_notification, name="display_announcement_notification"),
    path('notification-job-advertised/<int:pk>/', views.display_job_advertised_notification,
         name="display_job_advertised_notification"),
    path('notification-job-request/<int:pk>/', views.display_job_request_notification,
         name="display_job_request_notification"),
    path('notification-job-category/<int:pk>/', views.display_job_category_notification,
         name="display_job_category_notification"),

    # Recommender System URL

    # path('dashboard/', views.dashboard, name="dashboard"),
    path('announcement/', views.add_announcements, name="add_announcements"),
    path('browse-announcements/', views.display_announcement,
         name="display_announcements"),
    path('advertise-jobs/', views.advertise, name="advertise"),
    path('view-job/<int:pk>/', views.view_ad, name="view_ad"),
    path('update-advertisement/<int:pk>/', views.update_ad, name="update_ad"),
    path('delete-advertisement/<int:pk>/', views.delete_ad, name="delete_ad"),

    path('browse-jobs/', views.browser, name="browser"),
    path('categorized-jobs/<int:category>',
         views.categorized_jobs, name="categorized_jobs"),

    path('job-requests/', views.job_requests, name="job_requests"),
    path('delete-job-request/<int:pk>/',
         views.delete_job_request, name='delete_job_request'),

    path('users/', views.users, name="users"),
    path('user-info/<int:pk>/', views.user_information, name="user_information"),
    path('user-infos/<int:pk>/', views.user_informations, name="user_informations"),

    path('create-user-management', views.create_user_management, name="create_user_management"),
    path('display-user-management', views.display_user_management, name="display_user_management"),

    path('profile-picture/<int:pk>/',
         views.profile_picture, name="profile_picture"),

    # Graduate Tracer - Adminz
    #Jobs
    path('browse-available-jobs/', views.available_jobs, name="available_jobs"),
    path('add-jobs/', views.add_job_categories, name='add_jobs'),
    path('display-jobs/', views.display_job_categories, name='display_jobs'),
    path('update-jobs/<int:pk>/', views.update_job_category,
         name='update_job_category'),
    path('delete-jobs/<int:pk>/', views.delete_job_category,
         name='delete_job_category'),
    #Job Types
    path('add-job-types/', views.add_category_types, name='add_job_types'),
    path('display-types-of-job/', views.display_category_types,
         name='display_job_types'),
    path('update-job-types/<int:pk>/',
         views.update_category_type, name='update_job_type'),
    path('delete-job-types/<int:pk>/',
         views.delete_category_type, name='delete_job_type'),

    #admindashboard
     path('admindash/', approver.admindash, name='admindash'),
     #create accounts
     path('approvedaccounts/', approver.approvedaccounts, name='approvedaccounts'),
     path('pendingaccounts/', approver.pendingaccounts, name='pendingaccounts'),
     path('approved/user/<int:pk>/', approver.ApprovedUser, name='approvedUser'),
     path('disapproved/user/<int:pk>/', approver.DisapprovedUser, name='disapprovedUser'),
     # Announcements
     path('addannounce/', approver.addannounce, name='addannounce'),
     path('displayannounce/', approver.displayannounce, name='displayannounce'),
     #users
     path('user/', approver.user, name='user'),
     path('userinformation/<int:pk>', approver.userinformation, name='userinformation'),
     path('userinformations/<int:pk>', approver.userinformations, name='userinformations'),
     path('adprof/<int:pk>', approver.adprof, name='adprof'),

    ]
