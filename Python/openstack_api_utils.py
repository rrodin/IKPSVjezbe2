#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ukljucivanje potrebnih knjiznica knjiznica za slanje http zahtjeva
import requests
# knjiznica za rad s json formatom
import json


# ovo su podaci koji su potrebni Identity servisu da nam izda token najvaznije je 
# dobro zadati lozinku i ime treba paziti da je ime odabranog projekta tocno
data = {
 "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "admin",
          "domain": {"id": "default"},
          "password": "AkX3UrB9"
        }
      }
    },
    "scope": {
      "project": {
        "name": "admin",
        "domain": {"id": "default"}
      }
    }
  }
}

# funkcija koja se poziva na pocetku drugih skripti kako bi se izvrsila autentikacija
# i kako bi se dobio auth token koji je potreban za daljni rad s Openstack API-jem 
def get_auth_token():
    # definira se zaglavlje zahtjeva, podatci se salje u obliku json datoteke pa je 
    # onda potrebno u zaglavlju Content-Type postaviti na slijedecu vrijednost
    headers = {'Content-Type': 'application/json'}
    # salje se POST zahtjev sa gore definiranim podacima na Identity servis koji je zaduzen za autentikaciju	 
    r = requests.post("http://10.30.1.2:5000/v3/auth/tokens", headers=headers, data=json.dumps(data))
    print("Creating new auth token...")
    # ispis vracenog statusnog koda kao povratna informacija korisniku da je sve u redu
    print(r.status_code, r.reason)
    # kao sto je navedeno u dokumentaciji uspjesni zahtjev vraca token u zaglavlju
    # ovdje se taj token vraca tamo gdje se funkcija pozvala
    return r.headers.get("x-subject-token")

# funkcija koja dohvaca endpoint (URL) na kojoj se nalazi pojedini servis
# kao argument prima ime tog servisa i auth token
def get_endpoint(service_name, auth_token):
    # u zaglavlju se salje auth token  
    headers = {'X-Auth-Token': auth_token}
    # kao sto pise u dokumentaciji salje se GET zahtjev na navedeni url
    r = requests.get("http://10.30.1.2:5000/v3/auth/catalog", headers=headers)
    # pretvaranje rezultata u json format
    results_json = r.json()

    # iteriranje po json datoteci po svakom izlistanom servisu da bi se izvukao URL modula cije je ime zadano kao argument
    for catalog_entry in results_json["catalog"]:
        # if uvjet usporedjuje odgovara li ime servisa onome iz argumenta
        if catalog_entry["name"] == service_name:
            # ako odgovara potrebno je proci kroz sva njegova sucelja i pronaci ono koje je javno
            for endpoint in catalog_entry["endpoints"]:
                if endpoint["interface"] == "public":
                    # kada smo nasli njegovo javno sucelje spremimo njegov url u varijablu koju na kraju vracamo
                    service_endpoint = endpoint["url"]
    return service_endpoint