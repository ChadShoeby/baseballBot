from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('testyfpy', views.testyfpy, name='testyfpy'),
    path('record', views.record, name='record'),    
    path('yahooQueryTest', views.yahooQueryTest, name='yahooQueryTest'),    

]