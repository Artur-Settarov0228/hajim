from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('image/', views.image_compress, name='image_compress'),
    path('video/', views.video_compress, name='video_compress'),
    path('file/', views.file_compress, name='file_compress'),
    path('upload/', views.upload_file, name='upload_file'),
]
