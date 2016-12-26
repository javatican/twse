
import datetime
import re

from django.db import models 
from django.utils.translation import ugettext_lazy as _ 

    
class Trans_Data(models.Model):
    CALL = '1'
    PUT = '2' 
    CLASSIFICATION_CHOICES = (
        (CALL, 'C'),
        (PUT, 'P'),)    
    trans_date = models.DateField('trans_date')
    strike_price = models.PositiveIntegerField(default=0, verbose_name=_('strike_price'))
    expiration_date = models.CharField(default='', max_length=8, verbose_name=_('expiration_date')) 
    classification = models.CharField(max_length=1, default=1, choices=CLASSIFICATION_CHOICES, verbose_name=_('classification'))
    trans_time = models.TimeField(verbose_name=_('trans_time'))       
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('price'))
    volume = models.PositiveIntegerField(default=0, verbose_name=_('volume')) 
    
    def is_call(self):
        return self.classification == self.CALL
    def is_put(self):
        return self.classification == self.PUT
    def set_classification(self, classification):
        for a,b in self.CLASSIFICATION_CHOICES:
            if(classification==b):
                self.classification=a
    
    def set_trans_date(self, trans_date):
        m = re.match(r"(^\d{4})(\d{2})(\d{2}$)",trans_date)
        self.trans_date = datetime.date(m.group(1),m.group(2),m.group(3))
    def set_trans_time(self, trans_time):
        m = re.match(r"(^\d+?)(\d{2})(\d{2}$)",trans_time)
        self.trans_time = datetime.time(m.group(1),m.group(2),m.group(3))
        
    
        
        