from django.db import models

from tokafatso.models import BaseUUIDModel, Device, KannelServer, Requisition
from tokafatso.choices import MESSAGE_TYPE, MESSAGE_DELIVERY_REPORTS

class TextMessage(BaseUUIDModel):
    """
    Model for storing information about messages sent in study
    """
    message_text = models.TextField()

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE,
        )

    related_requisition = models.ForeignKey(
        Requisition,
        null=True,
        blank=True,
        related_name='%(class)s_set',
        )

    class Meta:
        app_label = 'tokafatso'
        abstract = True

class IncomingMessage(TextMessage):

    sender = models.ForeignKey(
        Device,
        related_name='sms_sent_by_device',
        )

    recipient = models.ForeignKey(
        KannelServer,
        related_name='sms_sent_to_server',
        )

    def is_confirmation_message(self):
        """
        Checks if the message matches what is expected from a confirmation message.
        In the simplest case, it contains a given string.
        Ideally, it would contain some information about the message it is validating.
        """
        return self.message_text == 'OK' and bool(self.sender.clinic_set.all())

    def save(self, *args, **kwargs):
        """
        Overwriting save method to check if the message is a confirmation.
        If so, it uses the sender device's advance_queue method to confirm the last
        sent message and send the next message in queue.
        """

        if not self.id and not self.related_requisition and self.is_confirmation_message:
            
            confirmation_queue = self.sender.confirmation_queue()
            
            if confirmation_queue:
                
                message_to_confirm = confirmation_queue[0]
                message_to_confirm.message_confirmed = True
                message_to_confirm.save()

                self.related_requisition = message_to_confirm.related_requisition

                self.sender.check_queue()

        super(IncomingMessage, self).save(*args, **kwargs)
        self.related_requisition.update_status()

    class Meta:
        app_label = 'tokafatso'


class OutgoingMessage(TextMessage):
    
    sender = models.ForeignKey(
        KannelServer,
        related_name='sms_sent_by_server',
        )

    recipient = models.ForeignKey(
        Device,
        related_name='sms_sent_to_device',
        )

    message_confirmed = models.BooleanField(
        default=False,
        )

    message_sent_datetime = models.DateTimeField(
        null=True,
        blank=True,
        )

    message_sent = models.BooleanField(
        default=False,
        )

    class Meta:
        app_label = 'tokafatso'

    def save(self,*args, **kwargs):
        super(OutgoingMessage, self).save(*args, **kwargs)
        self.recipient.check_queue()

    def send(self):
        """
        Calls the sender's send message method.
        """ 
        #Save the model so it has a primary key.
        if not self.id:
            self.save()

        kannel_response = self.sender.send_message(
            self.recipient.device_number,
            self.id,
            self.message_text,
            )

        #Mark message as sent if kannel responds.
        if kannel_response.getcode() in [200,202]:
            self.message_sent = True
            self.save()

        if self.related_requisition:
            self.related_requisition.update_status()

        return kannel_response.read()

    def rendered_text(self):
        return self.message_text.replace('%%','<br>')
    rendered_text.allow_tags = True



class MessageDeliveryReport(BaseUUIDModel):

    message = models.ForeignKey(OutgoingMessage)

    report = models.CharField(
        max_length=5,
        choices = MESSAGE_DELIVERY_REPORTS,
        )

    class Meta:
        app_label = 'tokafatso'



