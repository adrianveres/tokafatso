from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django_extensions.db.fields import UUIDField

from tokafatso.models import BaseUUIDModel, TestCode, Requisition
from tokafatso.choices import RESULT_QUANTIFIER
from tokafatso.validators import is_result_identifier

# from audit_trail import audit

class Result(BaseUUIDModel):
    """
    Base class for results.
    """

    requisition = models.ForeignKey(
        Requisition,
        null=True,
        blank=True,
        related_name='%(class)s_set',
        )

    result_identifier = models.CharField(
        max_length=25,
        db_index=True,        
        validators = [
            is_result_identifier,
            ]
        )

    result_datetime = models.DateTimeField(
        help_text = 'Date result added to system.',
        db_index=True,        
        )

    result_active = models.BooleanField(
        help_text = 'Set to False to remove result from system without deleting it.',
        default = True,
        )

    def __eq__(self,other):
        """
        Defines equality of two results. 
        This equality is based on comparing the result items associated with the result isinstance.
        """
        if isinstance(other, Result):
            return self.get_resultitem_dict() == other.get_resultitem_dict()
        else:
            print 'no class'
            return False

    def __ne__(self,other):
        return not self.__eq__(other)
    
    def __unicode__(self):
        return '%s' % (self.result_identifier)

    class Meta:
        app_label = 'tokafatso'
        abstract = True
        ordering =['result_identifier','result_datetime',]

    def link_to_requisition(self):
        """
        Find requisition with matching identifier and created within
        a certain time window around the result datetime.
        """

        if not self.requisition:
            requisition = Requisition.objects.filter(sample_identifier = self.result_identifier)
        
            if requisition:
                self.requisition = requisition[0]
                self.save()

                #Trigger requisition update status.
                self.requisition.update_status()

        return self

    def get_resultitem_dict(self):

        if self.id:
            ctype = ContentType.objects.get_for_model(self.__class__)
            return dict([(item.test_code.name, item) for item in ResultItem.objects.filter(result_type__pk = ctype.id,result_id = self.id)])
        else:
            return None

    def delete(self,*args, **kwargs):
        """
        Over-writing delete method so that deleting a Result subclass also removes ResultItems instead of orphaning them.
        """
        for item in self.get_resultitem_dict().values():
            item.delete()
        super(Result, self).delete(*args, **kwargs)

class ResultItem(BaseUUIDModel):
    """
    Base class for result items.
    Stores a specific item from a set of results (such as the CD4 count from a full FACS panel).
    Uses a GenericForeignKey for the 'result' field because we want relationships with abstract base classes.
    A Validator function checks that the result field points to a subclass of 'Result' defined above.
    """

    result_type = models.ForeignKey(ContentType)
    result_id = UUIDField()
    result = generic.GenericForeignKey('result_type','result_id')

    test_code = models.ForeignKey(TestCode)

    result_item_value = models.CharField(
        verbose_name = 'Result',
        max_length = 25,
        help_text = '',
        db_index=True,
        )

    result_item_quantifier = models.CharField(
        verbose_name = 'Quantifier',
        default = '=',
        choices = RESULT_QUANTIFIER,
        max_length = 25,
        help_text = '',
        )
    
    result_item_datetime = models.DateTimeField(
        verbose_name = 'Assay date and time',
        db_index=True,        
        )
    
    error_code = models.CharField(
        verbose_name = 'Error codes',
        max_length = 50,
        null = True,
        blank = True,       
        help_text = ''
        )
        
    def __eq__(self,other):
        """
        Defines equality between different result items.
        Allows for loose equality that accounts for things such as rounding errors.
        Looser equalities are independently defined for specific test codes below.
        """
        if isinstance(other, self.__class__):
            if self.test_code == other.test_code:
                #Implement loose equality for specific test codes
                if self.test_code.code in ['CD4', 'CD4%', 'CD8', 'CD8%']:
                    return abs(int(float(self.result_item_value))-int(float(other.result_item_value))) <= 1
                else:
                    return self.result_item_value == other.result_item_value
            else:
                return False    
        else:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)
        
    def __unicode__(self):
        return '%s: %s' % (unicode(self.test_code.code), unicode(self.result_item_value))
           
    class Meta:
        app_label = 'tokafatso'

    def summary(self):

        return (self.test_code.code, self.result_item_value)
