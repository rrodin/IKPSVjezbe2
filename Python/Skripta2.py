#!/usr/bin/env python
# -*- coding: utf-8 -*-

# knjiznice koje su potrebne za rad skripte
# authentication je py modul koji smo kreirali da provodi autentikaciju
from authentication import get_auth_token, get_endpoint
# knjiznica za slanje http zahtjeva 
import requests
# knjiznica za rad s json datotekama
import json

# dohvaca auth token pomocu funkcije iz authenticate.py
# i sprema ga u varijablu auth_token
auth_token = get_auth_token()
# dohvaca se URL glance servssa pomocu funkcije pomocne knjiznice
glance_endpoint = get_endpoint("glance", auth_token)
# ispis teksta na terminal
print "List of all images by name and size:"

# kreairanje zaglavlja zahtjeva, zaglavlje mora sadrzavati token u ovom obliku
headers = {'X-Auth-Token': auth_token}
# slanje GET zahtjeva na url od glance servisa sa ukljucenim zaglavljem
r = requests.get(glance_endpoint + "/v2/images", headers=headers)
# ispis koda koji smo dobili kao povratnu informaciju
print(r.status_code, r.reason)

# pretvaranje rezultata u json format
json_data = r.json()
# petlja u kojoj se iterira po svim slikama koje se dobiju
for image in json_data["images"]:
	# ispis podataka (ime i velicina) pojedine slike uz formatiranje
    print repr(image["name"]).ljust(50) + repr(image["size"]).rjust(15)

# trazenje unosa preko terminala od strane korisnika
name = raw_input('\nSearch for image by name: ')

# pitaj korisnika za unos imena po kojem se pretrazuje
print('\nLooking for %s...\n' % name)


# dohvacanje specificne OS slike putem njezinog imena
# salje se GET zahtjev s query parametrom unesene rijeci
r = requests.get(glance_endpoint + "/v2/images?name=" + name, headers=headers)
# ponovno se rezultat pretvara u json format
results_json = r.json()
# iz rezultata se dohvaca polje svih slika koje je glance servis vratio 
images = results_json["images"]
# provjera postoji li rezultat pretrage
if images:
    # ako postoji za svaku sliku ispis njen ID
    for image in images:
        print('Images found, id is:%s' % image["id"])
else:
    # ako upit ne vrati nikakav rezultat
    print "Image Not Found"
