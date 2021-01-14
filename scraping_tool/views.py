from django.shortcuts import render, redirect
import re

from .models import *
from .forms import *

from.ScrapeZoomURLfromOutlook import *

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
    items = Mail.objects.all()

    if request.method == 'POST':
        items.delete()
        return redirect('/')
     
    context = {}
    return render(request, 'scraping_tool/delete_all.html', context)


def index(request):
    scheduled_items = Mail.objects.filter(is_scheduled=True).order_by('event_datetime')
    unscheduled_items = Mail.objects.filter(is_scheduled=False).order_by('received_time')

    context = {'scheduled_items': scheduled_items, 'unscheduled_items': unscheduled_items}
    return render(request, 'scraping_tool/index.html', context)


def join(request, pk):
    item = Mail.objects.get(id=pk)
    name = item.name
    body_list = item.body.split('|')
    urls = item.url_list.split('|')

    context = {'name': name, 'body_list': body_list, 'urls': urls}
    return render(request, 'scraping_tool/join.html', context)


def update(request, pk):
    item = Mail.objects.get(id=pk)
    body_list = item.body.split('|')
    form = ScheduleForm(instance=item)

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            Mail.objects.filter(id=pk).update(is_scheduled=True)
        return redirect('/')

    context = {'form': form, 'item': item, 'body_list': body_list}
    return render(request, 'scraping_tool/update.html', context)


def delete(request, pk):
    item = Mail.objects.get(id=pk)

    if request.method == 'POST':
        item.delete()
        return redirect('/')

    context = {'item': item}
    return render(request, 'scraping_tool/delete.html', context)

