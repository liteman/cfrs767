#!/usr/bin/python
__author__ = 'liteman'


from netaddr import *
import argparse
import sys
import os
import string
import random
import time
import dns.resolver

random.seed(time.localtime())

servlist = ["4.2.2.2",  # level 3
            "8.8.8.8",  # google
            "8.8.4.4",  # google
            "208.67.222.222",  # OpenDNS Home
            "195.46.39.39",  # SafeDNS
            "64.7.11.2",  # megapath East Coast Primary
            "208.67.220.220"]  # OpenDNS

rezolver = dns.resolver.Resolver()  # create a resolver object
rezolver.nameservers = servlist     # specify nameserver to use


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

'''
def execute(cmdstr):

    cmd = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cmd.stdout.readline().decode("ASCII").rstrip()
'''

def domainLookup(domain):
    global servlist
    global rezolver

    # Resolver tries each nameserver in order. Shuffle server list in order to randomize queries
    # This will *hopefully* avoid hitting rate-limits
    random.shuffle(servlist)
    rezolver.nameservers = servlist

    #find A record with command: host <domain> <soa server> | grep "has address"
    #Sample output: gmu.edu has address 129.174.1.38
    #arecord = execute("host " + domain + " " + server + " | grep 'has address'")
    try:
        #print "Debug using server: " + servlist[0]
        answer = rezolver.query(domain)
        arecord = str(answer.rrset).split()[4].rstrip('.')
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoAnswer) as e:
        arecord = ''  #TODO timeout and NoAnswer should be handled better (query a different server in the list)

    if arecord == '':
        return "Not Found"
    else:
        return arecord

def findSOA(domain):
    global servlist

    #find SOA for root
    try:
        answer = rezolver.query(domain, rdtype="SOA")
        soa = str(answer.rrset).split()[4].rstrip('.')
    except dns.resolver.Timeout, dns.resolver.NXDOMAIN:
        soa = ''

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

def haswildcard(domain):
    '''
    Function that will generate random sub-domains and perform lookups. Successful
    responses indicate a *.domain.tld record is in place - which will cloud
    enumeration results.
    :param domain: the domain to test
    :return: boolean - True: has wildcard  False: no wildcard detected
    '''

    counter = 0
    wildcardlist = []
    for i in range(3):
        sub = subdomaingenerator() + "." + domain
        result = domainLookup(sub)
        if result != 'Not Found':
            counter += 1
            wildcardlist.append(sub + ": " + result)

    if counter > 1:  # 2 out of 3 successful tests
        print "Wildcard Tests: "
        for dom in wildcardlist:  # print the successful wildcard queries
            print "\t" + dom
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

        soa = findSOA(root)  # find SOA for root domain
        print root.upper() + " SOA is: " + soa

        rootrecord = domainLookup(root)  # find A record for root domain - use SOA name server if possible
        print root.upper() + " address: " + rootrecord

        if args.nowildcard:
            wildcard = False
        else:
            wildcard = haswildcard(root)  # check for wildcard A record

        if wildcard:
            print "[+] WARNING: Wildcard record found: *." + root
            print "[+] Only displaying results with A records different from " + root

        for sub in sublist:
            num = random.choice(range(len(servlist)))  # pick a random number as a selector for a server from servlist[]
            #print "DEBUG: Random number: " + str(num)
            #print "DEBUG: Using server: " + servlist[num]
            subdomain = sub + "." + root
            subrecord = domainLookup(subdomain)  # perform lookup using specified server
            if wildcard:
                if subrecord != rootrecord:
                    print "\t" + sub.lower() + "." + root.lower() + " record " + subrecord
            elif subrecord != "Not Found":
                print "\t" + sub.lower() + "." + root.lower() + " record " + subrecord


        print "\n"






def bruteReverse(args):
    global servlist
    '''

    :param args: Contains list of command-line arguments
    :iterate through list of hosts in the IPNetwork (args.CIDR) and perform a reverse-lookup using the 'host' command
    : sub-domains will be output to a text file and displayed on the screen.
    '''

    ipnet = args.CIDR

    ip = IPNetwork(ipnet)
    f = open("dnsenumResults.txt", 'w')
    for addr in ip:
        random.shuffle(servlist)
        revaddr = dns.reversename.from_address(str(addr))
        #output = execute("host " + str(addr))
        try:
            answer = rezolver.query(revaddr, "PTR")
            stranswer = str(answer.rrset).split()[4].rstrip('.')
        except dns.resolver.NXDOMAIN:
            continue

        display = str(addr) + ": " + stranswer

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











