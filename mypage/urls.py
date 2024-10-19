# mypage/urls.py

from django.urls import path
from .views import home, register, login_view, logout_view, view_pending_users, approve_user, create_post, view_all_posts, report_post

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('register/', register, name='register'),  # Registration page
    path('login/', login_view, name='login'),  # Login page
    path('logout/', logout_view, name='logout'),  # Logout page
    path('pending-users/', view_pending_users, name='pending_users'),  # New path for viewing pending users
    path('approve/<int:user_id>/', approve_user, name='approve_user'),
    path('post/create/', create_post, name='create_post'),
    path('posts/', view_all_posts, name='all_posts'),
    path('report/', report_post, name='report_post'),  # Add this line

]
