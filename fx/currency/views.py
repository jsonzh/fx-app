from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader

from .models import Bank,Currency,Rate
from django.utils import timezone
from django.template.defaulttags import register

import time,datetime
from dateutil.relativedelta import relativedelta
import json



def index(request):
    template = loader.get_template('currency/index.html')
    currency = Currency.objects.all()
    crc_dict = {}
    for c in currency:
    	crc_dict[c.code] = c.name
    latest_rate = Rate.objects.raw(
    	'''SELECT * FROM currency_rate
    	INNER JOIN
    	    (SELECT currency_id,Max(time) AS ltime
    	    FROM currency_rate 
    	    WHERE bank_id = '004'
    	    GROUP BY currency_id) clate 
        ON (currency_rate.currency_id = clate.currency_id AND currency_rate.time = clate.ltime)
        ORDER BY currency_rate.currency_id
    	''')
    if len(list(latest_rate))!=0:
        latest_time = timezone.localtime(latest_rate[0].time).strftime('%Y-%m-%d %H:%M')
    else:
        latest_time='-'
    print(latest_time)
    context = {'latest_rate':latest_rate,'crc_dict':crc_dict,'latest_time':latest_time}
    return HttpResponse(template.render(context, request))

def rates(request):
    template = loader.get_template('currency/rate.html')
    today = datetime.datetime.now()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    start_date = lastMonth.replace(day=1,hour=0, minute=0, second=0, microsecond=0)
    start_date_str = start_date.strftime('%Y-%m-%d')
    print(start_date)

    currency = Currency.objects.all()
    crc_dict = {}
    for c in currency:
    	crc_dict[c.code] = c.name
    top_c = currency[0]
    top_c_code = top_c.code
    # top_month_rates = Rate.objects.filter(currency_id=top_c.code,time__gt=start_date).order_by('time')
    sql = '''SELECT * FROM currency_rate 
        WHERE  bank_id = '004' AND currency_id = '{}' 
        AND time in (
            SELECT Max(time) AS ltime
            FROM currency_rate 
            WHERE bank_id = '004' AND currency_id = '{}'
            GROUP BY Date(time)
        )
        AND time >= '{}'
        ORDER BY time DESC'''.format(top_c_code,top_c_code,start_date_str)
    top_month_rates = Rate.objects.raw(sql)
    # print(sql)
    # for r in top_month_rates:
    # 	print(r.time)

    labels_lst = []
    cash_b_rates_lst = []
    cash_s_rates_lst = []
    spot_b_rates_lst = []
    spot_s_rates_lst = []
    for r in top_month_rates:
    	time_str = timezone.localtime(r.time).strftime('%m/%d')
    	labels_lst.insert(0,time_str)
    	cash_b_rates_lst.insert(0,r.cash_buying)
    	cash_s_rates_lst.insert(0,r.cash_selling)
    	spot_b_rates_lst.insert(0,r.spot_buying)
    	spot_s_rates_lst.insert(0,r.spot_selling)
    json_dict = {}
    json_dict['currency'] = top_c_code
    json_dict['labels'] = labels_lst
    json_dict['cash_buying'] = cash_b_rates_lst
    json_dict['cash_selling'] = cash_s_rates_lst
    json_dict['spot_buying'] = spot_b_rates_lst
    json_dict['spot_selling'] = spot_s_rates_lst
    json_str = json.dumps(json_dict)
    context = {'top_month_rates':top_month_rates,'crc_dict':crc_dict,'currency':currency,'chart_data':json_str}
    return HttpResponse(template.render(context, request))

