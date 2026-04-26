from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max, Avg, Q, IntegerField,  Value
from django.db.models import F, Sum, BigIntegerField, DecimalField, ExpressionWrapper
from django.db.models.functions import Cast
import json
from .models import (
    Main,
    Vuz,
    Training,
    Districts,
    Regions,
    Ministries,
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

    fields = (
        Training.objects.all().values("fieldid", "fieldname").distinct().order_by("fieldid")
    )


    context = {
        "regions": regions,
        "districts": districts,
        "ministry": ministry,
        "fields": fields,
        "vuz": vuz,
    }
    return render(request, "vuz/vuz.html", context)


def vuz_info(request, vuz_id):
    vuz = Vuz.objects.get(pk=vuz_id)
    fields = (
        Training.objects.all().values("fieldid", "fieldname").distinct().order_by("fieldid")
    )
    context = {
        "vuz": vuz,
        "fields": fields,
    }
    return render(request, "vuz/vuz_info.html", context)

def prog(request, vuz_id, year):
    vuz = Vuz.objects.get(pk=vuz_id)
    vuzid = vuz.id

    main_obj = Main.objects.filter(id_vuz=vuzid, year=year).select_related(
        "fieldid", "progid", "id_vuz"
    ).order_by("fieldid", "-formname", "profile")
    fieldname = (
        main_obj.values("fieldid__fieldname").distinct().order_by("fieldid__fieldname")
    )

    fields = (
        Training.objects.all().values("fieldid", "fieldname").distinct().order_by("fieldid")
    )

    formname = main_obj.values("formname").distinct().order_by("-formname")
    prog = main_obj.values("progid__progname").distinct().order_by("progid__progname")
    context = {
        "main_obj": main_obj,
        "fieldname": fieldname,
        "fields": fields,
        "formname": formname,
        "prog": prog,
    }
    return render(request, "vuz/prog.html", context)

from django.db.models.functions import Coalesce

def vuz_profit(request, vuz_id, year):
    # === 1. Получаем параметры сортировки ===
    sort_field = request.GET.get('sort')
    order = request.GET.get('order', 'desc')

    # === 2. Базовые аннотации (как было) ===
    c1 = Coalesce(F('course1'), 0)
    dc1 = Coalesce(F('dcont1'), 0)
    d_val = Coalesce(F('discount__discount'), 0)
    d_dc1 = Coalesce(F('discount__dcont1'), 0)

    output = DecimalField(max_digits=20, decimal_places=2)

    formula_no_discount = ExpressionWrapper(c1 * dc1, output_field=output)
    formula_with_discount = ExpressionWrapper(
        c1 * d_dc1 * (100 - d_val) / 100, 
        output_field=output
    )
    formula_lost_profit = ExpressionWrapper(
        c1 * d_val / 100 * d_dc1, 
        output_field=output
    )

    queryset = Main.objects.filter(
        id_vuz=vuz_id, 
        year=year, 
        course1__isnull=False
    ).select_related("fieldid", "progid", "id_vuz", "discount")

    # === 3. Применяем аннотации ===
    queryset = queryset.annotate(
        sum_no_discount=formula_no_discount,
        sum_with_discount=formula_with_discount,
        lost_profit=formula_lost_profit,
        total_profit=ExpressionWrapper(
            F('sum_no_discount') + F('sum_with_discount'), 
            output_field=output
        ),
        # Для сортировки по названию программы
        fieldname=F('fieldid__fieldname')
    )

    

    # === 4. Сортировка ===
    valid_sort_fields = {
        'id': 'id',
        'fieldname': 'fieldname',
        'fieldid': 'fieldid',
        'course1': 'course1',
        'dcont1': 'dcont1',
        'discount__dcont1': 'discount__dcont1',
        'sum_no_discount': 'sum_no_discount',
        'sum_with_discount': 'sum_with_discount',
        'lost_profit': 'lost_profit',
        'total_profit': 'total_profit',
    }

    if sort_field and sort_field in valid_sort_fields:
        order_by_field = valid_sort_fields[sort_field]
        if order == 'asc':
            queryset = queryset.order_by(order_by_field)
        else:
            queryset = queryset.order_by(F(order_by_field).desc())
    else:
        # Сортировка по умолчанию
        queryset = queryset.order_by('-total_profit')

    main_obj = queryset.values(
        'id', 'id_vuz__name', 'fieldid__fieldname', 'fieldid', 
        'course1', 'dcont1', 
        'discount__dcont1', 'discount__discount',
        'sum_no_discount', 'sum_with_discount', 'total_profit', 'lost_profit'
    )

    # Итоги
    overall_results = main_obj.aggregate(
        total_course1=Coalesce(Sum('course1'), 0, output_field=output),
        total_dcont1=Coalesce(Sum('dcont1'), 0, output_field=output),
        total_discount_dcont1=Coalesce(Sum('discount__dcont1'), 0, output_field=output),
        total_no_discount=Coalesce(Sum('sum_no_discount'), 0, output_field=output),
        total_with_discount=Coalesce(Sum('sum_with_discount'), 0, output_field=output),
        total_profit_all=Coalesce(Sum('total_profit'), 0, output_field=output),
        total_lost_profit=Coalesce(Sum('lost_profit'), 0, output_field=output)
    )

    fields = (
        Training.objects.all().values("fieldid", "fieldname").distinct().order_by("fieldid")
    )

    return render(request, "vuz/vuz_profit.html", {
        "main_obj": main_obj,
        "overall_results": overall_results,
        "current_year": year,
        "vuz_id": vuz_id,
        "fields": fields
    })


def field_stat(request, year):
    field_id = request.GET.get("field_id", '')

    filter_condition = {}

    if field_id:
        field = Training.objects.get(pk=field_id)
        filter_condition['fieldid'] = field_id
    else:
        field = ''
        filter_condition['fieldid'] = "99999"

    main_obj = Main.objects.filter(**filter_condition, year=year).select_related(
        "progid", "id_vuz"
    ).order_by("id_vuz__name")

    fields = (
        Training.objects.all().values("fieldid", "fieldname").distinct().order_by("fieldid")
    )

    formname = main_obj.values("formname").distinct().order_by("-formname")
    vuzname = main_obj.values("id_vuz__name").distinct().order_by("id_vuz__name")
    prog = main_obj.values("progid__progname").distinct().order_by("progid__progname")
    context = {
        "main_obj": main_obj,
        "field": field,
        "fields": fields,
        "formname": formname,
        "vuzname": vuzname,
        "prog": prog,
    }
    return render(request, "vuz/prog_stat.html", context)

def analitic_districts_get(request, year):
    field_id = request.GET.get("field_id", '')

    filter_condition = {}

    if field_id:
        field = Training.objects.get(pk=field_id)
        filter_condition['fieldid'] = field_id
    else:
        field = ''

    main_obj = (
        Main.objects.filter(**filter_condition, year=year)
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
        Main.objects.filter(**filter_condition, year=year)
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

    fields = Training.objects.all().values("fieldname", "fieldid").order_by("fieldid")
    
    context = {
        "fields": fields,
        "field": field,
        "overall_results": overall_results,
        "main_obj": main_obj,
    }
    return render(request, "vuz/analitic_districts.html", context)

def analitic_price(request):
    # 1. Получаем параметры из GET-запроса
    field_id = request.GET.get("field_id")
    district_id = request.GET.get("district_id")
    region_id = request.GET.get("region_id")
    year_from = request.GET.get("year_from")
    year_to = request.GET.get("year_to")

    # 2. Данные для выпадающих списков
    districts = Districts.objects.all().exclude(id_district=9999)
    regions = Regions.objects.all()
    fields = Training.objects.all()

    # 3. Формируем базовый фильтр
    filter_condition = {}
    
    if field_id:
        filter_condition['fieldid'] = field_id
    
    # ВАЖНО: используем __id_district_id, так как фильтруем через связь FK
    if district_id and district_id != '9999':
        filter_condition['id_vuz__id_district_id'] = int(district_id)
        
    if region_id:
        filter_condition['id_vuz__id_region_id'] = int(region_id)

    yearly_stats = []

    # 4. Основной цикл расчетов
    if year_from and year_to:
        y_start = int(year_from)
        y_end = int(year_to)

        for year in range(y_start, y_end + 1):
            current_filter = filter_condition.copy()
            current_filter['year'] = year
            
            # Агрегируем среднюю стоимость
            avg_price = Main.objects.filter(**current_filter).aggregate(Avg('course1'))['course1__avg']
            
            # Текущие данные за год
            current_data = {
                'year': year,
                'price': float(avg_price) if avg_price else 0,
                'diff_price': 0,
                'diff_percent': 0
            }

            # 5. Расчет динамики (сравнение с предыдущим годом в списке)
            if len(yearly_stats) > 0:
                prev_year_data = yearly_stats[-1]
                if current_data['price'] and prev_year_data['price']:
                    diff = current_data['price'] - prev_year_data['price']
                    percent = (diff / prev_year_data['price']) * 100
                    current_data['diff_price'] = diff
                    current_data['diff_percent'] = percent

            yearly_stats.append(current_data)

    # 6. Расчет итоговых показателей за весь период
    overall_stats = None
    if len(yearly_stats) > 1:
        first = yearly_stats[0]
        last = yearly_stats[-1]
        if first['price'] > 0:
            overall_diff = last['price'] - first['price']
            overall_stats = {
                'diff': overall_diff,
                'percent': (overall_diff / first['price']) * 100
            }
    
    # 7. Создание связей
    connections = {}
    valid_combinations = Main.objects.values(
        'fieldid', 
        'id_vuz__id_district_id', 
        'id_vuz__id_region_id'
    ).distinct()

    for item in valid_combinations:
        f_id = str(item['fieldid'])
        d_id = str(item['id_vuz__id_district_id'])
        r_id = str(item['id_vuz__id_region_id'])
        
        if f_id not in connections:
            connections[f_id] = {'districts': set(), 'regions': set()}
        
        connections[f_id]['districts'].add(d_id)
        connections[f_id]['regions'].add(r_id)

    # Преобразуем set в list для JSON
    for f_id in connections:
        connections[f_id]['districts'] = list(connections[f_id]['districts'])
        connections[f_id]['regions'] = list(connections[f_id]['regions'])

    context = {
        'districts': districts,
        'regions': regions,
        'fields': fields,
        'selected_district': district_id,
        'selected_region': region_id,
        'selected_field': field_id,
        'yearly_stats': yearly_stats,
        'overall_stats': overall_stats,
        'connections_json': json.dumps(connections),
    }
    
    return render(request, "vuz/analitic_price.html", context)