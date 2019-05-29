from django.conf.urls import url
# from sprout.views import HomeView
from sprout import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home"),
    # url(r'^$', HomeView.as_view(), name="home"),
    url(r'^new_recipient/$', views.NewRecipient.as_view(), name="new_recipient"),
    url(r'^link_recipient/$', views.LinkRecipient.as_view(), name="link_recipient"),
    url(r'^pay/$', views.pay, name="pay"),
    url(r'^payment_verification/$', views.payment_verification, name="payment_verification"),
    url(r'^transfer/$', views.transfer, name="transfer"),
    # url(r'^profile/$', views.profile, name="profile"),
]
