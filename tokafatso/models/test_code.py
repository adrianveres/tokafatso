from django.db import models
from django.core.validators import RegexValidator

from tokafatso.models import BaseUUIDModel
from tokafatso.choices import UNITS, ABS_CALC

class TestCode(BaseUUIDModel):

    code = models.CharField(
        verbose_name = "Test Code", 
        max_length=15, 
        unique=True,
        validators = [
            RegexValidator('^[A-Z0-9\%\_\-]{1,15}$', 'Ensure test code is uppercase alphanumeric ( with _ ,%) and no spaces'),
            ],
        )
        
    name = models.CharField(
        verbose_name = "Test Code Description", 
        max_length=50,
        )

    units = models.CharField(
        verbose_name = 'Units',
        max_length = 25,
        choices = UNITS,
        )
        
    display_decimal_places = models.IntegerField(
        verbose_name = 'Decimal places to display',
        null = True,
        blank = True,        
        )

    is_absolute = models.CharField(
        verbose_name = 'Is the value absolute or calculated?',
        max_length = '15',
        default = 'absolute',
        choices = ABS_CALC,
        )
        
    formula = models.CharField(
        verbose_name = 'If calculated, formula?',
        max_length = '50',
        null = True,
        blank = True,
        )

    def __unicode__(self):
        return self.code

    class Meta:
        app_label = 'tokafatso'

class TestCodeMapping(BaseUUIDModel):

    code = models.ForeignKey(TestCode)

    interface_name = models.CharField(
        verbose_name = 'Interface name',
        max_length = '15',
        )

    code_mapping = models.CharField(
        verbose_name = 'Interface code mapping',
        max_length = '50',
        )

    class Meta:
        app_label = 'tokafatso'



