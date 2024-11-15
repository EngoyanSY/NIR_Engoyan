from django.shortcuts import render
from django.db.models import F
from .models import (
    Main,
    Vuz,
    Training,
    Program,
    Regions,
    Districts,
    Ministries,
)

def vuz(request, filter):
    if (filter == 0):
        vuz = Vuz.objects.all()
    elif (filter == 1):
        vuz = Vuz.objects.filter(id_parent = F('id_listedu'))
    elif (filter == 2):
        vuz = Vuz.objects.exclude(id_parent = F('id_listedu'))

    vuz = vuz.select_related('id_region', 'id_district', 'id_ministry')
    return render(request, 'vuz/vuz.html', {'vuz': vuz})

def prog(request, vuz_id):
    vuz = Vuz.objects.get(pk=vuz_id)
    vuzid = vuz.id

    main_obj = Main.objects.filter(id_vuz = vuzid).select_related('fieldid', 'progid', 'id_vuz')
    fieldname = main_obj.values('fieldid__fieldname').distinct()
    formname = main_obj.values('formname').distinct()
    prog = main_obj.values('progid__progname').distinct()
    context = {'main_obj': main_obj,
               'fieldname': fieldname,
               'formname': formname,
               'prog': prog,
               }
    return render(request,'vuz/prog.html', context)