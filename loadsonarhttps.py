import multiprocessing
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
import random
import base64
import codecs

def process_https_file(file_queue, key, hostlist=['localhost'], batchsize=16384, index='sonarhttps', sourcetype='sonar:https'):
    logger = logging.getLogger("HTTPSImporter")
    while True:
        host = random.choice(hostlist)
        print host
        hec = http_event_collector(key, host)
        gzfilename = file_queue.get()
        if gzfilename == "DONE":
            return True
        logger.warning("Loading file {f} at {d}".format(f=gzfilename, d=datetime.now()))
        with gzip.open(gzfilename, 'rb') as resultsfile:
            print gzfilename
            m = re.search('^.*\/(\d{4})\-?(\d{2})\-?(\d{2})', gzfilename)
            filedate = '{}{}{}'.format(m.group(1), m.group(2), m.group(3))
            filedate_struct = time.strptime(filedate, "%Y%m%d")
            filedate_epoch = time.mktime(filedate_struct)
            batchcount = 0
            for line in resultsfile:
                new_https_get_dict = {}
                new_https_get_dict = json.loads(line)
                new_https_get_dict['data_decoded'] = unicode(base64.b64decode(new_https_get_dict['data']), errors='ignore')
                payload = {}
                payload.update({"index":index})
                payload.update({"host":host})
                payload.update({"sourcetype":sourcetype})
                payload.update({"source":gzfilename})
                payload.update({"event":new_https_get_dict})
                hec.batchEvent(payload)
                batchcount = batchcount + 1
                if batchcount == batchsize:
                    hec.flushBatch()
                    batchcount = 0
            if batchcount > 0:
                hec.flushBatch()

def get_files_to_load(path="/sonar", project="sonar.ssl", reverse=False):
    files_to_load = []
    
    if project == "sonar.ssl":
        return files_to_load 
    if project == "sonar.https":
        tmp_dict = {}
        for filename in os.listdir(os.path.join(path,project)):
            m = re.search('^(\d{4})\-?(\d{2})\-?(\d{2})', filename)
            datestring = '{}{}{}'.format(m.group(1), m.group(2), m.group(3))
            tmp_dict[datestring] = filename
        sortedkeys = sorted(tmp_dict.keys(), key=int, reverse=reverse) 
        for datestring in sortedkeys:
            files_to_load.append(os.path.join(path, project, tmp_dict[datestring]))
        return files_to_load
    return []


def main(argv):
    logger = logging.getLogger('HTTPSImporter')
    logger_format = logging.Formatter('\033[1;32m%(levelname)-5s %(module)s:%(funcName)s():%(lineno)d %(asctime)s\033[0m| '
                                  '%(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logger_format)
    logger.addHandler(stream_handler)
    parser = argparse.ArgumentParser()   
    numproc = 32 

    directory='/sonar'
    project_uniqid = 'sonar.https'
    http_event_collector_key = "8e77145a-e160-48b8-9744-8b098bd7270a"

    file_queue = multiprocessing.Queue()
    pool = multiprocessing.Pool(numproc, process_https_file,(file_queue, http_event_collector_key, ['172.31.45.216', '172.31.41.80', '172.31.40.226'],))

    myfiles = get_files_to_load(directory, project_uniqid, True)

    for item in myfiles:
        file_queue.put(item)

    for i in range(numproc):
        file_queue.put("DONE")

    pool.close()
    pool.join()

if __name__ == '__main__':
    main(sys.argv)
