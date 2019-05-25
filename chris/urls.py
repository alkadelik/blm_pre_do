from django.conf.urls import url
from . import views
from django.contrib.auth.views import (
    login,
    logout,
    password_reset,
    password_reset_done,
    password_reset_confirm,
    password_reset_complete
)

urlpatterns = [
    url(r'^$', views.login_redirect, name='login_redirect'),
    url(r'^index/$', login, {'template_name': 'chris/index.html'}, name="login"),
    url(r'^logout/$', logout, {'next_page': '../'}, name="logout"),
    url(r'^register/$', views.register, name='register'),
    # url(r'^home/$', views.home, name="home"),
    url(r'^menu/$', views.menu, name="menu"),
    url(r'^settings/$', views.settings, name="settings"),
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^change_password/$', views.change_password, name="change_password"),
    url(r'^reset_password/$', password_reset,{'template_name':
    'chris/reset_password.html', 'post_reset_redirect':
    'chris:password_reset_done', 'email_template_name':
    'chris/reset_password_email.html'}, name="reset_password"), # See tutorial 31

    url(r'^password_reset/done/$', password_reset_done, {'template_name':
    'chris/reset_password_done.html'}, name="password_reset_done"),

    url(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
    password_reset_confirm, {'template_name':
    'chris/reset_password_confirm.html', 'post_reset_redirect':
    'chris:password_reset_complete'}, name="password_reset_confirm"),

    url(r'^password_reset/complete/$', password_reset_complete, {'template_name':
    'chris/reset_password_complete.html'}, name="password_reset_complete")
]
