
from django.db import models
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from tokafatso.choices import ANC_CLINICS, DRAW_LOCATIONS,  REQUISITION_STATUS, HAART_STATUS, POS_NEG_UNKNOWN
from tokafatso.fields import InitialsField, IsDateEstimatedField
from tokafatso.models import BaseUUIDModel, Clinic, KannelServer
from tokafatso.validators import *

class Requisition(BaseUUIDModel):
    """
    Models sample requisition received from clinics.
    """

    requisition_form_number = models.CharField(
        max_length = 20,
        help_text = "Order ID",
        )
    
    requisition_status = models.CharField(
         verbose_name='Status',
         max_length=30,
         choices=REQUISITION_STATUS,
         default='new',
         )
        
    anc_clinic = models.ForeignKey(Clinic)

    # Order Information
    sample_identifier = models.CharField(
        max_length=10,
        verbose_name= 'Sample ID',
        help_text = "Meditech order barcode/number or internal sample identifier.",
        validators = [
        is_result_identifier,
        ],
        )

    # Patient Information
    patient_first_name = models.CharField(
        max_length=50,
        verbose_name = 'Patient first name(s)',
        )

    patient_last_name = models.CharField(
        max_length=50,
        verbose_name = 'Patient surname',
        )

    omang_number = models.CharField(
        max_length=10,
        verbose_name= 'Omang number',
        help_text =  'OMANG or Birth Certificate Number',
        validators = [
            is_omang,
            ],
        )

    dob = models.DateField(
        verbose_name = "Date of birth",
        validators = [
            dob_not_future,
            birthyear_in_range,
            ],
        help_text= "Format is YYYY-MM-DD",
        )

    is_dob_estimated = IsDateEstimatedField( 
        verbose_name= "Is the subject's date of birth estimated?",     
        default='No'  
        )

    # Specimen Information
    blood_drawn_date = models.DateField(
        verbose_name = "Date blood drawn",
        validators = [
            dob_not_future,
            is_within_x_weeks,
            ],
        help_text="Format is YYYY-MM-DD",
        blank = True,
        null = True, 
        )
       
    blood_drawn_time = models.TimeField(
        verbose_name = "Time blood drawn",
        help_text = "Format is HH:MM",
        blank = True,
        null = True, 
        )    

    blood_draw_location = models.CharField(
        max_length = 10,
        choices = DRAW_LOCATIONS,
        default = 'external',
        )

    # Tracing Details
    referral_date = models.DateField(
        verbose_name = "Test referral date",
        help_text= "Format is YYYY-MM-DD or blank (with comment below)",
        validators = [
            date_not_future, 
            ],
        blank = True,
        null = True, 
        )
    
    return_date = models.DateField(
        verbose_name = "Patient return date",
        help_text= "Format is YYYY-MM-DD or blank (with comment below)",
        blank = True,
        null = True, 
        )
    
    confinement_date = models.DateField(
        verbose_name = "Estimated date of confinement",
        help_text= "Format is YYYY-MM-DD or blank (with comment below)",
        validators =[
            is_possible_confinement_date,
            ],
        blank = True,
        null = True, 
        )
        
    art_status = models.CharField(
        max_length = 10,
        choices = HAART_STATUS,
        verbose_name = 'Patient taking HAART?',
        default='no',
        )

    patient_phone_number = models.CharField(
        max_length = 10,
        verbose_name = "Patient phone number",
        blank = True,
        )

    other_phone_number = models.CharField(
        max_length = 10,
        verbose_name = "Other phone number",
        help_text = "Other contact number, if known.",
        blank = True,
        )

    comment = models.TextField(
        verbose_name = "Requisition comments",
        help_text = "Comments required if any field (except other phone number) is left blank.",
        blank = True,
        )

    #System performance fields
    #These values are calculated with the requisition is finalized and used in dashboard.
    days_from_referral_to_blood_draw = models.IntegerField(
        blank = True,
        null = True,
        default = None,
        )

    days_from_referral_to_result = models.IntegerField(
        blank = True,
        null = True, 
        default = None,
        )

    days_from_blood_draw_to_requisition = models.IntegerField(
        blank = True,
        null = True, 
        default = None,
        )

    days_from_blood_draw_to_result = models.IntegerField(
        blank = True,
        null = True, 
        default = None,
        )

    days_from_requisition_to_result = models.IntegerField(
        blank = True,
        null = True, 
        default = None,
        )

    days_from_result_to_validation = models.IntegerField(
        blank = True,
        null = True, 
        default = None,
        )

    days_from_validation_to_communication =models.IntegerField(
        blank = True,
        null = True, 
        default = None,
        )

    class Meta:
        app_label = 'tokafatso'

    class ResultValidationError(Exception):
        """
        Exception raised by Requisition methods involved in result validation.
        """

        def __init__(self, requisition, error):
            self.requisition = requisition
            self.error = error
            requisition.requisition_status = error
            requisition.save()

        def __repr__(self):
            status = dict(REQUISITION_STATUS)[self.error]
            return "Requisition '%s' validation error: %s" % (self.requisition.identifier, status)

    def __unicode__(self):
        return self.sample_identifier

    def clean(self):
        """
        Clean method following the django model definition.
        """

        if not self.comment:
            if Requisition.objects.filter(sample_identifier=self.sample_identifier, omang_number = self.omang_number):
                raise ValidationError('This Requisition was already added. It cannot be added again.')

            if not self.blood_drawn_date:
                raise ValidationError('No Blood Drawn Date and no comment provided. Please add comment or complete the blood drawn date.')

            if not self.blood_drawn_time:
                raise ValidationError('No Blood Drawn Time and no comment provided. Please add comment or complete the blood drawn time.')

            if not self.referral_date:
                raise ValidationError('No Referral Date and no comment provided. Please add comment or complete the referral date.')
            
            if not self.return_date:
                raise ValidationError('No Return Date and no comment provided. Please add comment or complete the return date.')

            if not self.confinement_date:
                raise ValidationError('No Confinement Date and no comment provided. Please add comment or complete the confinement date.')

            if not self.patient_phone_number:
                raise ValidationError('No Patient Phone Number and o comment provided. Please add comment or complete the patient phone number.')

        if self.referral_date:
            if self.dob > self.referral_date:
                raise ValidationError('Date of birth is set after referral date.')

        if self.referral_date and self.return_date:
            if self.referral_date > self.return_date:
                raise ValidationError('Return date is set before referral date.')
        
        if self.referral_date and self.blood_drawn_date:
            if self.referral_date > self.blood_drawn_date:
                raise ValidationError('Blood drawn date is set before referral date.')

        if self.return_date and self.confinement_date:
            if self.return_date > self.confinement_date:
                raise ValidationError('Return date is set after confinement date.')

    def get_confirmation_message(self):
        """
        Returns an IncomingMessage confirming reception of result sent by SMS.
        """
        if self.incomingmessage_set.all():
            return self.incomingmessage_set.order_by('-created')[0]
        else:
            return None

    def get_result(self):
        """
        Returns the result connected to this requisition. 
        """
        facsresult_set = list(self.facsresult_set.filter(result_active=True).order_by('result_datetime'))
        if facsresult_set:
            if len(facsresult_set)>1:
                #Check if all these results are actually duplicates
                if facsresult_set[1:]==facsresult_set[:-1]:
                    return facsresult_set[0]
                else:
                    raise self.ResultValidationError(self, 'multiple_results')
            return facsresult_set[0]
        else:
            return None

    def get_validation(self):
        """
        Returns the result validation connected to this requisition.
        This method is used to prioritized different forms of validations,
        using automatically parsed validations whenever possible.
        """
        manualresult_set = list(self.manualresult_set.filter(result_active=True).order_by('result_datetime'))
        meditechresult_set = list(self.meditechresult_set.filter(result_active=True).order_by('result_datetime'))

        for result_set in [meditechresult_set, manualresult_set]:
            if len(result_set) == 1:
                return result_set[0]
            elif len(result_set) > 1:
                if result_set[1:]==result_set[:-1]:
                    return result_set[0]
                else:
                    raise self.ResultValidationError(self, 'multiple_validation')
        else:
            return None

    def get_requisition_status(self):
        """
        Computes and returns the requisition's present status. 
        It raises ValidateErrors if the status corresponds to an error state.
        """
        if self.requisition_status in ['final']:
            return self.requisition_status

        outgoing_messages = self.outgoingmessage_set.all()
        if outgoing_messages:
            if outgoing_messages.filter(message_confirmed=True):
                return 'final'
            else:
                return 'sent'
        
        result = self.get_result()
        validation = self.get_validation()

        if result and validation:
            if result == validation:
                return 'complete'
            else:        
                raise self.ResultValidationError(self, 'mismatched_validation')
        elif result:
            return 'prelim'
        elif validation:
            return 'waiting'
        else:
            return 'new'

    def update_delay_fields(self):
        """
        Updates the requisition delay fields.
        """

        if self.referral_date and self.blood_drawn_date:
            self.days_from_referral_to_blood_draw = (self.blood_drawn_date-self.referral_date).days

        if self.referral_date and self.get_result():
            self.days_from_referral_to_result = (self.get_result().created.date() - self.referral_date).days

        if self.blood_drawn_date:
            self.days_from_blood_draw_to_requisition = (self.created.date() - self.blood_drawn_date).days

        if self.blood_drawn_date and self.get_result():
            self.days_from_blood_draw_to_result = (self.created.date() - self.get_result().created.date()).days        

        if self.get_result():
            self.days_from_requisition_to_result = (self.get_result().created.date() - self.created.date()).days

        if self.get_result() and self.get_validation():
            self.days_from_result_to_validation = (self.get_validation().created.date() - self.get_result().created.date()).days

        if self.get_validation() and self.get_confirmation_message():
            self.days_from_validation_to_communication = (self.get_confirmation_message().created.date() - self.get_validation().created.date()).days

        self.save()
                    

    def update_status(self):
        """
        Updates the requisition status, handling related exceptions.
        If update leads to complete requisition, sends message.
        """
        try:
            status = self.get_requisition_status()

            #Check if status is different, save if it is.
            if self.requisition_status != status:
                self.requisition_status = status
                self.save()


                #If new status is complete, try to send it out.
                if status == 'complete':
                    self.send_result_text_message()


        except self.ResultValidationError:
            pass

    def get_result_data(self):
        """
        Method for return requisition result data as a dictionnary.
        Wrapper around get_result() and get_validation()
        """
        result_data = {}
        for code, item in self.get_result().get_resultitem_dict().items():
            result_data[code] = item.result_item_value


    def send_result_text_message(self):
        """
        Creates and saves a new message containing the result Information
        """
        context = {'requisition':self, 'result_items':self.get_result().get_resultitem_dict()}

        self.outgoingmessage_set.create(
            message_text = render_to_string('tokafatso/result_text_message.txt', context),
            message_type = 'result',
            sender = KannelServer.objects.get(),
            recipient = self.anc_clinic.clinic_printer,
            )

    def result_CD4(self):
        """
        Method used in Admin Page's listdisplay.
        """
        try:
            if self.get_result():
                if 'CD4_ABS' in self.get_result().get_resultitem_dict():
                    cd4_count = float(self.get_result().get_resultitem_dict()['CD4_ABS'].result_item_value)
                    style = 'color: red; font-weight: bold' if cd4_count<251 else 'color: black'
                    return '<span style="%s">%s</span>'%(style,cd4_count)
                else:
                    return '(no CD4)'
            else:
                return '(none)'
        except self.ResultValidationError:
            return '(error)'
    result_CD4.allow_tags = True

    def validation_CD4(self):
        """
        Method used in Admin Page's listdisplay.
        """
        try:
            if self.get_validation():
                if 'CD4_ABS' in self.get_validation().get_resultitem_dict():
                    try:
                        cd4_count = float(self.get_validation().get_resultitem_dict()['CD4_ABS'].result_item_value)
                        style = 'color: red; font-weight: bold' if cd4_count<251 else 'color: black'
                        return '<span style="%s">%s</span>'%(style,cd4_count)
                    except:
                        return '(%s)'%self.get_validation().get_resultitem_dict()['CD4_ABS']
                else:
                    return '(no CD4)'
            else:
                return '(none)'
        except self.ResultValidationError:
            return '(error)'
    validation_CD4.allow_tags = True

    