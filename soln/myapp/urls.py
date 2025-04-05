from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),  # Register Page URL
    path('', views.home, name='home'),  # Home Page URL
    path('login/', views.user_login, name='login'),  # Login URL

    path('logout/', views.logout_view, name='logout'),  # Logout URL


    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'), 
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('captcha/', views.generate_captcha, name='captcha'),

    ]
  
   