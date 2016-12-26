from django.db import models
from django.db.models.aggregates import Max, Min
from django.db.models.base import Model
from django.utils.translation import ugettext_lazy as _


class DownloadLogMixin(object):
    def last_download(self): 
        return self.order_by('-trading_date')[0]
    def first_download(self): 
        return self.order_by('trading_date')[0]
    

class DownloadLogQuerySet(models.QuerySet, DownloadLogMixin):
    pass

class DownloadLogManager(models.Manager, DownloadLogMixin):
    def get_last_download_date(self):
        data = self.all().aggregate(Max('trading_date'))
        return data['trading_date__max']
    def get_first_download_date(self):
        data = self.all().aggregate(Min('trading_date'))
        return data['trading_date__min']
 
class Download_Log(Model):
    trading_date = models.DateField(auto_now_add=False, null=False, unique=True, verbose_name=_('trading_date')) 
    serial_id = models.PositiveIntegerField(null=False, unique=True, verbose_name=_('serial_id'))
     
    objects = DownloadLogManager() 