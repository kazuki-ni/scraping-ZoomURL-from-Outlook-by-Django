from django.urls import path
from . import views

app_name= 'scraping_tool'
urlpatterns = [
    path('', views.index, name='index'),
    path('scrape_URLs/', views.scrape_URLs, name='scrape_URLs'),
    path('delete_all/', views.delete_all, name='delete_all'),
    path('join/<int:pk>/', views.join, name='join'),
    path('update/<int:pk>/', views.update, name='update'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path('scrape_sample_URLs/', views.scrape_sample_URLs, name='scrape_sample_URLs'),

]