import argparse
import re
import sys
import logging
from datetime import datetime
import hashlib
import gzip
import requests
import os
import json
import time
from splunk_http_event_collector import http_event_collector
from helpers.certparser import process_cert
from helpers.hostparser import proccess_host
import multiprocessing
import random


def process_certs_file(file_queue, key, logger, hostlist=['localhost'], batchsize=16384, index='sonarsslcert', sourcetype='sonarsslcert'):
    while True:
        host = random.choice(hostlist)
        print host
        hec = http_event_collector(key, host)
        gzfilename = file_queue.get()
        if gzfilename == "DONE":
            return True 
        logger.warning("Loading file {f} at {d}".format(f=gzfilename, d=datetime.now()))
        with gzip.open(gzfilename, 'rb') as resultsfile:
            m = re.search('.*\/(\d{8})', gzfilename)
            if m:
                filedate = m.group(1)
            else:
                m = re.search('.*\/(\d{4}-\d{2}-\d{2})', gzfilename)
                filedate = m.group(1)
                filedate = re.sub('-', '', filedate, 0, 0)
            filedate_struct = time.strptime(filedate, "%Y%m%d")
            filedate_epoch = time.mktime(filedate_struct)
            batchcount = 0
            for line in resultsfile:
                cleanline = line.strip('\n')
                (hash_string, cert_b64) = cleanline.split(',', 1)
                newcert = process_cert(cert_b64, logger)
                newcert_dict = json.dumps(newcert)
                payload = {}
                payload.update({"index":index})
                payload.update({"sourcetype":sourcetype})
                payload.update({"source":gzfilename})
                payload.update({"event":newcert_dict})
                hec.batchEvent(payload)
                batchcount = batchcount + 1
                if batchcount == batchsize:
                    hec.flushBatch()
                    batchcount = 0
            if batchcount > 0:
                hec.flushBatch()


def main(argv):
    logger = logging.getLogger('SSLImporter')
    logger_format = logging.Formatter('\033[1;32m%(levelname)-5s %(module)s:%(funcName)s():%(lineno)d %(asctime)s\033[0m| '
                                  '%(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logger_format)
    logger.addHandler(stream_handler)
    parser = argparse.ArgumentParser()   
    numproc = 64

    #Cert load test
    directory='/sonar/sonar.ssl'
    http_event_collector_key = "cffe598c-8363-490d-ab32-a42e5a65c4fd"

    file_queue = multiprocessing.Queue()
    pool = multiprocessing.Pool(numproc, process_certs_file,(file_queue, http_event_collector_key, logger,['34.206.168.126','34.237.203.207','34.238.205.37'],))

    for filename in os.listdir(directory):
        if filename.endswith("certs.gz"):
            file_queue.put(os.path.join(directory,filename))

    for i in range(numproc):
        file_queue.put("DONE")

    pool.close() 
    pool.join() 


if __name__ == '__main__':
    main(sys.argv)
