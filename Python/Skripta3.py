#!/usr/bin/env python
# -*- coding: utf-8 -*-

# dohvacanje vanjskih funkcija i knjiznica funkcija
from openstack_api_utils import get_auth_token, get_endpoint
import json
import requests

# dohvacanje autentifikacijskog tokena pomocu metode iz skripte openstack_api_utils.py
auth_token = get_auth_token()

#dohvacanje URL-a (endpointa) servisa neutron kojem ce se proslijediti zahtjev za kreiranje mreze
neutron_endpoint = get_endpoint("neutron", auth_token)

#trazimo od korisnika unos imena nove mreze koju cemo kreirati
network_name = raw_input("\nEnter new network name: ")


#definicija zaglavlja POST zahtjeva
headers={
    'X-Auth-Token': auth_token,
    "Content-Type": "application/json"
}

#varijabla data kojom se prenose podaci, tocnije ime mreze koju cemo kreirati
data = {
    "network": {"name": network_name}
}

#slanje post zahtjeva sa specificiranim zaglavljima i podacima na URL (endpoint) neutrona
# te primanje odgovora (response) u varijablu r
r = requests.post(neutron_endpoint + "/v2.0/networks", headers=headers, data=json.dumps(data))

#provjera je li mreza uspjesno kreirana,  status code 201 oznacava uspjesnu kreaciju
if r.status_code != 201:
    sys.exit("Network creation error!")
else:
    #pretvaranje odgovora u json format
    results_json = r.json() 
    #iscitavanje ID-a novokreirane mreze iz odgovora koji smo dobili od servisa neutron
    net_dict = results_json['network']
    network_id = net_dict['id']
    #ispis potvrde kreacije i ID-a novokreirane mreze
    print('Network %s created' % network_id)





#creating subnets


#trazimo od korisnika unos imena nove podmreze koju cemo kreirati
subnet_name = raw_input("\nEnter new subnet name: ")

#trazimo od korisnika unos cidr-a (Classless Inter-Domain Routing) nove podmreze koju cemo kreirati
subnet_cidr = raw_input("\nEnter subnet cidr: ")

#varijabla data kojom se prenose podaci, tocnije ime podmreze koju cemo kreirati
#cidr podmreze, verzija ip adrese, ID mreze kojoj se dodjeljuje podmreza
data = {
     "subnet":{"name":subnet_name,
               "cidr":subnet_cidr,
               "ip_version":4,
               "network_id":network_id}
}

#definicija zaglavlja POST zahtjeva
headers={
    'X-Auth-Token': auth_token,
    "Content-Type": "application/json"
}

#slanje post zahtjeva sa specificiranim zaglavljima i podacima na URL (endpoint) neutrona
# te primanje odgovora (response) u varijablu r
r = requests.post(neutron_endpoint + "/v2.0/subnets", headers=headers, data=json.dumps(data))

#provjera je li podmreza uspjesno kreirana,  status code 201 oznacava uspjesnu kreaciju
if r.status_code != 201:
    sys.exit("Subnet creation error!")
else:
    #pretvaranje odgovora u json format
    results_json = r.json()
    #iscitavanje imena novokreirane podmreze iz odgovora koji smo dobili od servisa neutron
    subnet_dict = results_json['subnet']
    subnet_name = subnet_dict['name']
    #ispis potvrde kreacije i naziva novokreirane podmreze
    print('Subnet %s created' % subnet_name)


