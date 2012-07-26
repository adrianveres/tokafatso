from django.db import models

from django_extensions.db.fields import UUIDField
from django_extensions.db.models import TimeStampedModel

class BaseUUIDModel(TimeStampedModel):
    """
    Base model for application.
    Introduces tracking of creation and changes (for users and time).
    Change id to UUID instead of INT.
    """

    id = UUIDField(primary_key=True)

    user_created = models.CharField(max_length=250, verbose_name='user created', editable=False, default="")
    
    user_modified = models.CharField(max_length=250, verbose_name='user modified',editable=False, default="")

    class Meta:
        abstract = True
