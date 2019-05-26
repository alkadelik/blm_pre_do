from django.conf.urls import url
# from sprout.views import HomeView
from sprout import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home"),
    # url(r'^$', HomeView.as_view(), name="home"),
    url(r'^receipient/$', views.Receipient.as_view(), name="receipient"),
    url(r'^pay/$', views.pay, name="pay"),
    url(r'^payment_verification/$', views.payment_verification, name="payment_verification"),
    # url(r'^profile/$', views.profile, name="profile"),
]
