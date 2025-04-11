from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),  # Register Page URL
    path('', views.home, name='home'),  # Home Page URL
    path('login/', views.user_login, name='login'),  # Login URL

    path('logout/', views.logout_view, name='logout'),  # Logout URL


    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'), 
    path('manage_post/', views.manage_post, name='manage_post'),
    path('create_post/', views.create_post, name='create_post'), 
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('captcha/', views.generate_captcha, name='captcha'),
    path('oxygen-manage/', views.manage_oxygen, name='manage_oxygen'),
    path('oxygen-availability/', views.view_oxygen, name='view_oxygen'),
    path('create_poll/', views.create_poll, name='create_poll'),
    path('delete_poll/<int:poll_id>/', views.delete_poll, name='delete_poll'),
    path('edit_poll/<int:poll_id>/', views.edit_poll, name='edit_poll'),
    path('poll_report/', views.poll_report, name='poll_report'),
    path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('pandemic-polls/', views.pandemic_poll_list, name='pandemic_poll_list'),
    path('pandemic-polls/vote/<int:poll_id>/', views.pandemic_poll_vote, name='pandemic_poll_vote'),
    path('pandemic-polls/thank-you/', views.pandemic_poll_thankyou, name='pandemic_poll_thankyou'),
    # Normal Poll
    path('polls/', views.poll_list, name='poll_list'),
    path('polls/create/', views.create_poll, name='create_normal_poll'),
    path('polls/<int:poll_id>/', views.poll_detail, name='normal_poll_detail'),
    path('polls/<int:poll_id>/edit/', views.edit_poll, name='edit_normal_poll'),
    path('polls/<int:poll_id>/delete/', views.delete_poll, name='delete_normal_poll'),
    path('polls/<int:poll_id>/vote/', views.vote_poll, name='vote_normal_poll'),
    path('normal-polls/', views.user_normal_poll_list, name='user_normal_poll_list'),
    path('normal-polls/vote/<int:poll_id>/', views.normal_poll_vote, name='normal_poll_vote'),
    path('normal-polls/results/<int:poll_id>/', views.normal_poll_results, name='normal_poll_results'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/like/', views.event_like, name='event_like'),
    path('events/<int:event_id>/dislike/', views.event_dislike, name='event_dislike'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('users/', views.admin_user_list, name='admin_user_list'),





    ]
  
   