from django.db import models

# Create your models here.
class Mail(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name="Event Name",
        null=True
    )    
    received_time = models.DateTimeField(
        verbose_name='Received Time'
        )
    sender = models.CharField(
        max_length=32,
        verbose_name='Sender',
        null=True
        )
    sender_email_address = models.EmailField(
        max_length=254,
        verbose_name="Sender Email Address"
        )
    url_list = models.TextField(
        max_length=1024,
        verbose_name="Zoom URL List"
        )
    body = models.TextField(
        max_length=2048,
        verbose_name='Body',
        null=True
    )
    is_scheduled = models.BooleanField(
        default=False,
        verbose_name='Scheduled'
    )
    event_datetime = models.DateTimeField(
        verbose_name='Date and Time of Event',
        null=True
        )
    comment = models.TextField(
        max_length=256,
        verbose_name='Comment',
        null=True
    )

    def __str__(self):
        if self.is_scheduled == True:
            return self.name
        return self.sender
