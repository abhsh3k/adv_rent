from django.urls import path
from . import views

urlpatterns = [
    path('login/',              views.login_view,         name='login'),
    path('register/',           views.register,           name='register'),
    path('logout/',             views.logout_view,        name='logout'),
    path('verify-otp/',         views.verify_otp_view,    name='verify_otp'),
    path('resend-otp/',         views.resend_otp,         name='resend_otp'),
    path('forgot-password/',    views.forgot_password,    name='forgot_password'),
    path('reset-password/',     views.reset_password,     name='reset_password'),
    path('profile/',            views.profile,            name='profile'),
    path('link-telegram/',      views.link_telegram,      name='link_telegram'),
    path('unlink-telegram/',    views.unlink_telegram,    name='unlink_telegram'),
    path('verify/',             views.verify_id,          name='verify_id'),
    path('change-contact/',     views.change_contact,     name='change_contact'),      # ← this
    path('verify-contact-otp/', views.verify_contact_otp, name='verify_contact_otp'), # ← and this
    path('admin/verify/', views.verification_queue, name='verification_queue'),
    path('admin/verify/approve/<int:user_id>/', views.approve_user, name='approve_user'),
]