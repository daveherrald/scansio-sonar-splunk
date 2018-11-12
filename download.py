from __future__ import division
import math
import argparse
import sys
import multiprocessing
import logging
import hashlib
import requests
import os
import re
import time
import random
import locale


def sha1_file (fqname):
    with open('{f}'.format(f=fqname), 'rb') as fh:
        h = hashlib.sha1()
        while True:
            data = fh.read(8192)
            if not data:
                break
            h.update(data)
    sha1 = h.hexdigest()
    return sha1


def get_scans_io_json(url='https://scans.io/json'):
    scansio_feed = requests.get(url)
    if scansio_feed.status_code == 200:
        feed = scansio_feed.json()
        if 'studies' in feed:
            return feed
        else: return None
    else:
        return None
def download_file(file_q, downloadpath, study, verbose=False):
    logger = logging.getLogger("SPLUNKSONAR")
    if verbose:
        logger.warning("Worker starting. Download path: {}  study: {}".format(downloadpath, study))
    while True:
        item = file_q.get()
        if item == "DONE":
            if verbose:
               logger.warning("End of queue. Worker exiting")
            return True

        download = True

        fqname = get_study_file_fqname(item['name'], study, downloadpath, verbose)

        logger.warning("Processing file {}".format(fqname))

        if os.path.isfile(fqname):
            if verbose:
                logger.warning('File {0} exists checking hash...'.format(fqname))
            if not sha1_file(fqname) == item['fingerprint']:
                if verbose:
                    logger.warning( 'File {0} exists but sha1 hash does not match. Downloading ({1}).'.format(fqname, item['size']))
                download=True
            else:
                if verbose:
                    logger.warning('File {0} exists and sha1 hash matches. Not downloading'.format(fqname))
                download=False

        if download:
            time.sleep(random.random() * 10)
            m = re.search('^(.+\/).+$', fqname)
            download_path = m.group(1)
            if not os.path.exists(download_path):
                if verbose:
                    logger.warning('Path {0} does not exist. Creating'.format(fqname))
                os.makedirs(download_path)
            success = False
            attempt = 0
            while not success and attempt < 100:
                attempt = attempt +1
                if verbose:
                    logger.warning('Attempt {0} for {1}'.format(attempt, fqname))
                download_stream = requests.get(item['name'], stream=True)
                with open('{f}'.format(f=fqname), 'wb') as filename:
                    for chunk in download_stream.iter_content(chunk_size=1024):
                        if chunk:
                            filename.write(chunk)
                if sha1_file(fqname) == item['fingerprint']:
                    success = True
                else:
                    logger.warning(u'File {0} does not match SHA1 fingerprint. Retrying'.format(fqname))


def download_files(feed, study, downloadpath, numproc=1, verbose=False):
    logger = logging.getLogger("SPLUNKSONAR")
    file_q = multiprocessing.Queue()
    pool = multiprocessing.Pool(numproc, download_file,(file_q, downloadpath, study, True,))

    if verbose:
        logger.warning("Getting metadata for {}.".format(study))
    download_list = get_study_file_metadata(feed, study, verbose)

    for item in download_list:
        file_q.put(item)

    for i in range(numproc):
        file_q.put("DONE")
    pool.close()
    pool.join()
    

def get_studies(feed):
    result=[]
    if 'studies' in feed:
        for item in feed['studies']:
            result.append([item['name'], item['uniqid'], item['short_desc'], get_study_size(feed,item['name'],False)])
    return result


def handle_studies( ):
    logger = logging.getLogger("SPLUNKSONAR")
    studies = get_studies(get_scans_io_json())
    print
    print ("{: <75} {: <25} {: <9}".format("Study", "Uniqe ID(uniqid)", "Size (GB)"))
    print ("{: <75} {: <25} {: <9}".format("-" * 75 , "-" * 25 , "-" * 9 ))
    for row in studies:
        print("{: <75} {: <25} {: >9}".format(row[0], row[1], int(math.ceil(row[3]))))
    print
    print("More details available at https://scans.io")
    print


def normalize_size(sizestr):
    m = re.search('([\d\,\.]+)\s{0,1}([KMGTP])B?', sizestr)
    try:
        magnitude = m.group(1)
    except:
        magnitude = '0'
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    magnitude = locale.atof(magnitude)
    try:
        unit = m.group(2)
    except:
        unit = 'G'
    if unit == 'K' or unit == 'k':
        return magnitude / 1024 / 1024
    if unit == 'M' or unit == 'm':
        return magnitude / 1024 
    if unit == 'G' or unit == 'g':
        return magnitude 
    if unit == 'T' or unit == 't':
        return magnitude * 1024
    if unit == 'P' or unit == 'p':
        return magnitude * 1024 * 1024
    return None


def get_study_file_metadata(feed, study, verbose=False):
    logger = logging.getLogger("SPLUNKSONAR")
    study_file_metadata_list = []
    if 'studies' in feed:
        for result in feed['studies']:
            if result['name'] == study or result['uniqid'] == study :
                for res in result['files']:
                    name = res['name']
                    study_file_metadata_list.append(res)
    return study_file_metadata_list
    

