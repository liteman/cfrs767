domainenum.py
=======

Author: Kevin Romano
CFRS767

Requirement: Write a script which enumerates valid DNS host names from a given domain
                The script must accept a command-line argument specifying a text file with a list of domains
                The script must accept a command-line argument specifying a text file with a list of sub-domains

=======
HELP Section

./domainenum.py -h
usage: domainenum.py [-h] [--CIDR IP/MASK] [--domain DOM.TLD or FILE]
                     [--wordlist FILE] [--nowildcard] [--verify] [-v]

Enumerate hosts through DNS

optional arguments:
  -h, --help            show this help message and exit
  --CIDR IP/MASK        Specify CIDR range (e.g 192.168.1.0/24)
  --domain DOM.TLD or FILE
                        Enumerate the specified domain or list of domains
  --wordlist FILE       Brute-force domains based on predefined list
  --nowildcard          Disable the wildcard record test
  -v, --verbose         Displays additional output


=======
Sample output one:

./domainenum.py --domain domains.txt --wordlist sublist.txt

GMU.EDU SOA is: magda.gmu.edu
GMU.EDU address: 129.174.1.38
	kerberos.gmu.edu record 129.174.0.251
	kerberos1.gmu.edu record 129.174.0.251
	kerberos2.gmu.edu record 129.174.16.14
	kerberos3.gmu.edu record 129.174.0.247
	mail.gmu.edu record 129.174.0.51
	www.gmu.edu record 129.174.1.38
	webmail.gmu.edu record 129.174.0.51
	ftp.gmu.edu record 129.174.1.13
	vpn.gmu.edu record 129.174.3.22

Sample output two:

BLUEMANTLETECH.COM SOA is:
BLUEMANTLETECH.COM address: 206.188.193.121
[+] WARNING: Wildcard record found: *.bluemantletech.com
[+] Only displaying results with A records different from bluemantletech.com
	mail.bluemantletech.com record 50.245.245.165
	vpn.bluemantletech.com record 50.245.245.165

=======
References

http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python