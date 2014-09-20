#!/usr/bin/python
__author__ = 'liteman'


from netaddr import *
import argparse
import sys
import subprocess
import os
import string
import urllib2
import re

def list_all_urls(path):
    """
    List all websites
    @param path: if it is a path, read the file and return a list of values,
    if a string, return a list of one

    """

    urllist = []
    if os.path.exists(path):
        f = open(path, 'r')
        for urlstr in f.readlines():
            urlstr = urlstr.strip()
            #print "Debug: urlstr is -" + urlstr + "- end line."  # debug string
            if urlstr == '':
                continue
            urllist.append(urlstr.strip())
        f.close()

        return urllist

    else:
        urllist.append(path)
    return urllist

def execute(cmdstr):

    cmd = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cmd.stdout.readline().decode("ASCII").rstrip()  # expected output is only one line in length

def dedup(duplist):
    nodups = []
    for item in duplist:
        if item not in nodups: nodups.append(item)

    return nodups

def beginscrape(args):
    #TODO VALIDATE URLs
    '''

    :param args:
    :return:

    Reference: http://www.pythonforbeginners.com/python-on-the-web/how-to-use-urllib2-in-python/
    '''
    urllist = list_all_urls(args.url)

    for url in urllist:
        print ""
        response = urllib2.urlopen(url)
        html = response.read()
        #e-mail pattern: <a href="mailto:rchapin@gmu.edu">rchapin@gmu.edu</a></p>
        #e-mail pattern: csadmin /@/ cs.gmu.edu
        patternList = ["[:<>\s]{0,1}([\d\w]+@[\d\w]{3}[\d\w]*\.\w{2}\w*)[<>:\s\"]{0,1}",
                       ">(\w+\s/@/\s\w{2,3}.\w{2,3}[\.\w]*)[<>:\s\"]",
                       "[:<>\s]{0,1}(\w+\s\[at\]\s\w+\s\[dot\]\s\w{2,3})[:<>\s\"]{0,1}",
                       "[:<>\s]{0,1}(\w+\s\[at\]\s\w+\sdot\s\w{2,3})[:<>\s\"]{0,1}",
                       "[:<>\s]{0,1}(\w+\sat\s\w+\sdot\s\w{2,3})[:<>\s\"]{0,1}",
                       "[:<>\s]{0,1}(\w+\sat\s\w+\s\.\s\w{2,3})[:<>\s\"]{0,1}",
                       "[:<>\s]{0,1}(\w+\s@\s\w+\sdot\s\w{2,3})[:<>\s\"]{0,1}",
                       "[:<>\s]{0,1}(\w+\s@\s\w+\s\.\s\w{2,3})[:<>\s\"]{0,1}"]

        emailcount = 0
        emaillist = []
        for pattern in patternList:
            matches = re.findall(pattern, html)

            if matches:
                matches = dedup(matches)
                emailcount += len(matches)
                for match in matches:
                    emaillist.append(match)

        if emailcount > 0:
            print "Page: " + url
            print "\tE-mail count: " + str(len(emaillist))
            print "\tList: "
            for mail in emaillist:
                print "\t\t" + mail
        else:
            print "Page: " + url
            print "No e-mail addresses found"



def main(argv):

    parser = argparse.ArgumentParser(description="Enumerate hosts through DNS", add_help=True)

    parser.add_argument("--url",
                        help="Enumerate the specified URL or list of URLs -- must be in the from http://dom.tld/page",
                        metavar="URL or FILE",
                        required=True)
    parser.add_argument("-v", "--verbose",
                        help="Displays additional output",
                        action="store_true",
                        required=False)


    args = parser.parse_args()

    if args.verbose:
        print "-v flag set. Debugging on.\n"

    beginscrape(args)


main(sys.argv[1:])











