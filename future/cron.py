import logging
from pathlib import Path
import sys 

from bs4 import BeautifulSoup
import requests

from twse.models import Cron_Job_Log 
from twse.settings import TWSE_FUTURE_DOWNLOAD
from twse.utils.dateutil import  transform_date_string


logger = logging.getLogger('twse.cronjob')

def download_future_trans_job(): 
    job = Cron_Job_Log()
    job.title = download_future_trans_job.__name__ 
    try:      
        serviceUrl = 'http://www.taifex.com.tw/chinese/3/3_1_3.asp'
        try:        
            httpResponse = requests.get(serviceUrl, stream=True)
            httpResponse.encoding = "utf-8"
        except requests.HTTPError as e:
            result = e.read()
            raise Exception(result)
        
        soup = BeautifulSoup(httpResponse.text, 'lxml')
        table_list = soup.find_all('table', class_='table_c')
        # use second table with css class 'table_c'
        table_element = table_list[1]
        if not table_element: 
            logger.warning("No future trans data available!")
            raise Exception("No future trans data available.")
         
        tr_list = table_element.find_all('tr') 
        #skip the first tr element
        for i, row in enumerate(tr_list[1:]):
            row_list = row.find_all('td', recursive=False)
            # use the second td element
            td_element= row_list[1]
            dt_data = td_element.string.strip()
            date_string = transform_date_string(dt_data)
            exists, filename = _get_future_trans(date_string)
            if not exists:
                logger.info("Future trans data of %s is downloaded: filename: %s" % (date_string,filename))
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()
                
def _get_future_trans(qdate_str, target_dir=TWSE_FUTURE_DOWNLOAD):
    # exists = False if the zip file is successfully downloaded
    # exists = True if tje zip file exists.
    exists = False
    # qdate_str format: eg. 2016_12_22
    zip_filename = "Daily_%s.zip" % qdate_str
    filename = "%s/%s" % (target_dir, zip_filename)
    # check if option trans data exists 
    if Path(filename).is_file():
        logger.info("Future trans data of %s exists, so skip ..." % qdate_str)
        exists = True
    else:
        logger.info("downloading future trans data...")
        serviceUrl = "http://www.taifex.com.tw/DailyDownload/DailyDownloadCSV/%s" % zip_filename
        try:        
            httpResponse = requests.get(serviceUrl, stream=True)
        except requests.HTTPError as e:
            result = e.read()
            raise Exception(result)
        
        with open(filename, 'wb') as fd:
            for chunk in httpResponse.iter_content(chunk_size=1000):
                fd.write(chunk)
    return (exists, filename)