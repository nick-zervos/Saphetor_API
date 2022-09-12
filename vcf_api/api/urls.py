from django.urls import path
from . import views

urlpatterns = [
    path('get_data/', views.getData, name='get-data'),
    path('post_data/', views.postData, name='post-data'),
    path('put_data/', views.putData, name='put-data'),
    path('delete_data/', views.deleteData, name='delete-data'),
]