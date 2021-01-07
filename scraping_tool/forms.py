from django import forms
from django.forms import ModelForm
import datetime

from .models import *

class ScheduleForm(ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder':'Event Name?'}
            ),
        required=True
    )
    event_datetime = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={'placeholder':'example: 2021-1-1 12:00'}
        ),
        input_formats=['%Y-%m-%d %H:%M']
        )
    comment = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder':'Add a new comment...'}
            ),
        required=False
        )

    class Meta:
        model = Mail
        fields = ['name', 'event_datetime', 'comment']


class DatetimeForm(forms.Form):
    collect_from = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(2018, datetime.date.today().year+1)
        )
    )
    collect_until = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(2018, datetime.date.today().year+1)
        )
    )
