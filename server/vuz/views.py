from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Min, Max, Avg, Q
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
    field_id = request.GET.get("field_id")
    if not field_id:
        fields = Training.objects.all().values("fieldname", "fieldid")
        context = {
            "fields": fields
        }
        return render(request, "vuz/analitic_districts.html", context=context)
    
    field = get_object_or_404(Training, pk=field_id)
    
    main_obj = (
        Main.objects.filter(fieldid=field_id, )
        .values("id_vuz__id_district__id_district", "id_vuz__id_district__district")
        .exclude(id_vuz__id_district__id_district=9999) 
        .annotate(
            och_avg=Avg('course1', filter=Q(formname='очная')),
            och_min=Min('course1', filter=Q(formname='очная')),
            och_max=Max('course1', filter=Q(formname='очная')),
            ochzaoch_avg=Avg('course1', filter=Q(formname='очно-заочная')),
            ochzaoch_min=Min('course1', filter=Q(formname='очно-заочная')),
            ochzaoch_max=Max('course1', filter=Q(formname='очно-заочная')),
            zaoch_avg=Avg('course1', filter=Q(formname='заочная')),
            zaoch_min=Min('course1', filter=Q(formname='заочная')),
            zaoch_max=Max('course1', filter=Q(formname='заочная'))
        )
    )

    fields = Training.objects.all().values("fieldname", "fieldid")
    
    context = {
        "fields": fields,
        "field": field,
        "main_obj": main_obj,
    }
    return render(request, "vuz/analitic_districts.html", context)