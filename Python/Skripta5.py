
import requests
import json
from openstack_api_utils import get_auth_token, get_endpoint
import sys

# dohvacanje tokena za autentifikaciju korisnika sa pomocnom funkcijom
auth_token = get_auth_token()
# dodavanje auth tokena u zaglavlje koje ce se poslati
headers = {'X-Auth-Token': auth_token}

# iduce tri linije su pomocne funkcije za dohvacanje URL-a (endpointa) svih potrebnih servisa
# ove funkcije su uvezene iz pomocne knjiznice
nova_endpoint = get_endpoint("nova", auth_token)
glance_endpoint = get_endpoint("glance", auth_token)
neutron_endpoint = get_endpoint("neutron", auth_token)

print "List of all images by name and size:"

# slanje zahtjeva na glance url da se dohvate sve slike
r = requests.get(glance_endpoint + "/v2/images", headers=headers)
# ispis statusnog koda koji je glance servis vratio
print(r.status_code, r.reason)
# pretvaranje rezultata u json format
json_data = r.json()

# ispis svih slika koje smo dobili
for image in json_data["images"]:
    # ljust i rjust poravnavaju ispis u lijevo i u desno kako bi 
    # ga korisnik mogao lakse citati
    print repr(image["name"]).ljust(50) + repr(image["size"]).rjust(15)

# trazenje unosa preko terminala od strane korisnika
name = raw_input('\nEnter image name to be used for the instance: ')

# pitaj korisnika za unos imena po kojem se pretrazuje
print('\nLooking for %s...\n' % name)

# dohvacanje specificne slike putem njezinog imena koje je korisnik unio
r = requests.get(glance_endpoint+"/v2/images?name=" + name, headers=headers)
# pretvaranje rezultata u json format
results_json = r.json()
images = results_json["images"]
# provjera ima li rezultata naseg upita
if images:
    # ako ima ispisi sve slike koje su proandjene
    for image in images:
        print('Images found, id is:%s' % image["id"])
        image_id = image["id"]
# ako nema ispisi poruku i zavrsi izvrsavanje programa
else:
    # izvrsava se ukoliko nema rezultata pretrage
    sys.exit("Image Not Found")

# trazi unos naziva mreze od korisnika
name = raw_input('\nEnter exact network name: ')

# dohvaca id mreze cije ime je korisnik unio
r = requests.get(neutron_endpoint + "/v2.0/networks?name=" + name + "&fields=id", headers=headers)
print("Finding network...")
# ispis statusnog koda koji nam vrati neutron servis
print(r.status_code, r.reason)
results_json = r.json()

# provjera ima li rezultata pretrage, ako ih nema rezults_json ce biti prazan (len ce biti nula)
if len(results_json["networks"]) > 0:
    # ako postoje rezultati pretrage dohvati prvi i spremi ga u rjecnik (dictionary)
    net_dict = results_json['networks'][0]
    network_id = net_dict['id']
    # ispis podataka o pronadjenoj mrezi
    print('Found network %s with id %s' % (name, network_id))
else:
    # u slucaju da nema rezultata pretrage ispisuje se odgovarajuca poruka i zavrsava se program
    sys.exit("Network not found.")


# slanje GET zahtjeva za popisom dostupnih flavora
r = requests.get(nova_endpoint + "/flavors", headers=headers)
print(r.status_code, r.reason)
json_data = r.json()

# ispis liste svih dostupnih flavora sa formatiranje da bi bilo citljivije
for flavor in json_data["flavors"]:
    print repr(flavor["id"]).ljust(40) + repr(flavor["name"]).rjust(15)


# trazenje unosa od korisnika
flavor_id = raw_input('\nEnter flavor ID: ')
# slanje GET zahtjeva da se dohvate podaci o flavoru sa odredjenim ID-om
r = requests.get(nova_endpoint + "/flavors/" + flavor_id, headers=headers)
print(r.status_code, r.reason)
if r.status_code != 200:
    # ako se dobije statusni kod razlicit od 200 (OK) znaci da se flavor nije
    # uspio dohvatiti te se ispisuje poruka i zavrsava program
    sys.exit("Invalid flavor id")

# trazenje unosa od korisnika, ako unese prazan string onda ga se pita da unese opet
instance_name = raw_input('\nEnter name for new instance: ')
while instance_name == "":
    print "Name cannot be empty\n"
    instance_name = raw_input('\nEnter name for new instance: ')

# podaci za kreiranje nove instance, sastoje se od podataka koje je korisnik unio
data = {
        "server": {
                "name": instance_name,
                "imageRef": image_id,
                "flavorRef": flavor_id,
                "networks": [
                    {
                        "uuid": network_id
                    }
                ],
                "availability_zone": "nova",
                "security_groups": [
                    {
                        "name": "default"
                    }
                ]
            }
}
# u zaglavlje je potrebno dodatio Content Type jer se salju 
# podaci pa je potrebno definirati kojeg su tipa
headers = {
    'X-Auth-Token': auth_token,
    'Content-Type': 'application/json'
}

# slanje POST zahtjeva za kreiranje nove isntance sa gore definiranim podacima
# json.dumps(data) je potrebno napraviti kako bi se osiguralo da su poslani podaci 
# u json formatu
r = requests.post(nova_endpoint + "/servers", headers=headers, data=json.dumps(data))
print("Creating instace...")
print(r.status_code, r.reason)
if r.status_code != 202:
    sys.exit("Unable to create instace")
else:
    print "Instance created successfully"

# slanje zahtjeva da se izlistaju sve instance kako bi mogli vidjeti je li
# kreirana nasa nova instanca
r = requests.get(nova_endpoint + "/servers", headers=headers, data=json.dumps(data))
json_data = r.json()
for server in json_data["servers"]:
    print server["name"]
