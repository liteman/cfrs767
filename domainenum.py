#!/usr/bin/python
__author__ = 'liteman'

from netaddr import *
import argparse
import sys
import subprocess
import os
import string
import random

def list_all_domains(path):
    """
    List all domains
    @param path: if it is a path, read the file and return a list of values,
    if a string, return a list of one

    """

    domainlist = []
    if os.path.exists(path):
        f = open(path, 'r')
        for domain in f.readlines():
            domain = domain.strip()
            #print "Debug: domain is -" + domain + "- end line."  # debug string
            if domain == '':
                continue
            domainlist.append(domain.strip())
        f.close()

        return domainlist

    else:
        domainlist.append(path)
    return domainlist

def verifyDomain():
    '''
    #TODO -- perform some type of connectivity test to identify valid hosts
    :return: Boolean specifying whether connectivity test was successful
    '''
    #TODO

    return True

def execute(cmdstr):

    cmd = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cmd.stdout.readline().decode("ASCII").rstrip()

def domainLookup(domain, server=""):

    #find A record with command: host <domain> <soa server> | grep "has address"
    #Sample output: gmu.edu has address 129.174.1.38
    arecord = execute("host " + domain + " " + server + " | grep 'has address'")
    if arecord == '':
        return "Not Found"
    else:
        return arecord.split()[-1]

def findSOA(domain):
    #find SOA for root: host -C <root domain> | grep -m 1 SOA
    # sample output:
    # gmu.edu has SOA record magda.gmu.edu. dnsadmin.gmu.edu. 2009036937 10800 3601 604800 86400
    soa = execute("host -C " + domain + " | grep -m 1 SOA")
    if soa == '':
        return soa
    else:
        soa = soa.split()[4].rstrip(".")

    return soa

def subdomaingenerator(size=9, chars=string.ascii_lowercase):
    '''
    Function that will return a random string of characters
    :param size: length of string to return
    :param chars: characterset to use
    :return: random string of characters
    reference: http://stackoverflow.com/questions/2257441/random-string-generation-
                                                        with-upper-case-letters-and-digits-in-python
    '''
    return ''.join(random.choice(chars) for _ in range(size))

def haswildcard(domain, soa):
    '''
    Function that will generate random sub-domains and perform lookups. Successful responses indicate a *.domain.tld
    record is in place - which will make dns enumeration slightly less valuable.
    :param domain: the domain to test
    :return: boolean - True: has wildcard  False: no wildcard detected


    '''

    #perform 3 tests - if any result in a valid record, return true
    for i in range(3):
        sub = subdomaingenerator() + "." + domain
        #print "Debug: random sub: " + sub  # debug string
        result = domainLookup(sub, soa)
        #print "Debug: result: " + result  # debug string
        if result != 'Not Found':
            return True

    return False


def bruteList(args):
    '''

    :param args: list of all command-line arguments
    Requirement: at a minimum domain and wordlist must be supplied
    :
    '''

    if not args.wordlist:
        print "Error: No wordlist specified. Please use --wordlist"
        sys.exit(1)

    if args.verbose:
        print "Debug: Domain specified: " + args.domain
        print "Debug: Wordlist specified: " + args.wordlist

    rootlist = list_all_domains(args.domain)
    sublist = list_all_domains(args.wordlist)

    if args.verbose:
        print "Debug: Domain(s): " + str(rootlist)
        print "Debug: Sub-domains: " + str(sublist)

    #loop through root domain list (--domain) and for each sub-domain look for valid A records
    for root in rootlist:
        resultDict = {}

        soa = findSOA(root)  # find SOA for root domain
        print root.upper() + " SOA is: " + soa

        rootrecord = domainLookup(root, soa)  # find A record for root domain - use SOA name server if possible
        print root.upper() + " address: " + rootrecord
        resultDict[root] = rootrecord

        if args.nowildcard:
            wildcard = False
        else:
            wildcard = haswildcard(root, soa)  # check for wildcard A record

        if wildcard:
            print "[+] WARNING: Wildcard record found: *." + root
            print "[+] Only displaying results with A records different from " + root

        for sub in sublist:
            subdomain = sub + "." + root
            subrecord = domainLookup(sub + "." + root, soa)
            if wildcard:
                if subrecord != rootrecord:
                    print "\t" + sub.lower() + "." + root.lower() + " record " + subrecord
                    resultDict[subdomain] = subrecord
            elif subrecord != "Not Found":
                print "\t" + sub.lower() + "." + root.lower() + " record " + subrecord
                resultDict[subdomain] = subrecord

        print "\n"






def bruteReverse(args):
    '''

    :param args: Contains list of command-line arguments
    :iterate through list of hosts in the IPNetwork (args.CIDR) and perform a reverse-lookup using the 'host' command
    : sub-domains will be output to a text file and displayed on the screen.
    '''

    ipnet = args.CIDR

    ip = IPNetwork(ipnet)
    f = open("dnsenumResults.txt", 'w')
    for addr in ip:

        output = execute("host " + str(addr))

        if "domain name pointer" in output:
            if not args.verify:  #The user does not wish to verify connectivity
                display = str(addr) + ": " + output.split()[4] + " Unverified"
            elif verifyDomain(): #The user requested a connectivity check
                display = str(addr) + ": " + output.split()[4] + " Verified"

            #Record result
            if args.verbose:
                print display
            f.write(display + "\n")

    f.close()




def main(argv):

    parser = argparse.ArgumentParser(description="Enumerate hosts through DNS", add_help=True)

    parser.add_argument("--CIDR",
                        help="Specify CIDR range (e.g 192.168.1.0/24)",
                        metavar="IP/MASK",
                        required=False)
    parser.add_argument("--domain",
                        help="Enumerate the specified domain or list of domains",
                        metavar="DOM.TLD or FILE",
                        required=False)
    parser.add_argument("--wordlist",
                        help="Brute-force domains based on predefined list",
                        metavar="FILE",
                        required=False)
    parser.add_argument("--nowildcard",
                        help="Disable the wildcard record test",
                        action="store_true",
                        required=False)
    parser.add_argument("--verify",
                        help="Perform connectivity test for each domain Warning:"
                             " Setting this flag will cause traffic to be sent to "
                             "the target domain(s)",
                        action="store_true",
                        required=False)
    parser.add_argument("-v", "--verbose",
                        help="Displays additional output",
                        action="store_true",
                        required=False)


    args = parser.parse_args()

    if args.verbose:
        print "-v flag set. Debugging on.\n"

    if args.CIDR:
        bruteReverse(args)

    if args.domain:
        bruteList(args)


main(sys.argv[1:])











