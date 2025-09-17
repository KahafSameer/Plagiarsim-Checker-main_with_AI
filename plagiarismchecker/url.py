from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index12/', views.index12, name='index12'),
    path('main/', views.index12, name='plagiarism-check-mainpage'),

    # Separated compare routes
    path('text-compare/', views.text_compare, name='text_compare'),
    path('file-compare/', views.file_compare, name='file_compare'),

    # Web Search
    path('compare/', views.compare, name='compare'),
    path('test/', views.test, name='Test'),
    path('filetest/', views.filetest, name='filetest'),

    # Two input comparison
    path('twofiletest1/', views.twofiletest1, name='twofiletest1'),
    path('twofilecompare1/', views.twofilecompare1, name='twofilecompare1'),
]
