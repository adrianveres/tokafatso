from django.core.exceptions import ValidationError
import re
import datetime

def is_meditech_order(order):
    order_def = r'[0-9]{6}'
    if not re.match(order_def, order) or len(order)!=6:
        #mop
        raise ValidationError(u'Invalid Meditech order number. You entered %s.' % order)

def is_omang(omang):

    omang_def = r'[0-9]{9}'
    if not re.match(omang_def, omang) or len(omang)!=9:
        raise ValidationError(u'Invalid Omang number. You entered %s.' % omang)


def birthyear_in_range(dob):

    now = datetime.datetime.now()
    if dob.year > now.year-10:
        raise ValidationError(u'Invalid date of birth. Date of birth is less than 10 years ago. You entered %s.' % dob)

    if dob.year < now.year-60:
        raise ValidationError(u'Invalid date of birth. Date of birth is more than 60 years ago. You entered %s.' % dob)


def is_within_x_weeks(date):

    now = datetime.datetime.now().date()

    date_diff = now-date
    if date_diff.days>60:
        raise ValidationError(u'Invalid date. Date is more than 3 weeks ago. You entered %s.' % date)

def is_possible_confinement_date(date):

    now = datetime.datetime.now().date()

    date_diff = now-date
    if date_diff.days<-40*7:
        raise ValidationError(u'Invalid confinement date (EDC). Date is more than 40 weeks ago. You entered %s.' % date)

def is_result_identifier(order):

    error_message = u'Invalid Meditech order number. You entered %s. Format should be 6 digits (123456) for Meditech orders or 2 letters, 5 digits (AA12345) for lab data.'% order

    meditech_def = r'[0-9]{6}'
    bhp_def = r'[a-zA-Z]{2}[0-9]{5}'
        
    if not re.match(bhp_def, order) or len(order)!=7:
        if not re.match(meditech_def, order) or len(order)!=6:
            raise ValidationError(error_message)        

def is_lab_result_identifier(order):

    order_def = r'[a-zA-Z]{2}[0-9]{5}'
    mis_def = r'[0-9]{6}'

    if not re.match(order_def, order) or len(order)!=7:
        
        if re.match(mis_def, order) and len(order)==6:
            ValidationError(u'Invalid Laboratory order number. You entered %s. This seems to be a Meditech order. Results with Meditech orders cannot be validated manually'% order)            


        raise ValidationError(u'Invalid Laboratory order number. You entered %s. Format must be 2 letters, 5 digits (AA12345)'% order)

def dob_not_future(value):
    now = datetime.datetime.now().date()
    if now < value :
        raise ValidationError(u'Date of birth cannot be a future date. You entered %s.' % value)

def dob_not_today(value):
    now = datetime.datetime.now().date()
    if now == value :
        raise ValidationError(u'Date of birth cannot be today. You entered %s.' % value)

def date_not_future(value):
    now = datetime.datetime.now().date()
    if value > now:
        raise ValidationError(u'Date cannot be a future date. You entered %s' % (value,))
