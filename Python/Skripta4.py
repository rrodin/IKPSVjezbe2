#!/usr/bin/env python
# -*- coding: utf-8 -*-

#dohvacanje vanjskih funkcija i knjiznica funkcija
import requests
import json
from openstack_api_utils import get_auth_token, get_endpoint
import sys

# dohvacanje tokena za autentifikaciju korsnika
auth_token = get_auth_token()
headers = {'X-Auth-Token': auth_token}

# dohvacanje URL-a(endpointa) neutron servisa
neutron_endpoint = get_endpoint("neutron", auth_token)

# trazi unos naziva mreze od korisnika
name = raw_input('\nEnter exact network name: ')

# dohvaca id mreze cije ime je korisnik unio
r = requests.get(neutron_endpoint + "/v2.0/networks?name=" + name + "&fields=id", headers=headers)
print("Finding network...")
print(r.status_code, r.reason)
results_json = r.json()

# provjera ima li rezultata pretrage, ako ih nema rezults_json ce biti prazan (len ce biti nula)
#ako rezultata pretrage postoji spremamo ga u varijablu network_id 
if len(results_json["networks"]) > 0:
	net_dict = results_json['networks'][0]
	network_id = net_dict['id']
	print('Found network %s with id %s' % (name, network_id))
else:
   	sys.exit("Network not found.")

# dohvacanje id-ja javne mreze te id-ja subneta javne mreze
r = requests.get(neutron_endpoint + "/v2.0/networks?name=admin_floating_net", headers=headers)
print(r.status_code, r.reason)
results_json = r.json()

# provjera ima li rezultata pretrage, ako ih nema rezults_json ce biti prazan (len ce biti nula) 
#ako ima rezultata pretrage spremamo ih u varijable public_network_id i public_subnet_id
if len(results_json["networks"]) > 0:
	net_dict = results_json['networks'][0]
	public_network_id = net_dict['id']
	public_subnet_id = net_dict['subnets'][0]
	
	print('Found public network with id %s' %  public_network_id)
	print ('Found public subnet id %s' % public_subnet_id)
else:
	sys.exit("Public network not found.")

#trazimo od korisnika unos imena rutera koji cemo kreirati
router_name = raw_input('\nEnter new router name: ')

#specifikacija zaglavlja
headers = {
	'X-Auth-Token': auth_token,
	'Content-Type': 'application/json'
}

#specifikacija podataka o novom ruteru, naziv rutera, id javne mreze, fiksna javna adresa
#id podmreze
data = {
	"router": {
		"name": router_name,
		"external_gateway_info": {
            "network_id": public_network_id,
            "enable_snat": "true",
            "external_fixed_ips": [
                {
                    "ip_address": "10.30.2.171",
                    "subnet_id": public_subnet_id
                }
            ]
        },
		"admin_state_up": "true"
	}
}

#slanje post zahtjva za kreaciju novog rutera servisu neutron
r = requests.post(neutron_endpoint + "/v2.0/routers", headers=headers, data=json.dumps(data))
print "Creating router..."
# ispis statusnog koda o kreaciji te spremanje ID-ja rutera iz odgovora dobivenog od neutrona 
print(r.status_code, r.reason)
results_json = r.json()
router_id = results_json["router"]["id"]


#specifikacija podataka za kreiranje novog porta
#id privatne mreze, fiksna ip adresa
data = {
		'port': {
			'admin_state_up': True,
			'network_id': network_id,
			'fixed_ips': [{"ip_address": "10.20.0.126"}]
		}
}

#slanje post zahtjeva za stvaranje porta servisu neutron
r = requests.post(neutron_endpoint + "/v2.0/ports", headers=headers, data=json.dumps(data))
print "Creating port..."
print(r.status_code, r.reason)
results_json = r.json()
#provjera uspjesnosti kreacije porta i ispis poruke
#dohvacanje id-ja novokreiranog porta koji ce se kasnije dodijeliti ruteru
if len(results_json["port"]) > 0:
	net_dict = results_json['port']
	port_id = net_dict['id']
	print('Created port %s with id %s' % (name, port_id))







#specifikacija id-ja porta koji dodjeljujemo ruteru
data = {
		"port_id":port_id
}

#slanje put zahtjeva za dodavanje porta ruteru
r = requests.put(neutron_endpoint + "/v2.0/routers/"+router_id+"/add_router_interface", headers=headers, data=json.dumps(data))
print "Adding interface to router ..."

#ispis statusnog koda o dodavanju porta ruteru
print(r.status_code, r.reason)
results_json = r.json()
print json.dumps(results_json, indent=4)


