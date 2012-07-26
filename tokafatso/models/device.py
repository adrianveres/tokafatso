import urllib,urllib2

from django.db import models
from django.core.urlresolvers import reverse

from tokafatso.models import BaseUUIDModel

class Device(BaseUUIDModel):
    """
    Model for storing information about cellular devices used in study.
    Notice that device numbers are required to be unique.
    Abstract class.
    """

    device_name = models.CharField(
        max_length=200,
        )

    device_comment = models.CharField(
        help_text = "Device description and details",
        max_length=500,
        blank=True,
        )

    device_number = models.CharField(
        max_length=15,
        unique = True,
        )

    is_authorized = models.BooleanField(
        default=True,
        )

    def __unicode__(self):
        return '%s' % (self.device_name)

    class Meta:
        app_label = 'tokafatso'

    def confirmation_queue(self):
        """
        Returns messages queued to be sent to this device.
        """
        return self.sms_sent_to_device.filter(message_confirmed=False, message_sent=True).order_by('created')

    def sending_queue(self):
        return self.sms_sent_to_device.filter(message_confirmed=False, message_sent=False).order_by('created')

    def check_queue(self):
        """
        Check if the confirmation queue is empty.
        If it is, send the next message in the sending queue.
        """
        if not self.confirmation_queue():
            if self.sending_queue():
                self.sending_queue()[0].send()

class KannelServer(Device):

    kannel_username = models.CharField(
        max_length=50,
        )

    kannel_password = models.CharField(
        max_length=50,
        )

    kannel_send_url = models.URLField()

    def send_message(self, recipient_number, message_id, message_text):

        message_data = urllib.urlencode({
            'username':self.kannel_username,
            'password':self.kannel_password,
            'to':recipient_number,
            'text':message_text,
            # 'dlr-url':reverse('receive_dlr')+'?report=%d&'+urllib.urlencode({'msgid':message_id}),
            # 'dlr-mask':31,
        })

        return urllib2.urlopen(self.kannel_send_url+'?'+message_data)

    class Meta:
        app_label = 'tokafatso'
