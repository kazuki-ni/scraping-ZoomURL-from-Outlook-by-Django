from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import *
from .forms import *

from.ScrapeZoomURLfromOutlook import scrape
from.scrape_from_json import scrape_sample_data


# Create your views here.
def scrape_URLs(request):
    form = DatetimeForm()

    if request.method == 'POST':
        form = DatetimeForm(request.POST)
        if form.is_valid():
            collect_from = form.cleaned_data["collect_from"]
            collect_until = form.cleaned_data["collect_until"]
            scrape(collect_from, collect_until)
            return redirect('/')

    context = {"form": form}
    return render(request, 'scraping_tool/scrape_URLs.html', context)


def delete_all(request):
    if request.method == 'GET':
        items = Mail.objects.all()
        items.delete()
        return HttpResponse('Resetting Successful')


def index(request):
    scheduled_items = Mail.objects.filter(is_scheduled=True).order_by('event_day', 'start_time')
    unscheduled_items = Mail.objects.filter(is_scheduled=False).order_by('received_time')

    context = {'scheduled_items': scheduled_items, 'unscheduled_items': unscheduled_items}
    return render(request, 'scraping_tool/index.html', context)


def join(request, pk):
    item = Mail.objects.get(id=pk)
    body_list = item.body.split('|')
    urls = item.url_list.split('|')

    context = {'item': item, 'body_list': body_list, 'urls': urls}
    return render(request, 'scraping_tool/join.html', context)


def update(request, pk):
    item = Mail.objects.get(id=pk)
    body_list = item.body.split('|')
    form = ScheduleForm(instance=item)
    message = ''

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            Mail.objects.filter(id=pk).update(is_scheduled=True)
            return redirect('/')
        else:
            message = 'Form submission fails'

    context = {'form': form, 'item': item, 'body_list': body_list, 'message': message}
    return render(request, 'scraping_tool/update.html', context)


def delete(request, pk):

    if request.method == 'GET':
        item = Mail.objects.get(id=pk)
        item_id = 'mail-{}'.format(pk)
        item.delete()
        return HttpResponse(item_id)


# Scrape sample data set
def scrape_sample_URLs(request):

    scrape_sample_data()
    return redirect('/')
