import datetime
import django.utils.simplejson as json

from django.db import models
from django.template.loader import render_to_string

from tokafatso.models import BaseUUIDModel, Device

class Clinic(BaseUUIDModel):
    """
    Model for storing information about clinics enrolled in study
    """
    
    clinic_code = models.CharField(
        max_length = 20,
        help_text = "Unique identifying code",
        unique = True,
        )
    
    clinic_name = models.CharField(
        max_length = 200,
        help_text = "Full clinic name",
        )

    active = models.BooleanField(
        verbose_name = "Clinic active",
        default = True,
        )

    clinic_printer = models.ForeignKey(
        Device,
        blank=True,
        null=True,
        )

    def __unicode__(self):
        return '%s - %s'%(self.clinic_name, self.clinic_code)

    class Meta:
        app_label = 'tokafatso'

    def get_requisition_timeseries(self):
        if not self.requisition_set.all():
            return None

        clinic_data = []
        date_weekstart = lambda d: (d - datetime.timedelta(d.weekday()))

        first_requisition = self.requisition_set.order_by('created')[0]
        first_monday = date_weekstart(first_requisition.created.date())
        today = datetime.date.today()

        for td in range((first_monday-today).days, 0, 7):

            daterange = (today+datetime.timedelta(td),today+datetime.timedelta(td+6))
            week_data = self.requisition_set.filter(created__range=daterange).aggregate(
                models.Avg('days_from_referral_to_blood_draw'),
                models.Avg('days_from_referral_to_result'),
                models.Avg('days_from_blood_draw_to_requisition'),
                models.Avg('days_from_blood_draw_to_result'),
                models.Avg('days_from_requisition_to_result'),
                models.Avg('days_from_result_to_validation'),
                models.Avg('days_from_validation_to_communication'),
                count=models.Count('id'))
            week_data['startdate'] = daterange[0].isoformat()
            for key, value in week_data.items():
                if value is None:
                    week_data[key] = 0
            clinic_data.append(week_data)

        return clinic_data 

    def received_requisition_counts(self):
        today = datetime.datetime.now().date()
        this_week_range = (today - datetime.timedelta(6), today)
        last_week_range = (today - datetime.timedelta(13), today - datetime.timedelta(7))
        last_12_weeks_range = (today - datetime.timedelta(83), today)

        this_week = self.requisition_set.filter(created__range=this_week_range).count()
        last_week = self.requisition_set.filter(created__range=last_week_range).count()
        last_12_weeks_average = float(self.requisition_set.filter(created__range=last_12_weeks_range).count())/12
        return (round(last_12_weeks_average,2), last_week, this_week)

    def received(self):
        clinic_data = {
            'clinic_id': 'clinic-plot-'+self.id,
            'data': self.received_requisition_counts(),
            }
        content = """<svg id="%s" height="400" width="600"></svg>""" % clinic_data['clinic_id']
        content += """<script type="text/javascript"> plot_clinic_requisition_summary('"""+json.dumps(clinic_data)+"')</script>"
        return content
    received.allow_tags = True

    def clinic_timeseries(self):
        clinic_data = {
            'clinic_id': 'clinic-ts-'+self.id,
            'data': self.get_requisition_timeseries(),
            'data_headers': [
                'days_from_referral_to_result__avg',
                'days_from_result_to_validation__avg',
                'days_from_validation_to_communication__avg',
                ]
            }
        content = """<svg id="%s" height="400" width="600"></svg>""" % clinic_data['clinic_id']
        content += """<script type="text/javascript"> plot_clinic_data_timeseries('"""+json.dumps(clinic_data)+"')</script>"
        return content
    clinic_timeseries.allow_tags = True

    def requisition_timeseries(self):
        clinic_data = {
            'clinic_id': 'clinic-reqs-'+self.id,
            'data': self.get_requisition_timeseries(),
            }
        content = """<svg id="%s" height="400" width="600"></svg>""" % clinic_data['clinic_id']
        content += """<script type="text/javascript"> plot_clinic_requisition_timeseries('"""+json.dumps(clinic_data)+"')</script>"
        return content
    requisition_timeseries.allow_tags = True


    def last_message_confirmed(self):
        if self.clinic_printer:
            if self.clinic_printer.confirmation_queue():
                style = 'color: red; font-weight: bold'
                content = 'NO'
                return '<span style="%s">%s</span>'%(style,content)
            else:
                style = 'color: green; font-weight: bold'
                content = 'YES'
                return '<span style="%s">%s</span>'%(style,content)
        else:
            return 'no printer'
    last_message_confirmed.allow_tags = True