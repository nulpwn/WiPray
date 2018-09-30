# WiPray
Wifi Password Spray in EAP-MSCHAPv2 networks.

Blog: https://labs.pwn.pt/articles/wipray/

# Requirements
pip install wpa_supplicant

# Usage
Running the tool:
  python wipray.py [options]
 
Typical Usage Example:
  python wipray.py --user-file users_all.txt --password Password123 --domain MyDomain --ssid MyWifiSSID  

Options:
  -h, --help            show this help message and exit
  --user-file USER_FILE
                        User file containing a user in each line
  --password PASSWORD   The password to be used in the spray
  --domain DOMAIN       The user's domain
  --ssid SSID           The ssid to use
  --key-management KEY_MANAGEMENT
                        key_mgmt value
  --eap EAP             eap value
  --phase1 PHASE1       peapver=0
  --phase2 PHASE2       auth=MSCHAPV2
  --wpa_supplicant_log WPA_SUPPLICANT_LOG
                        Location of the log file containing the logs from
                        wpa_supplicant
  --interface INTERFACE
                        Interface to use

# License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
