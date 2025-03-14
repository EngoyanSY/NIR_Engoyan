from django.urls import path

from . import views

urlpatterns = [
    path("", views.vuz, name="vuz_view"),
    path("prog/<int:vuz_id>/", views.prog, name="prog_view"),
    path("prog_stat/<str:field_id>/", views.field_stat, name="prog_stat_view"),
]
