__author__ = 'liteman'

from netaddr import *
import argparse
import sys
import subprocess

def verifyDomain():
    '''
    #TODO -- perform some type of connectivity test to identify valid hosts
    :return:
    '''

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
        cmd = subprocess.Popen("host " + str(addr), shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = cmd.stdout.readline().decode("ASCII").rstrip()

        if "domain name pointer" in output:
            if not args.VERIFY:  #The user does not wish to verify connectivity
                display = str(addr) + ": " + output.split()[4] + " Unverified"
            elif verifyDomain(): #The user requested a connectivity check
                display = str(addr) + ": " + output.split()[4] + " Verified"

            #Record result
            if args.VERBOSE:
                print display
            f.write(display + "\n")

    f.close()




def main(argv):

    parser = argparse.ArgumentParser(description="Testing the netaddr library to "
                                                 "manipulate IP addresses", add_help=True)

    parser.add_argument("--CIDR",
                        help="Specify CIDR range (e.g 192.168.1.0/24)",
                        metavar="IP/MASK",
                        required=False)
    parser.add_argument("--domain",
                        help="Domain to enumerate (e.g google.com",
                        metavar="DOM.TLD",
                        required=False)
    parser.add_argument("--domlist",
                        help="Enumerate the specified list of domains",
                        metavar="FILE",
                        required=False)
    parser.add_argument("--wordlist",
                        help="Brute-force domains based on predefined list",
                        metavar="FILE",
                        required=False)
    parser.add_argument("--verify",
                        help="Perform connectivity test for each domain Warning:"
                             " Setting this flag will cause traffic to be sent to "
                             "the target domain(s)",
                        action="store_true",
                        required=False)
    parser.add_argument("-v", "--VERBOSE",
                        help="Displays additional output",
                        action="store_true",
                        required=False)


    args = parser.parse_args()

    if args.CIDR:
        bruteReverse(args)




main(sys.argv[1:])











