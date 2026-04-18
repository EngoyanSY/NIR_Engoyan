from django.urls import path

from . import views

urlpatterns = [
    path("", views.vuz, name="vuz_view"),
    path("<int:vuz_id>/", views.vuz_info, name="vuz_info_view"),
    path("<int:year>/<int:vuz_id>/profit/", views.vuz_profit, name="vuz_profit_view"),
    path("<int:year>/prog/<int:vuz_id>/", views.prog, name="prog_view"),
    path("<int:year>/analitic/prog/<str:field_id>/", views.field_stat, name="prog_stat_view"),
    path("<int:year>/analitic/district/", views.analitic_districts_get, name="analitic_districts_view"),
]
