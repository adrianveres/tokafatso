from django.utils.timezone import now as datetime_now

from django.forms import ModelForm


from django.contrib import admin

from django.contrib.contenttypes.generic import GenericTabularInline

from tokafatso.models import *

class ResultItemInline(GenericTabularInline):
    
    model = ResultItem
    ct_field = 'result_type'
    ct_fk_field = 'result_id'
    can_delete = False
    extra = 0

class FacsResultAdmin(admin.ModelAdmin):
  
    inlines = [ResultItemInline]
    search_fields = ['result_identifier']

admin.site.register(FacsResult, FacsResultAdmin)

class MeditechResultAdmin(admin.ModelAdmin):
  
    inlines = [ResultItemInline]
    search_fields = ['result_identifier']

admin.site.register(MeditechResult, MeditechResultAdmin)


admin.site.register(TestCode)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_number', 'device_comment', 'is_authorized')
    
admin.site.register(Device, DeviceAdmin)


class OutgoingMessageaAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'created', 'rendered_text', 'message_sent', 'message_confirmed','message_sent_datetime')
    

admin.site.register(OutgoingMessage, OutgoingMessageaAdmin)

class ClinicAdmin(admin.ModelAdmin):

    list_display = ('clinic_code', 'clinic_name', 'last_message_confirmed', 'received')
    list_filter = ['active']

    readonly_fields = ('received', 'clinic_timeseries', 'requisition_timeseries')
    actions = ['restart_blocked_queue']



    def restart_blocked_queue(self, request, queryset):
        started_counter = 0
        no_printer = 0

        for clinic in queryset:
            if clinic.clinic_printer:
                if clinic.clinic_printer.confirmation_queue():
                    message = clinic.clinic_printer.confirmation_queue()[0]
                    message.send()
                else:
                    clinic.clinic_printer.check_queue()
                started_counter += 1
            else:
                no_printer += 1
                

        user_message =  'Restarted text message queues for %s clinic(s). ' % started_counter
        if no_printer:
            user_message += '%s clinic(s) with no registered printer.' % no_printer
        self.message_user(request, user_message)

    class Media:
        css = {
            "all": ("tokafatso/clinic_plots.css",)
        }
        js = ['d3/d3.v2.js', 'tokafatso/test.js', 'tokafatso/clinic_requisition_summary.js']


admin.site.register(Clinic, ClinicAdmin)


class ManualResultItemInline(GenericTabularInline):
    
    model = ResultItem
    ct_field = 'result_type'
    ct_fk_field = 'result_id'
    can_delete = False
    extra = 4
    fields = ['test_code', 'result_item_value']

class ManualResultAdmin(admin.ModelAdmin):
  
    inlines = [ManualResultItemInline]
    fields = ['result_identifier', 'result_datetime', 'manual_result_comment']

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.result_item_datetime = datetime_now()
            instance.save()
        formset.save_m2m()

    def save_model(self, request, result, form, change):
        result.link_to_requisition()
        result.save()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "requisition":
            kwargs["queryset"] = Requisition.objects.filter(requisition_status__in=['prelim', 'new'])
        return super(ManualResultAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ManualResult, ManualResultAdmin)

class RequisitionAdmin(admin.ModelAdmin):

    list_display = ('sample_identifier','anc_clinic','referral_date','blood_drawn_date','requisition_status', 'result_CD4', 'validation_CD4')
    list_filter = ('requisition_status', 'anc_clinic')
    search_fields = ['sample_identifier','patient_first_name','patient_last_name']
    ordering = ['-modified']
    actions = ['resend_text_message', 'send_using_validation']

    fieldsets = (
        ('Requisition information', {
            'fields':('requisition_form_number', 'anc_clinic', 'sample_identifier'),
        }),
        ('Patient information', {
            'fields':('patient_first_name', 'patient_last_name', 'omang_number', 'dob', 'is_dob_estimated', 'blood_drawn_date', 'blood_drawn_time', 'blood_draw_location'),
        }),
        ('Tracing Information', {
            'fields':('referral_date', 'return_date', 'confinement_date', 'art_status', 'patient_phone_number', 'other_phone_number'),
        }),
        ('Comment', {
            'fields':['comment'],
        }),
    )

    def resend_text_message(self, request, queryset):
        sent_counter = 0
        failed_counter = 0
        for requisition in queryset:
            try:
                requisition.send_result_text_message()
                sent_counter += 1
            except:
                failed_counter += 1

        user_message =  '%s result message(s) queued successfully. ' % sent_counter
        if failed_counter:
            user_message += 'Failed to queue %s message(s).' % failed_counter
        self.message_user(request, user_message)

    def send_using_validation(self, request, queryset):
        sent_counter = 0
        failed_counter = 0
        for requisition in queryset:
            try:
                context = {'requisition':requisition, 'result_items':requisition.get_validation().get_resultitem_dict()}
                requisition.outgoingmessage_set.create(
                    message_text = render_to_string('tokafatso/result_text_message.txt', context),
                    message_type = 'result',
                    sender = KannelServer.objects.get(),
                    recipient = requisition.anc_clinic.clinic_printer,
                    )
                sent_counter += 1
            except:
                failed_counter += 1

        user_message =  '%s result message(s) queued successfully using validation information. ' % sent_counter
        if failed_counter:
            user_message += 'Failed to queue %s message(s).' % failed_counter
        self.message_user(request, user_message)



    def save_model(self, request, requisition, form, change):
        requisition.save()

        for resultclass in [FacsResult, MeditechResult, ManualResult]:
            for result in resultclass.objects.filter(result_identifier=requisition.sample_identifier):
                result.link_to_requisition()

admin.site.register(Requisition, RequisitionAdmin)
