import logging
from pathlib import Path
import sys
import zipfile

from bs4 import BeautifulSoup
import requests

from twse.models import Cron_Job_Log 
from twse.settings import TWSE_OPTIONS_DOWNLOAD
from twse.utils.dateutil import transform_date_string

logger = logging.getLogger('twse.cronjob')

def download_options_trans_job(): 
    job = Cron_Job_Log()
    job.title = download_options_trans_job.__name__ 
    try:      
        serviceUrl = 'http://www.taifex.com.tw/chinese/3/3_2_4.asp'
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
            logger.warning("No options trans data available!")
            raise Exception("No options trans data available.")
         
        tr_list = table_element.find_all('tr') 
        #skip the first tr element
        for i, row in enumerate(tr_list[1:]):
            row_list = row.find_all('td', recursive=False)
            # use the second td element
            td_element= row_list[1]
            dt_data = td_element.string.strip()
            date_string = transform_date_string(dt_data)
            exists, filename = _get_options_trans(date_string)
            if not exists:
                logger.info("Options trans data of %s is downloaded: filename: %s" % (date_string,filename))
    except: 
        logger.warning("Error when perform cron job %s" % sys._getframe().f_code.co_name, exc_info=1)
        job.failed()
        raise  
    finally:
        job.save()
                
def _get_options_trans(qdate_str, target_dir=TWSE_OPTIONS_DOWNLOAD):
    # exists = False if the zip file is successfully downloaded
    # exists = True if tje zip file exists.
    exists = False
    # qdate_str format: eg. 2016_12_22
    zip_filename = "OptionsDaily_%s.zip" % qdate_str
    filename = "%s/%s" % (target_dir, zip_filename)
    # check if option trans data exists 
    if Path(filename).is_file():
        logger.info("Option trans data of %s exists, so skip ..." % qdate_str)
        exists = True
    else:
        logger.info("downloading option trans data...")
        serviceUrl = "http://www.taifex.com.tw/DailyDownload/OptionsDailyDownloadCSV/%s" % zip_filename
        try:        
            httpResponse = requests.get(serviceUrl, stream=True)
        except requests.HTTPError as e:
            result = e.read()
            raise Exception(result)
        
        with open(filename, 'wb') as fd:
            for chunk in httpResponse.iter_content(chunk_size=1000):
                fd.write(chunk)
    return (exists, filename)

def _extract_from_zipfile(filename, target_dir=TWSE_OPTIONS_DOWNLOAD):
    # filename: full path for the zipfile
    # target_dir: target directory to unzip into 
    
    zf = zipfile.ZipFile(filename, 'r')
    info_list = zf.infolist()
    if len(info_list) == 0 :
        raise Exception("No content in zip file : %s" % filename)
    zipinfo = info_list[0]
    zf.extract(zipinfo, path=target_dir)
    unzipped = "%s/%s" % (target_dir , zipinfo.filename)
    logger.info("extracting zipfile as %s ..." % unzipped)
    return unzipped
#     
# def _process_options_trans(filename):
#     logger.info("processing twse options trans data...")
#      
#     items_to_save = [] 
#     record_stored = 0
#     with codecs.open(filename, 'r', encoding="Big5") as csvfile:
#         csvreader = csv.reader(csvfile, delimiter=',')
#         for row in csvreader:
#             
#          
