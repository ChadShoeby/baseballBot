from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('record', views.record, name='record'),    
    path('yahooQueryTest', views.yahooQueryTest, name='yahooQueryTest'),    
    path('enter-verifier-token', views.get_verifier_token, name='enterVerifierTokenForm'),
]