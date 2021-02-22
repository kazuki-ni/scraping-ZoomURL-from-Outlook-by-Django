from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
import bootstrap_datepicker_plus as datetimepicker
import datetime

from .models import *


class ScheduleForm(ModelForm):

    def clean_name(self):
        name = self.cleaned_data['name']
        if name == "":
            raise ValidationError('Event name is required.')
        return name

    def clean(self):
        cleaned_data = super(ScheduleForm, self).clean()
        event_day = cleaned_data.get('event_day')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if (event_day == "") or (start_time == '') or (end_time == ''):
            raise ValidationError('Please select a datetime.')

    class Meta:
        model = Mail
        fields = [
            'name',
            'event_day',
            'start_time',
            'end_time',
            'comment'
        ]
        labels = {
            'name': 'event name',
            'event_day': 'scheduled time',
            'start_time': 'start time',
            'end_time': 'end time',
            'comment': 'comment'
        }
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Name the event...'
                }
            ),
            'event_day': datetimepicker.DatePickerInput(
                format='%Y-%m-%d',
                options={
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                }
            ),
            'start_time': datetimepicker.TimePickerInput(
                format='%H:%M'
            ).start_of('event'),

            'end_time': datetimepicker.TimePickerInput(
                format='%H:%M'
            ).end_of('event'),
            
            'comment': forms.Textarea(
                attrs={
                    'placeholder': 'memo space...'
                }
            )
        }


class DatetimeForm(forms.Form):
    collect_from = forms.DateField(
        widget=datetimepicker.DatePickerInput(
            format='%Y-%m-%d',
            options={
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        ).start_of('scraping')
    )
    collect_until = forms.DateField(
        widget=datetimepicker.DatePickerInput(
            format='%Y-%m-%d',
            options={
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        ).end_of('scraping')
    )
