import datetime
from enum import Enum
import logging 
import sys 

from bs4 import BeautifulSoup
import requests

from twse.models import Cron_Job_Log, Trading_Date, Twse_Index_Stats 
from twse.utils.dateutil import roc_year, roc_year_to_western, \
    is_third_wednesday  


logger = logging.getLogger('twse.cronjob')

class DOWNLOAD_RESULT(Enum):
    EXISTS = 1
    FAILED = 2
    SUCCESS = 3 
    
def download_twse_index_stats_job(year=None, month_list=None):
    # 發行量加權股價指數歷史資料(日期    開盤指數    最高指數    最低指數    收盤指數)
    # this job is used to download twse index open,high, low, close index
    # as well as create Trading_Date entry
    _CREATE_TRADING_DATE_OBJECT = True
    _CHECK_LAST_TRADING_DATE = True
    # log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = download_twse_index_stats_job.__name__ 
    try:    
        serviceUrl = 'http://www.twse.com.tw/ch/trading/indices/MI_5MINS_HIST/MI_5MINS_HIST.php'
        if _CHECK_LAST_TRADING_DATE:
            last_trading_date = Trading_Date.objects.get_last_trading_date()
        today = datetime.date.today()
        if not year:
            # default: this year
            year = today.year
        if not month_list:
            month_list = []
            month_list.append(today.month)
            
        # the year parameter is in ROC year , month with 2 digits
        for n in month_list:
            if n < 10:
                month = "0%s" % n
            else:
                month = n
            parameters = {'myear': roc_year(year) , 'mmon': month}
            
            try:        
                httpResponse = requests.post(serviceUrl, data=parameters, stream=True)
                httpResponse.encoding = "big5"
            except requests.HTTPError as e:
                result = e.read()
                raise Exception(result)
            
            soup = BeautifulSoup(httpResponse.text, 'lxml')
            table_element = soup.find('table', class_='board_trad')
            if not table_element:
                logger.warning("No index trading data available!")
                continue
            tr_list = table_element.find_all('tr', class_='gray12')
            trading_date_to_create = []
            twse_index_stats_to_create = []
            j = 0
            for row in tr_list:
                i = 0
                for td_element in row.find_all('td', recursive=False):
                    dt_data = td_element.string.strip()
                    if i == 0:
                        trading_date = roc_year_to_western(dt_data)
                        if _CHECK_LAST_TRADING_DATE:
                            if trading_date <= last_trading_date: break
                            
                        if _CREATE_TRADING_DATE_OBJECT:
                            tdate = Trading_Date()
                            tdate.trading_date = trading_date
                            # date.weekday(): Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
                            tdate.day_of_week = tdate.trading_date.weekday() + 1
                            if j == 0:
                                # first trading date of the month
                                tdate.first_trading_day_of_month = True
#                             if j == len(tr_list) - 1:
#                                 tdate.last_trading_day_of_month = True
                            if is_third_wednesday(tdate.trading_date):
                                tdate.is_future_delivery_day = True
                            trading_date_to_create.append(tdate)
# 
                        twse_index_stats = Twse_Index_Stats()
                        twse_index_stats.trading_date = trading_date
                    elif i == 1:
                        twse_index_stats.opening_price = float(dt_data.replace(',', ''))
                    elif i == 2:
                        twse_index_stats.highest_price = float(dt_data.replace(',', ''))
                    elif i == 3:
                        twse_index_stats.lowest_price = float(dt_data.replace(',', ''))
                    elif i == 4:
                        twse_index_stats.closing_price = float(dt_data.replace(',', ''))
                        twse_index_stats_to_create.append(twse_index_stats)                     
                    i += 1
                j += 1
            if _CREATE_TRADING_DATE_OBJECT: 
                if trading_date_to_create: Trading_Date.objects.bulk_create(trading_date_to_create)          
            if twse_index_stats_to_create: Twse_Index_Stats.objects.bulk_create(twse_index_stats_to_create)
    except:
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()

def download_twse_index_stats2_job(year=None, month_list=None):
    # 市場成交資訊(日期,成交股數,成交金額,成交筆數,發行量加權股價指數,漲跌點數)
    # this job is used to update Twse_Index_Stats's 
    # trade_volume, trade_transaction, trade_value data.
    # Need to be run after download_twse_index_stats_job
    # log_message(datetime.datetime.now())
    job = Cron_Job_Log()
    job.title = download_twse_index_stats2_job.__name__ 
    try:  
        today = datetime.date.today()
        if not year:
            # default: this year
            year = today.year
        if not month_list:
            month_list = []
            month_list.append(today.month)
            
        # the year parameter is in western year , month with 2 digits
        for n in month_list:
            if n < 10:
                month = "0%s" % n
            else:
                month = n
                 
            # serviceUrl = 'http://www.twse.com.tw/ch/trading/exchange/FMTQIK/genpage/Report%s%s/%s%s_F3_1_2.php?STK_NO=&myear=%s&mmon=%s' % (year, month, year, month, year, month)
            serviceUrl = 'http://www.twse.com.tw/ch/trading/exchange/FMTQIK/FMTQIK.php'
            parameters = {'query_year': year , 'query_month': month}
            
            try:        
                httpResponse = requests.post(serviceUrl, data=parameters, stream=True)
                httpResponse.encoding = "big5"
            except requests.HTTPError as e:
                result = e.read()
                raise Exception(result)
            
             
            
            soup = BeautifulSoup(httpResponse.text, 'lxml')
            table_element = soup.find('table')
            if not table_element: 
                logger.warning("No index trading data available!")
                continue
            tbody_element = table_element.find('tbody')
            tr_list = tbody_element.find_all('tr')
            twse_index_stats_to_update = []
            j = 0
            for row in tr_list:
                i = 0
                for td_element in row.find_all('td', recursive=False):
                    dt_data = td_element.string.strip()
                    if i == 0:
                        trading_date = roc_year_to_western(dt_data)
                        try:
                            twse_index_stats = Twse_Index_Stats.objects.by_date(trading_date)
                            if twse_index_stats.trade_volume > 0: 
                                break
                        except:
                            break
                    elif i == 1:
                        twse_index_stats.trade_volume = float(dt_data.replace(',', ''))
                    elif i == 2:
                        twse_index_stats.trade_value = float(dt_data.replace(',', ''))
                    elif i == 3:
                        twse_index_stats.trade_transaction = float(dt_data.replace(',', ''))
                        twse_index_stats_to_update.append(twse_index_stats)  
                        break                   
                    i += 1
                j += 1   
            if twse_index_stats_to_update: 
                for item in twse_index_stats_to_update:
                    item.save()
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()