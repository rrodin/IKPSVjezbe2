#!/usr/bin/env python
# -*- coding: utf-8 -*-

# dohvacanje vanjskih funkcija
from openstack_api_utils import get_auth_token, get_endpoint
import json
import requests

# dohvacanje auth tokena pomocu vanjske funkcije
auth_token = get_auth_token()

# dohvacanje url-a glance servisa
glance_endpoint = get_endpoint("glance", auth_token)

# trazenje unosa od korisnika
image_name = raw_input("\nEnter new image name: ")
image_path = raw_input("\nEnter image file location: ")

# osnovni podaci koji su potrebni za pokretanje slike
data = {
    "container_format": "bare",
    "disk_format": "qcow2",
    "name": image_name
}


# zaglavlje u kojem se salje auth token i u kojem su formatu podaci koji se salju 
headers={
    'X-Auth-Token': auth_token,
    "Content-Type": "application/json"
}

# slanje zahtjeva glance serivus da kreira novu sliku
r = requests.post(glance_endpoint + "/v2/images", headers=headers, data=json.dumps(data))
print "Creating image..."

# pretvorba rezultata u json format
results_json = r.json()
# dohvat ID-a kreirane slike kako bi joj mogli pridruziti datoteku koja sadrzi sliku
image_id = results_json["id"]

# otvaranje datoteke koja sadrzi sliku
data = open(image_path, 'rb').read()

# novo zaglavljalje koje je potrebno za slanje binarne slike
headers={
    'X-Auth-Token': auth_token,
    "Content-Type": "application/octet-stream"
}

# konacno slanje zahtjeva da se postojecoj slici doda binarna datoteka koju je korisnik unio
r = requests.put(glance_endpoint + "/v2/images/" + image_id + "/file", headers=headers, data=data)
if r.status_code == 204
	# ispis da je proces zavrsen
	print "Image Created!"
else:
	print "Image creation failed"

