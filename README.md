# scansio-sonar-splunk

The goal of this project is to make it possible for security researchers, threat intelligence analysts, and security operations teams to take advantage of the [Internet-Wide Scan Data Repository](https://scans.io) study data using Splunk. The tools included here download, parse, and enrich scan study data before loading it into Splunk for analysis. 

This project is inspired by the excellent work by [Mark Parsons](https://github.com/mpars0ns). Our goal is to extend upon the tools and techniques that Mark has pioneered. Significant portions of the code in this repository are copied with permission from Mark's [scansio-sonar-es](mpars0ns/scansio-sonar-es)

This project focuses on the use of [Splunk](https://splunk.com) as the analysis platform for large scale Internet scan data. Splunk is a commercial product, and the creators of the project are Splunk employees. You will need to arrange for proper Splunk licensing in oder to use this project. Some uses of this project are supported by the Splunk Enterprise Trial license and/or Splunk Free edition.

## download.py
download.py retrieves the files associated with a particular study available at https://scans.io. This script downloads the files and stores them locally. Other scripts in this repository are reponsible for parsing, enriching, and loading the files into Splunk. This project currently focuses on the "SSL Certificates" (sonar.ssl) and "HTTPS (TCP/443)" (sonar.https) studies, however download.py can be used generally to download any of the available studies. Integrity of the downloaded files is validated using a checksum. If a file has already been downloaded, and the checksum matches, it will not be downloaded again. download.py can use Python multi-processing to parrallelize the download process. download.py is often a long-running process so we recommend using screen. download.py does not have built-in safegurads to prevent filling up the disk. Use the --liststudies option to plan accordingly.

### Summary of options:

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

### View the list of available studies

Use the --liststudies option to list the studies available at https://scans.io. The script downloads https://scansio/json and parses it for convenient display. The output contains the name of the study as well as the unique identifier (uniqid) and the estimated size of the stufy files in gigabytes. The example below is a point in time (12/28/2017). You should download the script and run it yourself to view the most current output.

```
$ python ./download.py --liststudies

Study                                                                       Uniqe ID(uniqid)          Size (GB)
--------------------------------------------------------------------------- ------------------------- ---------
TLS in the E-mail Ecosystem                                                 sba-email                       202
Top 1 Million Site Scans                                                    scott-top-one-million           617
Nonce-Disrespecting Adversaries: Practical Forgery Attacks on GCM in TLS    nonce-disrespect                 35
Zonefile Database                                                           axfr-research                     2
HTTPS Ecosystem Scans                                                       umich-https                     261
Hurricane Sandy ZMap Scans                                                  umich-sandy                      33
Alexa Top Million Session Ticket Scans                                      umich-crypto-shortcuts          229
Heartbleed Vulnerability                                                    umich-heartbleed                  0
Security Challenges in an Increasingly Tangled Web Crawls                   tangled                          42
Reverse DNS (RDNS)                                                          sonar.rdns_v2                   859
Forward DNS (FDNS)                                                          sonar.fdns_v2                  1022
National Exposure TCP SYN Scans                                             sonar.national_exposure           6
HTTP (TCP/80)                                                               sonar.http                     7374
More SSL Certificates (non-443)                                             sonar.moressl                    76
SSL Certificates                                                            sonar.ssl                       298
Forward DNS (FDNS ANY) -- DEPRECATED                                        sonar.fdns                     1122
Critical.IO Service Fingerprints                                            sonar.cio                       355
Reverse DNS (RDNS) -- DEPRECATED                                            sonar.rdns                      634
Rapid7 Heisenberg Cloud Honeypot cowrie Logs                                heisenberg.cowrie                 1
ATG 10001/TCP SYN Scans                                                     sonar.atg_10001_tcp               1
TCP Scans                                                                   sonar.tcp                        42
UDP Scans                                                                   sonar.udp                       232
HTTPS (TCP/443)                                                             sonar.https                    3114
SNI Proxy ZMap Scans                                                        sniproxy                          3
Scan for AXFR DNS replies                                                   hanno-axfr                        1
IPv4 HTTP Scans                                                             mi                               31

More details available at https://scans.io
```


# Python Version
All scripts were developed and tested using Python 2.7.x. A conscious, though admittedly somewhat painful, decision was made to avoid Python 3 becasue portion of this code may someday be integrated more tightly into Splunk (e.g. as a modular input), and splunk does not currently support Python 3. 
