from datetime import timedelta 
import logging
from pathlib import Path
import sys 

import requests

from sgx.models import Download_Log
from twse.cron import DOWNLOAD_RESULT
from twse.models import Cron_Job_Log , Trading_Date
from twse.settings import SGX_DOWNLOAD
from twse.utils.dateutil import  dateToString


logger = logging.getLogger('twse.cronjob')

# below job is used for downloading old sgx trans data - one time use 
def download_sgx_trans_job_old(): 
    job = Cron_Job_Log()
    job.title = download_sgx_trans_job_old.__name__ 
    try:      
        #last_trading_date = Trading_Date.objects.get_last_trading_date()
        #last_download_log = Download_Log.objects.last_download()
        first_download_log = Download_Log.objects.first_download()
        serial_id = first_download_log.serial_id - 1
        trading_date = first_download_log.trading_date
        for i in range(1, 45):
            d_date=trading_date - timedelta(days=i * 1)
            date_string = dateToString(d_date)
            result_code, filename = _get_sgx_trans(date_string, serial_id)
            if result_code==DOWNLOAD_RESULT.EXISTS:
                logger.info("Sgx trans data of %s exists, so skip ..." % date_string)
                Download_Log.objects.create(trading_date=d_date, serial_id=serial_id)
                serial_id-=1
            elif result_code == DOWNLOAD_RESULT.FAILED:
                    logger.info("Sgx trans data of %s cannot be downloaded." % date_string)
            else:
                logger.info("Sgx trans data of %s is successfully downloaded: filename: %s" % (date_string, filename))
                Download_Log.objects.create(trading_date=d_date, serial_id=serial_id)
                serial_id-=1
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()
        
# below job is used to download sgx future data 
def download_sgx_trans_job(): 
    job = Cron_Job_Log()
    job.title = download_sgx_trans_job.__name__ 
    try:      
        last_trading_date = Trading_Date.objects.get_last_trading_date()
        last_download_log = Download_Log.objects.last_download()
         
        serial_id = last_download_log.serial_id + 1
        trading_date = last_download_log.trading_date
        i = 1
        while True:
            d_date=trading_date + timedelta(days=i * 1)
            if d_date > last_trading_date:
                break
            date_string = dateToString(d_date)
            result_code, filename = _get_sgx_trans(date_string, serial_id)
            if result_code==DOWNLOAD_RESULT.EXISTS:
                logger.info("Sgx trans data of %s exists, so skip ..." % date_string)
                Download_Log.objects.create(trading_date=d_date, serial_id=serial_id)
                serial_id+=1
            elif result_code == DOWNLOAD_RESULT.FAILED:
                    logger.info("Sgx trans data of %s cannot be downloaded." % date_string)
            else:
                logger.info("Sgx trans data of %s is successfully downloaded: filename: %s" % (date_string, filename))
                Download_Log.objects.create(trading_date=d_date, serial_id=serial_id)
                serial_id+=1
            i+=1
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()

    
def _get_sgx_trans(qdate_str, serial_id, target_dir=SGX_DOWNLOAD):
    # qdate_str format: eg. 20161222
    zip_filename = "WEBPXTICK_DT-%s.zip" % qdate_str
    filename = "%s/%s" % (target_dir, zip_filename)
    # check if sgx trans data exists 
    if Path(filename).is_file():
        result_code = DOWNLOAD_RESULT.EXISTS
    else:
        logger.info("downloading sgx trans data...")
        serviceUrl = 'http://infopub.sgx.com/Apps?A=COW_Tickdownload_Content&B=TimeSalesData&F=%s&G=%s' % (serial_id, zip_filename)
        try:        
            httpResponse = requests.get(serviceUrl, stream=True)
            if httpResponse.headers['Content-Type'] != 'application/download' : 
                result_code = DOWNLOAD_RESULT.FAILED
            else:
                with open(filename, 'wb') as fd:
                    for chunk in httpResponse.iter_content(chunk_size=1000):
                        fd.write(chunk) 
                result_code = DOWNLOAD_RESULT.SUCCESS
        
        except requests.HTTPError as e:
            result = e.read()
            logger.warning(result)
            result_code = DOWNLOAD_RESULT.FAILED
    return (result_code, filename)
