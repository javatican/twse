 

from django.db import models
from django.db.models.aggregates import Max
from django.db.models.base import Model 
from django.utils.translation import ugettext_lazy as _

from matplotlib.dates import date2num

    
class Cron_Job_Log(Model):
    STATUS_CHOICES = (
        ('1', _('cron_job_success')),
        ('2', _('cron_job_failed')),)
    title = models.CharField(max_length=48, default='', verbose_name=_('cron_job_title'))
    exec_time = models.DateTimeField(auto_now_add=True, verbose_name=_('cron_job_exec_time'))       
    status_code = models.CharField(default='1', max_length=1, choices=STATUS_CHOICES, verbose_name=_('cron_job_status'))
    error_message = models.CharField(max_length=120, default='', verbose_name=_('cron_job_error_message'))
    
    def success(self):
        self.status_code = '1'
    def failed(self):
        self.status_code = '2'
        
class TwseIndexStatsMixin(object):
    def between_dates(self, start_date, end_date):
        return self.filter(trading_date__gte=start_date, trading_date__lte=start_date)
    def lte_date(self, target_date):
        return self.filter(trading_date__lte=target_date)
    def get_missing_avg(self):
        return self.filter(week_avg__isnull=True)
    
class TwseIndexStatsQuerySet(models.QuerySet, TwseIndexStatsMixin):
    pass

class TwseIndexStatsManager(models.Manager, TwseIndexStatsMixin):
    def get_queryset(self):
        return TwseIndexStatsQuerySet(self.model, using=self._db)
    def by_date(self, trading_date):
        return self.get(trading_date=trading_date)
    def ohlc_between_dates(self, start_date, end_date, date_as_num=False):
        # return list of tuples containing d, open, high, low, close, volume
        entries = self.filter(trading_date__gte=start_date, trading_date__lte=end_date)
        if date_as_num:
            result = [(date2num(entry.trading_date),
                   float(entry.opening_price),
                   float(entry.highest_price),
                   float(entry.lowest_price),
                   float(entry.closing_price),
                   float(entry.trade_value)) for entry in entries]
        else:
            result = [(entry.trading_date,
                   float(entry.opening_price),
                   float(entry.highest_price),
                   float(entry.lowest_price),
                   float(entry.closing_price),
                   float(entry.trade_value)) for entry in entries]
        return result
    
#     def get_dates_for_missing_avg(self):
#         return self.filter(week_avg__isnull=True).values_list('trading_date', flat=True)
    def price_value_lte_date(self, target_date):
        return self.lte_date(target_date).values_list('closing_price', 'trade_value')
    
class Twse_Index_Stats(Model):
    trading_date = models.DateField(auto_now_add=False, null=False, unique=True, verbose_name=_('trading_date')) 
#
    trade_volume = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_volume')) 
    trade_transaction = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_transaction')) 
    trade_value = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name=_('trade_value')) 
    opening_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('opening_price'))
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('highest_price'))
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('lowest_price'))
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('closing_price'))
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price_change'))
#
    week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('week_avg'))
    two_week_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('two_week_avg'))
    month_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('month_avg'))
    quarter_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('quarter_avg'))
    half_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('half_avg'))
    year_avg = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name=_('year_avg'))
    day_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('day_k'))
    day_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('day_d'))
    week_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('week_k'))
    week_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('week_d'))
    month_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('month_k'))
    month_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_('month_d'))                                 
    year_value_avg = models.DecimalField(max_digits=15, decimal_places=0, null=True, verbose_name=_('year_value_avg'))
    
    objects = TwseIndexStatsManager()  
    
    
class TradingDateMixin(object):
    def since_which_date(self, qdate): 
        return self.filter(trading_date__gte=qdate)
    def between_dates(self, start_date, end_date): 
        return self.filter(trading_date__gte=start_date, trading_date__lte=end_date)
    

class TradingDateQuerySet(models.QuerySet, TradingDateMixin):
    pass

class TradingDateManager(models.Manager, TradingDateMixin):
    def get_last_trading_date(self):
        data = self.all().aggregate(Max('trading_date'))
        return data['trading_date__max']

class Trading_Date(Model):
    trading_date = models.DateField(auto_now_add=False, null=False, unique=True, verbose_name=_('trading_date')) 
    day_of_week = models.PositiveIntegerField(default=9, verbose_name=_('day_of_week'))
    is_future_delivery_day = models.BooleanField(default=False, verbose_name=_('is_future_delivery_day')) 
    first_trading_day_of_month = models.BooleanField(default=False, verbose_name=_('first_trading_day_of_month')) 
    last_trading_day_of_month = models.BooleanField(default=False, verbose_name=_('last_trading_day_of_month')) 
    is_market_closed = models.BooleanField(default=False, verbose_name=_('is_market_closed')) 
    
    objects = TradingDateManager() 