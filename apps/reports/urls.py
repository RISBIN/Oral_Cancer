from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/<uuid:id>/', views.generate, name='generate'),
    path('download/<uuid:id>/', views.download, name='download'),
]
