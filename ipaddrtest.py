__author__ = 'liteman'

''' Testing the netaddr library
'''

from netaddr import *
import argparse
import sys

def testip(ipnet):
    ip = IPNetwork(ipnet)

    for addr in ip:
        print addr




def main(argv):

    parser = argparse.ArgumentParser(description="Testing the netaddr library to "
                                                 "manipulate IP addresses", add_help=True)

    parser.add_argument("--CIDR",
                        help="Specify CIDR range (e.g 192.168.1.0/24)",
                        metavar="IP/MASK",
                        required=False)


    args = parser.parse_args()

    if args.CIDR:
        testip(args.CIDR)




main(sys.argv[1:])