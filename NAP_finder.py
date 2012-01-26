#! /usr/bin/python
# sudo apt-get install python-bluez
# import bluetooth
# Author: Max Sobell, Intrepidus Group
# Date: 1/26/2011
import urllib
import subprocess
import sys

IEEE_SITE = "http://standards.ieee.org/develop/regauth/oui/oui.txt"

# print "Looking at nearby devices..."

# nearby_devices = bluetooth.discover_devices( lookup_names=True )
# for d in nearby_devices:
#     try:
#         print "Found device",d[0],d[1]
#     except:
#         print "Something is broken."

print """
Bluetooth address breakdown:
[XX:XX:][XX:][XX:XX:XX]
[ NAP  ][UAP][   LAP  ]
[XX:XX:XX:  ] -> Available online
             [XX:XX:XX] -> Sniffable via Ubertooth One i.e. ubertooth-lap
        [XX:]-> Can be determined via checksums i.e. ubertooth-uap -l <LAP>

If you provide UAP and LAP, we can limit the search space by matching the UAP
with the database online.
"""

LAP = raw_input("Enter UAP + LAP or LAP\nex. 01:23:45:67:89:10, enter 45678910 or 678910\n")
MANU = raw_input("Enter device manufacturer ex. Cisco, Motorola, RIM\n").upper()

print "[+] Retrieving IEEE database"

f = urllib.urlopen( IEEE_SITE )
s = f.read()
f.close()

MANU_6 = []
DB = s.split('\n')
for item in DB:
    if MANU in item.upper() and 'base 16' in item:
        MANU_6.append(item[:6])

print "[+] Retrieved DB"

small_space = []
large_space = []

if len(LAP) > 6: # We have LAP + UAP
    for front_6 in MANU_6:
        if front_6[4:].upper() == LAP[:2].upper():
            print "[+] Found matching UAP, narrowing search"
            a = front_6[:4].upper() + LAP.upper()
            small_space.append( a[0:2]+":"+a[2:4]+":"+a[4:6]+":"+a[6:8]+":"+a[8:10]+":"+a[10:12] )
elif len(LAP) == 6:
    for front_6 in MANU_6:
        a = front_6.upper() + LAP.upper()
        large_space.append( a[0:2]+":"+a[2:4]+":"+a[4:6]+":"+a[6:8]+":"+a[8:10]+":"+a[10:12] )
else:
    print "[-] Please enter at least 6 hex characters with no colons."
    sys.exit(1)

device_found = False

def find_device( search_space ):
    print "[+] Trying",len( search_space ),"addresses" # whatever, grammar nazi.
    for a in search_space:
        print "\t",a,"\t",
        p = subprocess.Popen(["sdptool","browse",a],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        ret = None
        while ret is None:
            ret = p.communicate()
        if 'Browsing' in ret[0]:
            print "Device found!"
            return True
        else:
            print "No response"

if len(small_space) > 0:
    device_found = find_device( small_space )
if not device_found:
    if len( LAP ) > 6:
        print "[+] No response from limited space, possible UAP mismatch."
    print "[+] Trying larger address space."
    device_found = find_device( large_space )
