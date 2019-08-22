from django.conf.urls import url
# from sprout.views import HomeView
from sprout import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home"), # Used with class based view
    # url(r'^$', views.home, name="home"),
    url(r'^new_recipient/$', views.NewRecipient.as_view(), name="new_recipient"),
    url(r'^list_recipients/$', views.ListRecipients.as_view(), name="list_recipients"),
    url(r'^link_recipient/$', views.link_recipient, name="link_recipient"),
    url(r'^pay/$', views.pay, name="pay"),
    url(r'^payment_verification/$', views.payment_verification, name="payment_verification"),
    url(r'^transfer/$', views.transfer, name="transfer"),
    url(r'^resolve_account/$', views.resolve_account, name="resolve_account"),
    url(r'^add_recipient/$', views.add_recipient, name="add_recipient"),
]
