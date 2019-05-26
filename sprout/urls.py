from django.conf.urls import url
# from sprout.views import HomeView
from sprout import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home"),
    # url(r'^$', HomeView.as_view(), name="home"),
    url(r'^recipient/$', views.Recipient.as_view(), name="recipient"),
    url(r'^pay/$', views.pay, name="pay"),
    url(r'^payment_verification/$', views.payment_verification, name="payment_verification"),
    # url(r'^profile/$', views.profile, name="profile"),
]
