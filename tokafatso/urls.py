from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^receive_dlr$', 'tokafatso.views.receive_dlr', name='receive_dlr'),
    url(r'^receive_sms', 'tokafatso.views.receive_text_message', name='receive_text_message'),
    )
