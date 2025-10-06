from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('history/', views.history, name='history'),
    path('results/<uuid:id>/', views.results, name='results'),
]
