from django.urls import path

from . import views

urlpatterns = [
    path("", views.vuz, name="vuz_view"),
    path("prog/<int:vuz_id>/", views.prog, name="prog_view"),
    path("analitic/prog/<str:field_id>/", views.field_stat, name="prog_stat_view"),
    path("analitic/district/", views.analitic_districts_get, name="analitic_districts_view"),
]