def get_study_file_urls(feed, study, verbose=False):
    logger = logging.getLogger("SPLUNKSONAR")
    metadata = get_study_file_metadata(feed, study, verbose)
    study_file_urls = []
    for item in metadata:
        study_file_urls.append(item['name'])
    return study_file_urls 
    

def get_study_file_fqname(url, uniqid, downloadpath, verbose=False):
    m = re.search('.+\/(.*)', url)
    normalized_name = m.group(1)
    fqname = '{0}/{1}/{2}'.format(downloadpath, uniqid, normalized_name)
    return fqname

    
def get_study_file_fqnames(feed, study, downloadpath, verbose=False):
    logger = logging.getLogger("SPLUNKSONAR")
    study_file_fqnames = []
    urls = get_study_file_urls(feed, study, verbose)
    for url in urls:
        study_file_fqnames.append(get_study_file_fqname(url, study, downloadpath, verbose))
    return study_file_fqnames 


def get_file_size(feed, study, url):
    if 'studies' in feed:
        for result in feed['studies']:
            if result['name'] == study or result['uniqid'] == study :
                for res in result['files']:
                    if res['name']==url:
                        if 'size' in res:
                            return normalize_size(res['size'])
    return 0
                      

def get_study_size(feed, study, verbose=False):
    urls = get_study_file_urls(feed, study, verbose=False)
    study_size_gb = 0 
    for url in urls:
        file_size_gb = get_file_size(feed, study, url)
        study_size_gb = study_size_gb + file_size_gb
    return study_size_gb 
    
    
def get_uniqid(feed, study):
    if 'studies' in feed:
        for result in feed['studies']:
            if result['name'] == study or result['uniqid'] == study:
                return result['uniqid'] 
    return None


def main(argv):
    logger = logging.getLogger('SPLUNKSONAR')
    logger_format = logging.Formatter('\033[1;32m%(levelname)-5s %(module)s:%(funcName)s():%(lineno)d %(asctime)s\033[0m| %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logger_format)
    stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler)

    DEFAULT_DOWNLOAD_PATH = u'/sonar'
    DEFAULT_STUDY = u'SSL Certificates'
    DEFAULT_POOLSIZE = 1

    parser = argparse.ArgumentParser()
    parser.add_argument('--downloadpath', default=DEFAULT_DOWNLOAD_PATH,
                        help=u'Location to store downloaded files. (default {0})'.format(DEFAULT_DOWNLOAD_PATH))

    parser.add_argument('--verbose', action="store_true", 
                        help=u'Show verbose status information. (default: No)')

    parser.add_argument('--liststudies', action="store_true", 
                        help=u'Print a list of available studies and immediately exit. (default: No)')

    parser.add_argument('--study', default=DEFAULT_STUDY, 
                        help=u'Download files from this study. Use --list to view list of studies. Takes either uniqid or quoted Short Description. (default: {0})'.format(DEFAULT_STUDY))

    parser.add_argument('--listurls', action="store_true", 
                        help=u'List data file URLS from this study. Use --list to view list of studies. Use --study to specify a study.')

    parser.add_argument('--listfiles', action="store_true", 
                        help=u'List fully-qualified data file locations for this study. This option does NOT check to see that the file exists. Use --list to view list of studies. Use --study to specify a study.')

    parser.add_argument('--poolsize', default=DEFAULT_POOLSIZE, 
                        help=u'Number of processes to spawn. (default: {0})'.format(DEFAULT_POOLSIZE))

    parser.add_argument('--studysize', action="store_true", 
                        help=u'Return the current size of this study on the scans.io server. Use --study to specify a study.')

    # check if there are no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # parse arguments
    args = parser.parse_args(argv[1:])

    if args.liststudies:
        handle_studies()
        sys.exit(1)

    if args.verbose == True:
        logger.warning(u'Downloading scans.io JSON manifest')
    feed=get_scans_io_json()
    if not feed:
        logger.error("Error retrieving https://scans.io/json. Exiting")
        sys.exit(1)

    study = get_uniqid(feed, args.study)

    if args.listurls:
        urls = get_study_file_urls(feed, study, verbose=False)
        for url in urls:
            print url
        sys.exit(1)

    if args.listfiles:
        fqnames = get_study_file_fqnames(feed, study, args.downloadpath, verbose=False)
        for fqname in fqnames:
            print fqname
        sys.exit(1)

    if args.studysize:
        print ('{} GB'.format(int(math.ceil(get_study_size(feed, study, args.verbose)))))
        sys.exit(1)

    poolsize = int(args.poolsize)
    if args.verbose:
        logger.warning("Pool size is set to {} processes.".format(poolsize))
    download_files(feed, study, args.downloadpath, poolsize, True)


if __name__ == '__main__':
    main(sys.argv)
