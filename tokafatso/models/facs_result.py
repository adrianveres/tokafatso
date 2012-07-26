from django.db import models

from tokafatso.models import BaseUUIDModel, Result, ResultItem
from tokafatso.choices import RESULT_VALIDATION_STATUS

class FacsFile(BaseUUIDModel):
    """
    Model for storing information about FACS data files.
    """
    
    original_filename = models.CharField(max_length=200)
    md5hash = models.CharField(max_length=200,verbose_name = 'File Hash')
    archive_filename = models.CharField(max_length=200)

    def __unicode__(self):
        return self.original_filename

    class Meta:
        app_label = 'tokafatso'

class FacsResult(Result):
    """
    Model for storing information about a specific FACS result. 
    It inherits basic behavior from the Result base class.
    Additional fields may be added to store use-specific information.
    """

    origin_facs_file = models.ForeignKey(FacsFile)

    cytometer_serial_number = models.CharField(
        verbose_name = 'Cytometer Serial Number',
        max_length = 100,
        )

    class Meta:
        app_label = 'tokafatso'

