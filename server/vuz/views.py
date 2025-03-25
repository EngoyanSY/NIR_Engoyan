from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max, Avg, Q, IntegerField,  Value
from django.db.models.functions import Cast
from .models import (
    Main,
    Vuz,
    Training,
)


def vuz(request):
    vuz = Vuz.objects.all().select_related("id_region", "id_district", "id_ministry")
    regions = vuz.values("id_region__region").distinct().order_by("id_region__region")
    districts = (
        vuz.values("id_district__district")
        .distinct()
        .order_by("id_district__district")
    )
    ministry = (
        vuz.values("id_ministry__ministry")
        .distinct()
        .order_by("id_ministry__ministry")
    )
    context = {
        "regions": regions,
        "districts": districts,
        "ministry": ministry,
        "vuz": vuz,
    }
    return render(request, "vuz/vuz.html", context)


def prog(request, vuz_id):
    vuz = Vuz.objects.get(pk=vuz_id)
    vuzid = vuz.id

    main_obj = Main.objects.filter(id_vuz=vuzid).select_related(
        "fieldid", "progid", "id_vuz"
    )
    fieldname = (
        main_obj.values("fieldid__fieldname").distinct().order_by("fieldid__fieldname")
    )
    formname = main_obj.values("formname").distinct().order_by("-formname")
    prog = main_obj.values("progid__progname").distinct().order_by("progid__progname")
    context = {
        "main_obj": main_obj,
        "fieldname": fieldname,
        "formname": formname,
        "prog": prog,
    }
    return render(request, "vuz/prog.html", context)

def field_stat(request, field_id):
    field = Training.objects.get(pk=field_id)
    fieldid = field.fieldid
    print(fieldid)

    main_obj = Main.objects.filter(fieldid=fieldid).select_related(
        "progid", "id_vuz"
    )

    formname = main_obj.values("formname").distinct().order_by("-formname")
    vuzname = main_obj.values("id_vuz__name").distinct().order_by("id_vuz__name")
    prog = main_obj.values("progid__progname").distinct().order_by("progid__progname")
    context = {
        "main_obj": main_obj,
        "formname": formname,
        "vuzname": vuzname,
        "prog": prog,
    }
    return render(request, "vuz/prog_stat.html", context)

def analitic_districts_get(request):
    field_id = request.GET.get("field_id", '')

    filter_condition = {}

    if field_id:
        field = Training.objects.get(pk=field_id)
        filter_condition['fieldid'] = field_id
    else:
        field = ''

    main_obj = (
        Main.objects.filter(**filter_condition)
        .values("id_vuz__id_district__id_district", "id_vuz__id_district__district")
        .exclude(id_vuz__id_district__id_district=9999) 
        .annotate(
            och_avg=Cast(Avg('course1', filter=Q(formname='очная'), default=Value(0)), IntegerField()),
            och_min=Min('course1', filter=Q(formname='очная'), default=Value(0)),
            och_max=Max('course1', filter=Q(formname='очная'), default=Value(0)),
            ochzaoch_avg=Cast(Avg('course1', filter=Q(formname='очно-заочная'), default=Value(0)), IntegerField()),
            ochzaoch_min=Min('course1', filter=Q(formname='очно-заочная'), default=Value(0)),
            ochzaoch_max=Max('course1', filter=Q(formname='очно-заочная'), default=Value(0)),
            zaoch_avg=Cast(Avg('course1', filter=Q(formname='заочная'), default=Value(0)), IntegerField()),
            zaoch_min=Min('course1', filter=Q(formname='заочная'), default=Value(0)),
            zaoch_max=Max('course1', filter=Q(formname='заочная'), default=Value(0))
            
        )
    )

    overall_results = (
        Main.objects.filter(**filter_condition)
        .exclude(id_vuz__id_district__id_district=9999)
        .aggregate(
            overall_och_avg=Cast(Avg('course1', filter=Q(formname='очная'), default=Value(0)), IntegerField()),
            overall_och_min=Min('course1', filter=Q(formname='очная'), default=Value(0)),
            overall_och_max=Max('course1', filter=Q(formname='очная'), default=Value(0)),
            overall_ochzaoch_avg=Cast(Avg('course1', filter=Q(formname='очно-заочная'), default=Value(0)), IntegerField()),
            overall_ochzaoch_min=Min('course1', filter=Q(formname='очно-заочная'), default=Value(0)),
            overall_ochzaoch_max=Max('course1', filter=Q(formname='очно-заочная'), default=Value(0)),
            overall_zaoch_avg=Cast(Avg('course1', filter=Q(formname='заочная'), default=Value(0)), IntegerField()),
            overall_zaoch_min=Min('course1', filter=Q(formname='заочная'), default=Value(0)),
            overall_zaoch_max=Max('course1', filter=Q(formname='заочная'), default=Value(0))
        )
    )

    fields = Training.objects.all().values("fieldname", "fieldid")
    
    context = {
        "fields": fields,
        "field": field,
        "overall_results": overall_results,
        "main_obj": main_obj,
    }
    return render(request, "vuz/analitic_districts.html", context)