from django.urls import path

from . import views

urlpatterns = [
    path('<int:filter>/', views.vuz, name='vuz_view'),
    path('prog/<int:vuz_id>/', views.prog, name='prog_view'),
]