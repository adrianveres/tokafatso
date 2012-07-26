"""
Erik's additional model fields
"""
import sys, socket, re
from django.utils.translation import ugettext_lazy as _
from django.db.models import CharField, DateTimeField, DecimalField
from django.forms import RegexField
from django_extensions.db.fields import UUIDField
# from south.modelsinspector import add_introspection_rules

from tokafatso.choices import DATE_ESTIMATED

# class MyUUIDField (UUIDField):
#     """
#     http://code.djangoproject.com/ticket/12235
#     subclassed to avoid MultiValueDictKeyError when editing Inline objects
#     """

#     description = _("Custom Uuid field")

#     def contribute_to_class(self, cls, name):
#         if self.primary_key == True: 
#             assert not cls._meta.has_auto_field, "A model can't have more than one AutoField: %s %s %s; have %s" % (self,cls,name,cls._meta.auto_field)
#             super(MyUUIDField, self).contribute_to_class(cls, name)
#             cls._meta.has_auto_field = True
#             cls._meta.auto_field = self
#         else:
#             super(MyUUIDField, self).contribute_to_class(cls, name)


# class HostnameCreationField (CharField):  
#     """ 
#     HostnameCreationField

#     By default, sets editable=False, blank=True, default=socket.gethostname()
    
#     Created by Erik Widenfelt   
#     """

#     description = _("Custom field for hostname created")

#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('editable', False)
#         kwargs.setdefault('blank', True)
#         kwargs.setdefault('max_length', 50)
#         kwargs.setdefault('verbose_name', 'Hostname')
#         kwargs.setdefault('default', socket.gethostname())
#         CharField.__init__(self, *args, **kwargs)


#     def get_internal_type(self):
#         return "CharField"
  
#     def south_field_triple(self):
#         "Returns a suitable description of this field for South."
#         # We'll just introspect ourselves, since we inherit.
#         from south.modelsinspector import introspector
#         field_class = "django.db.models.fields.CharField"
#         args, kwargs = introspector(self)
#         return (field_class, args, kwargs)

# class HostnameModificationField (CharField):  
#     """ 
#     HostnameModificationField

#     By default, sets editable=False, blank=True, default=socket.gethostname()
    
#     Sets value to socket.gethostname() on each save of the model.

#     Created by Erik Widenfelt   
#     """

#     description = _("Custom field for hostname modified")
    
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('editable', False)
#         kwargs.setdefault('blank', True)
#         kwargs.setdefault('max_length', 50)
#         kwargs.setdefault('verbose_name', 'Hostname')
#         kwargs.setdefault('default', socket.gethostname())
#         CharField.__init__(self, *args, **kwargs)

#     def pre_save(self, model, add):
#         value = socket.gethostname()
#         setattr(model, self.attname, value)
#         return value

#     def get_internal_type(self):
#         return "CharField"
  
#     def south_field_triple(self):
#         "Returns a suitable description of this field for South."
#         # We'll just introspect ourselves, since we inherit.
#         from south.modelsinspector import introspector
#         field_class = "django.db.models.fields.CharField"
#         args, kwargs = introspector(self)
#         return (field_class, args, kwargs)
        
class DobField(DateTimeField):
    """
    Created by Erik Widenfelt
    """

    description = _("Custom field for date of birth")
            
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', _('Date of Birth'))
        kwargs.setdefault('editable', True)
        kwargs.setdefault('help_text', _('Format is YYYY-MM-DD'))
        #self.validators.append(datetime_is_not_future)
        DateTimeField.__init__(self, *args, **kwargs)
    
    def get_internal_type(self):
        return "DateTimeField"
  
    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.DateTimeField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

class IsDateEstimatedField(CharField):
    """
    Created by Erik Widenfelt
    """

    description = _("Custom field to question if date is estimated")
            
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', True)
        kwargs.setdefault('max_length', 25)        
        kwargs.setdefault('choices', DATE_ESTIMATED)
        kwargs.setdefault('help_text', _('If the exact date is not known, please indicate which part of the date is estimated.'))
        CharField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "CharField"
  
    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

class InitialsField(CharField):
    """
    Created by Erik Widenfelt
    """
   
    description = _("Custom field for a person\'s initials")
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', True)
        kwargs.setdefault('verbose_name', _('Initials'))
        kwargs.setdefault('max_length',3)
        #kwargs.setdefault('unique',True)                        
        kwargs.setdefault('help_text', _('Type 2-3 letters, all in uppercase and no spaces'))
        CharField.__init__(self, *args, **kwargs)
    
    def get_internal_type(self):
        return "CharField"
    
    def formfield(self, **kwargs):
        defaults = {
            'form_class': RegexField,
            'regex': re.compile("^[A-Z]{2,3}$"),
            'max_length': self.max_length,
            'error_messages': {
                'invalid': _(u'Enter valid initials. Must be 2-3 letters, all in uppercase and no spaces.'),
            }
        }
        defaults.update(kwargs)
        return super(InitialsField, self).formfield(**defaults)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

