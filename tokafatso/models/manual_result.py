from django.db import models

from tokafatso.models import Result, ResultItem
from tokafatso.choices import RESULT_VALIDATION_STATUS

class ManualResult(Result):
    """
    Model for storing information about a specific FACS result that has been keyed in manually.
    This Model is a validation result.
    """

    manual_result_comment = models.TextField(
        verbose_name = 'Manual Result comments',
        help_text = 'Please detail why a manual validation was necessary',
        )

    def __unicode__(self):
        return self.result_identifier

    class Meta:
        app_label = 'tokafatso'
