from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Existing dashboard route
    path('camera/', views.camera_dashboard, name='camera_dashboard'),  # Camera page route
    path('save_image/', views.save_image, name='save_image'),  # Route for saving captured image
]