def rates_json(request,currency,period):
    json_dict = {}
    labels_lst = []
    cash_b_rates_lst = []
    cash_s_rates_lst = []
    spot_b_rates_lst = []
    spot_s_rates_lst = []
    table = []
    c_name = Currency.objects.get(code=currency).name
    if period is "1":
        latested_rate = Rate.objects.filter(currency_id=currency).order_by('-time')[0]
        date_str = timezone.localtime(latested_rate.time).strftime('%Y-%m-%d')
        title = u'{}近一日匯率({})'.format(currency,date_str)
        rates = Rate.objects.filter(currency_id=currency,time__date=date_str).order_by('-time')
        

        for r in rates:
            time_str = timezone.localtime(r.time).strftime('%H:%M')
            time_tb_str = timezone.localtime(r.time).strftime('%Y-%m-%d %H:%M:%S')
            labels_lst.insert(0,time_str)
            cash_b_rates_lst.insert(0,r.cash_buying)
            cash_s_rates_lst.insert(0,r.cash_selling)
            spot_b_rates_lst.insert(0,r.spot_buying)
            spot_s_rates_lst.insert(0,r.spot_selling)
            row = {}
            row['time'] = time_tb_str
            row['currency'] = u'{}({})'.format(c_name,currency)
            row['cash_buying'] = r.cash_buying
            row['cash_selling'] = r.cash_selling
            row['spot_buying'] = r.spot_buying
            row['spot_selling'] = r.spot_selling
            table.append(row)
        json_dict['currency'] = currency
        json_dict['title'] = title
        json_dict['labels'] = labels_lst
        json_dict['cash_buying'] = cash_b_rates_lst
        json_dict['cash_selling'] = cash_s_rates_lst
        json_dict['spot_buying'] = spot_b_rates_lst
        json_dict['spot_selling'] = spot_s_rates_lst
        json_dict['table'] = table
        return JsonResponse(json_dict)

    elif period is "2":
        title = u'{}近一個月匯率'.format(currency)
        today = datetime.datetime.now()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        start_date = lastMonth.replace(day=1,hour=0, minute=0, second=0, microsecond=0)
        start_date_str = start_date.strftime('%Y-%m-%d')
        print(start_date_str)
        sql = '''SELECT * FROM currency_rate 
        WHERE  bank_id = '004' AND currency_id = '{}' 
        AND time in (
            SELECT Max(time) AS ltime
            FROM currency_rate 
            WHERE bank_id = '004' AND currency_id = '{}'
            GROUP BY Date(time)
        )
        AND time >= '{}'
        ORDER BY time DESC'''.format(currency,currency,start_date_str)
        rates = Rate.objects.raw(sql)
        for r in rates:
            time_str = timezone.localtime(r.time).strftime('%m/%d')
            time_tb_str = timezone.localtime(r.time).strftime('%Y-%m-%d')
            labels_lst.insert(0,time_str)
            cash_b_rates_lst.insert(0,r.cash_buying)
            cash_s_rates_lst.insert(0,r.cash_selling)
            spot_b_rates_lst.insert(0,r.spot_buying)
            spot_s_rates_lst.insert(0,r.spot_selling)
            row = {}
            row['time'] = time_tb_str
            row['currency'] = u'{}({})'.format(c_name,currency)
            row['cash_buying'] = r.cash_buying
            row['cash_selling'] = r.cash_selling
            row['spot_buying'] = r.spot_buying
            row['spot_selling'] = r.spot_selling
            table.append(row)
        json_dict['currency'] = currency
        json_dict['title'] = title
        json_dict['labels'] = labels_lst
        json_dict['cash_buying'] = cash_b_rates_lst
        json_dict['cash_selling'] = cash_s_rates_lst
        json_dict['spot_buying'] = spot_b_rates_lst
        json_dict['spot_selling'] = spot_s_rates_lst
        json_dict['table'] = table
        return JsonResponse(json_dict)

    elif period is "3":
        title = u'{}近三個月匯率'.format(currency)
        today = datetime.datetime.now()
        start_date = datetime.date.today() + relativedelta(months=-3)
        start_date = start_date.replace(day=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        print(start_date_str)
        sql = '''SELECT * FROM currency_rate 
        WHERE  bank_id = '004' AND currency_id = '{}' 
        AND time in (
            SELECT Max(time) AS ltime
            FROM currency_rate 
            WHERE bank_id = '004' AND currency_id = '{}'
            GROUP BY Date(time)
        )
        AND time >= '{}'
        ORDER BY time DESC'''.format(currency,currency,start_date_str)
        rates = Rate.objects.raw(sql)
        for r in rates:
            time_str = timezone.localtime(r.time).strftime('%m/%d')
            time_tb_str = timezone.localtime(r.time).strftime('%Y-%m-%d')
            labels_lst.insert(0,time_str)
            cash_b_rates_lst.insert(0,r.cash_buying)
            cash_s_rates_lst.insert(0,r.cash_selling)
            spot_b_rates_lst.insert(0,r.spot_buying)
            spot_s_rates_lst.insert(0,r.spot_selling)
            row = {}
            row['time'] = time_tb_str
            row['currency'] = u'{}({})'.format(c_name,currency)
            row['cash_buying'] = r.cash_buying
            row['cash_selling'] = r.cash_selling
            row['spot_buying'] = r.spot_buying
            row['spot_selling'] = r.spot_selling
            table.append(row)
        json_dict['currency'] = currency
        json_dict['title'] = title
        json_dict['labels'] = labels_lst
        json_dict['cash_buying'] = cash_b_rates_lst
        json_dict['cash_selling'] = cash_s_rates_lst
        json_dict['spot_buying'] = spot_b_rates_lst
        json_dict['spot_selling'] = spot_s_rates_lst
        json_dict['table'] = table
        return JsonResponse(json_dict)

    elif period is "4":
        title = u'{}近六個月匯率'.format(currency)
        today = datetime.datetime.now()
        start_date = datetime.date.today() + relativedelta(months=-6)
        start_date = start_date.replace(day=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        print(start_date_str)
        sql = '''SELECT * FROM currency_rate 
        WHERE  bank_id = '004' AND currency_id = '{}' 
        AND time in (
            SELECT Max(time) AS ltime
            FROM currency_rate 
            WHERE bank_id = '004' AND currency_id = '{}'
            GROUP BY Date(time)
        )
        AND time >= '{}'
        ORDER BY time DESC'''.format(currency,currency,start_date_str)
        rates = Rate.objects.raw(sql)
        for r in rates:
            time_str = timezone.localtime(r.time).strftime('%m/%d')
            time_tb_str = timezone.localtime(r.time).strftime('%Y-%m-%d')
            labels_lst.insert(0,time_str)
            cash_b_rates_lst.insert(0,r.cash_buying)
            cash_s_rates_lst.insert(0,r.cash_selling)
            spot_b_rates_lst.insert(0,r.spot_buying)
            spot_s_rates_lst.insert(0,r.spot_selling)
            row = {}
            row['time'] = time_tb_str
            row['currency'] = u'{}({})'.format(c_name,currency)
            row['cash_buying'] = r.cash_buying
            row['cash_selling'] = r.cash_selling
            row['spot_buying'] = r.spot_buying
            row['spot_selling'] = r.spot_selling
            table.append(row)
        json_dict['currency'] = currency
        json_dict['title'] = title
        json_dict['labels'] = labels_lst
        json_dict['cash_buying'] = cash_b_rates_lst
        json_dict['cash_selling'] = cash_s_rates_lst
        json_dict['spot_buying'] = spot_b_rates_lst
        json_dict['spot_selling'] = spot_s_rates_lst
        json_dict['table'] = table
        return JsonResponse(json_dict)

    elif period is "5":
        title = u'{}近一年匯率'.format(currency)
        today = datetime.datetime.now()
        start_date = datetime.date.today() + relativedelta(years=-1)
        start_date = start_date.replace(day=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        print(start_date_str)
        sql = '''SELECT * FROM currency_rate 
        WHERE  bank_id = '004' AND currency_id = '{}' 
        AND time in (
            SELECT Max(time) AS ltime
            FROM currency_rate 
            WHERE bank_id = '004' AND currency_id = '{}'
            GROUP BY Date(time)
        )
        AND time >= '{}'
        ORDER BY time DESC'''.format(currency,currency,start_date_str)
        rates = Rate.objects.raw(sql)
        for r in rates:
            time_str = timezone.localtime(r.time).strftime('%m/%d')
            time_tb_str = timezone.localtime(r.time).strftime('%Y-%m-%d')
            labels_lst.insert(0,time_str)
            cash_b_rates_lst.insert(0,r.cash_buying)
            cash_s_rates_lst.insert(0,r.cash_selling)
            spot_b_rates_lst.insert(0,r.spot_buying)
            spot_s_rates_lst.insert(0,r.spot_selling)
            row = {}
            row['time'] = time_tb_str
            row['currency'] = u'{}({})'.format(c_name,currency)
            row['cash_buying'] = r.cash_buying
            row['cash_selling'] = r.cash_selling
            row['spot_buying'] = r.spot_buying
            row['spot_selling'] = r.spot_selling
            table.append(row)
        json_dict['currency'] = currency
        json_dict['title'] = title
        json_dict['labels'] = labels_lst
        json_dict['cash_buying'] = cash_b_rates_lst
        json_dict['cash_selling'] = cash_s_rates_lst
        json_dict['spot_buying'] = spot_b_rates_lst
        json_dict['spot_selling'] = spot_s_rates_lst
        json_dict['table'] = table
        return JsonResponse(json_dict)
    return JsonResponse(json_dict)
    

@register.filter
def get_locale_time(obj):
    return timezone.localtime(obj.time).strftime('%Y-%m-%d %H:%M:%S')

@register.filter
def get_locale_date(obj):
    return timezone.localtime(obj.time).strftime('%Y-%m-%d')
