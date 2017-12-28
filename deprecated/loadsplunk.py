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


def process_hosts_file(gzfilename, key, logger, host='localhost', batchsize=16384, index='hosts', sourcetype='sonar-host', useesid=False):
    logger.warning("Loading file {f} at {d}".format(f=gzfilename, d=datetime.now()))
    hec = http_event_collector(key, host)
    with gzip.open(gzfilename, 'rb') as resultsfile:
        m = re.search('.*\/(\d{8})', gzfilename)
        filedate = m.group(1)
        filedate_struct = time.strptime(filedate, "%Y%m%d")
        filedate_epoch = time.mktime(filedate_struct)
        batchcount = 0
        for line in resultsfile:
            cleanline = line.strip('\n')
            (host, certhash) = cleanline.split(',', 1)
            newhost = {}
            newhost['host'] = host
            newhost['hash'] = certhash
            newhost['seen'] = filedate
            newhost['seen_epoch'] = filedate_epoch
            if useesid:
                cert_hash = hashlib.sha1(newhost['host']+newhost['hash']+'sonar')
                newhost['id'] = cert_hash.hexdigest()
            newhost = proccess_host(newhost, logger)
            payload = {}
            payload.update({"index":index})
            payload.update({"host":host})
            payload.update({"sourcetype":sourcetype})
            payload.update({"source":gzfilename})
            payload.update({"event":newhost})
            hec.batchEvent(payload)
            batchcount = batchcount + 1
            if batchcount == batchsize:
                hec.flushBatch()
                batchcount = 0
        if batchcount > 0:
            hec.flushBatch()


def process_certs_file(gzfilename, key, logger, host='localhost', batchsize=16384, index='certs', sourcetype='sonar-cert'):
    logger.warning("Loading file {f} at {d}".format(f=gzfilename, d=datetime.now()))
    hec = http_event_collector(key, host)
    with gzip.open(gzfilename, 'rb') as resultsfile:
        m = re.search('.*\/(\d{8})', gzfilename)
        filedate = m.group(1)
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

'''
def main(argv):
    logger = logging.getLogger('SSLImporter')
    logger_format = logging.Formatter('\033[1;32m%(levelname)-5s %(module)s:%(funcName)s():%(lineno)d %(asctime)s\033[0m| '
                                  '%(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logger_format)
    logger.addHandler(stream_handler)
    parser = argparse.ArgumentParser()   

    #Cert load test
    gzfilename = '/ssl/sonar/20150615_certs.gz'
    http_event_collector_key = "f81e6e7e-1342-4fd7-8445-652ab368618b"

    process_certs_file(gzfilename, http_event_collector_key, logger)


    # Host load
    gzfilename = '/ssl/sonar/20131030_hosts.gz'
    http_event_collector_key = "5c95a3ec-5521-4ad6-ad93-e926bc09747c"

    process_hosts_file(gzfilename, http_event_collector_key, logger)


if __name__ == '__main__':
    main(sys.argv)
'''
