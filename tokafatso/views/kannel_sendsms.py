from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

from tokafatso.models import Device, KannelServer, OutgoingMessage, IncomingMessage, MessageDeliveryReport

@csrf_exempt
def receive_dlr(request):
    """
    Simple view for receiving a message delivery report from a kannel server.
    The DLR url must be included in messages when to Django.
    """

    msgid = request.GET['msgid']
    report = request.GET['report']

    dlr = MessageDeliveryReport(
            message= OutgoingMessage.objects.get(pk=msgid),
            report=report)
    dlr.save()

    return HttpResponse('')

@csrf_exempt
def receive_text_message(request):
    """
    Simple view for receiving a text message from a kannel server.
    """
    device_number = request.GET['phone']
    text = request.GET['text']

    #Try to find device matching number
    sender_device, device_created = Device.objects.get_or_create(device_number=device_number)

    #If device is unknown, add an unathorized device to the system.
    #Alternatively, this could block the sender.
    if device_created:
        sender_device.device_name = 'Unknown Device'
        sender_device.comment = 'Automatically added at message reception.'
        sender_device.authorized = False
        sender_device.save()

    recipient_device = KannelServer.objects.all()[0]

    new_message = IncomingMessage(
        sender = sender_device,
        recipient = recipient_device,
        message_type = 'received' if not device_created else 'unauth',
        message_text = text)
    new_message.save()

    return HttpResponse('')
