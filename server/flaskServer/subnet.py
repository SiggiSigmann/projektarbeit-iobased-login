import csv
from ipaddress import IPv4Address
import sys
import requests
import json

#get infromation about subnet form csv file
#source: #https://www.nirsoft.net/countryip/de.html
class Subnet():
    def __init__(self, path):
        self.path = path
        self._loadFile()

    #cload csv and split entries
    #store data from file in self.data
    def _loadFile(self):
        self.data = []
        with open(self.path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            
            
            for row in csv_reader:
                entry = []
                i = 0
                for part in row:
                    if i == 0:
                        entry.append(IPv4Address(part))
                    elif i == 1:
                        entry.append(IPv4Address(part))
                    elif i == 2:
                        entry.append(int(part))
                    else:
                        entry.append(part)

                    i+=1

                #manuly edited (m.e.) ISP
                if len(entry) == 5:
                    if entry[0] == IPv4Address("188.1.0.0"):
                        entry[4] = "Deutschen Forschungsnetze - m.e."
                    if entry[0] == IPv4Address("141.70.0.0"):
                        entry[4] = "BelWue - m.e."



                self.data.append(entry)

    #get informations about ip addresses based on csv file loaded before
    def find_Ownder(self, ip):
        ipAddress = IPv4Address(ip)
        for i in self.data:
            if (i[0] >= ipAddress) or (ipAddress <= i[1]):
                if(i[4] == ''):
                    return str(i[0]) +" "+ str(i[1])
                return i[4]
        return "not found"

    def get_ip_location(self, ip):
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}")
            return [str(r.json().get('country', "-")), str(r.json().get('region', "-")),str(r.json().get('city', "-"))]
        except:
            return["-","-","-"]



        


