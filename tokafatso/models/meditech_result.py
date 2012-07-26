from django.db import models

from tokafatso.models import Result, ResultItem
from tokafatso.choices import RESULT_VALIDATION_STATUS

class MeditechResult(Result):
    """
    Model for storing information about a specific FACS result obtained from MEDITECH.
    This Model is a validation result.
    """
    
    date_of_birth = models.DateField(
        help_text = 'Patient Date of Birth'
        )
    
    u_number = models.CharField(
        max_length=25,
        help_text = 'Patient U Number')

    authorization_name = models.CharField(
        max_length=50,
        verbose_name = 'Authorizing Person',
        blank=True,
        null=True,
        )

    authorization_datetime = models.DateTimeField(
        help_text = 'Date when result was authorized.',
        blank=True,
        null=True,    
        )
    result_datetime_parsed = models.DateTimeField(
        help_text = 'Date result added to system.',
        db_index=True,        
        )

    result_datetime_ordered = models.DateTimeField(
        help_text = 'Date result was ordered.',
        db_index=True,        
        )

    result_datetime_collected = models.DateTimeField(
        help_text = 'Date result was collected.',
        db_index=True,        
        )

    result_datetime_received = models.DateTimeField(
        help_text = 'Date result was received.',
        db_index=True,        
        )

    def authorized_by(self):
        return self.authorization_name

    def authorized_date(self):
        return self.authorization_datetime.date()

    class Meta:
        app_label = 'tokafatso'