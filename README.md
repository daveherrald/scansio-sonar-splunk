# scansio-sonar-splunk

## download.py
download.py downloads the files associated with a particular study available at https://scans.io. This project currently focuses on the "SSL Certificates" (sonar.ssl) and "HTTPS (TCP/443)" (sonar.https) studies, however download.py can be used to download any of the available studies.

Summary of options:

```
$ python ./download.py -h
usage: download.py [-h] [--downloadpath DOWNLOADPATH] [--verbose]
                   [--liststudies] [--study STUDY] [--listurls] [--listfiles]
                   [--poolsize POOLSIZE] [--studysize]

optional arguments:
  -h, --help            show this help message and exit
  --downloadpath DOWNLOADPATH
                        Location to store downloaded files. (default /sonar)
  --verbose             Show verbose status information. (default: No)
  --liststudies         Print a list of available studies and immediately
                        exit. (default: No)
  --study STUDY         Download files from this study. Use --list to view
                        list of studies. Takes either uniqid or quoted Short
                        Description. (default: SSL Certificates)
  --listurls            List data file URLS from this study. Use --list to
                        view list of studies. Use --study to specify a study.
  --listfiles           List fully-qualified data file locations for this
                        study. This option does NOT check to see that the file
                        exists. Use --list to view list of studies. Use
                        --study to specify a study.
  --poolsize POOLSIZE   Number of processes to spawn. (default: 1)
  --studysize           Return the current size of this study on the scans.io
                        server. Use --study to specify a study.
```


# Python Version
All scripts were developed and tested using Python 2.7.x. A conscious, though admittedly somewhat painful, decision was made to avoid Python 3 becasue portion of this code may someday be integrated more tightly into Splunk (e.g. as a modular input), and splunk does not currently support Python 3. 
