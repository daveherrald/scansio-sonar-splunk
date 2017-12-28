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

Use the --liststudies option to list the studies available at https://scans.io. The script first downloads https://scansio/json and parses it for convenient display.
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
