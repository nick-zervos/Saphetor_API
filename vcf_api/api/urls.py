from django.urls import path
from . import views

urlpatterns = [
    path('get_data/', views.getData, name='get-data'),
    path('post_data/', views.postData, name='post-data'),
]