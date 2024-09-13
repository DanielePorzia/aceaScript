import json
import requests
import time

def get_access_token():

    grant_type="password"
    client_id = "webapp-client"
    username = "service.account@apishare.cloud"
    password = "techAdmin"
    tenant = "dev"
    # URL dell'endpoint per ottenere il token di accesso
    url = f"https://nopro-api.apishare.cloud/{tenant}/realms/{tenant}/protocol/openid-connect/token"
    
    # Intestazioni della richiesta
    my_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Dati della richiesta
    data = {
        "grant_type": grant_type,
        "username": username,
        "password": password,
        "client_id": client_id
    }

    # Effettua la richiesta POST per ottenere il token
    response = requests.post(url, headers=my_headers, data=data)
    
    # Verifica se la richiesta ha avuto successo (HTTP Status 200)
    if response.status_code == 200:
        # Decodifica la risposta JSON
        token = response.json().get("access_token")
        return token
        
    else:
        # Stampa l'errore se la richiesta fallisce
        print(f"Errore nella richiesta: {response.status_code} - {response.text}")
        return None

def check_api_status():
    url = basePath + "/" + api_id + "/versions/" + version + "?scope=workspace"
    
    response = requests.get(url,headers=headers)
    
     # Verifica se la richiesta ha avuto successo (HTTP Status 200)
    if response.status_code == 200:
        # Decodifica la risposta JSON
        environmentsSize = len(response.json().get("environments"))
        status = response.json().get("status")
        status_detail = response.json().get("statusDetail")
        return environmentsSize#f"{status}, {status_detail}"
        
    else:
        # Stampa l'errore se la richiesta fallisce
        print(f"Errore nella richiesta: {response.status_code} - {response.text}")
        return None
    
def create_api(json_obj):
    global api_id
    global version
    version = json_obj["version"]
    url = basePath
    
    body = {
        "name": json_obj["name"],
        "version": json_obj["version"],
        "groupId": json_obj["groupId"],
        "apiOwner": json_obj["apiOwner"],
        "developer": json_obj["developer"],
        "producers": json_obj["producers"],
        "integrationPatternId": json_obj["integrationPatternId"],
        "description": json_obj["description"]
    }
    
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        api_id = response.json().get("apiId")

        json_obj["ApiShareId"] = api_id
        print(f"API created successfully. apiId: {api_id}")
    else:
        print(f"Failed to create API. Status Code: {response.status_code}, Response: {response.text}")

def upload_swagger(json_obj):
    url = basePath + "/" + api_id + "/versions/" + version + "/swagger"  
    
    body = {
        "fileName": json_obj["fileName"],
        "contentType": json_obj["contentType"],
        "body": json_obj["body"],
        "authorizations":json_obj["authorizationType"]
    }
    
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("Swagger uploaded successfully and set authorizationType.")
    else:
        print(f"Failed to upload Swagger. Status Code: {response.status_code}, Response: {response.text}")
        
def add_metadata():
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Save",
        "status": "Concept",
        "statusDetail": "Draft",
        "authentications": ["f36880e9-9455-477d-b37b-e62254c99eec"],
        "gateways":["e17938e6-5875-49ae-9047-a7fa4f529078"]
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("Metadata correctly added.")
    else:
        print(f"Failed to add metadata. Status Code: {response.status_code}, Response: {response.text}")
        
def propose_concept():
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Propose",
        "status": "Concept",
        "statusDetail": "Proposed"
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("Concept proposed successfully.")
    else:
        print(f"Failed to propose concept. Status Code: {response.status_code}, Response: {response.text}")

def accept_concept():
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Accept",
        "status": "In Progress",
        "statusDetail": "Draft"
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("Concept accepted successfully.")
    else:
        print(f"Failed to accept concept. Status Code: {response.status_code}, Response: {response.text}")

def request_validation():
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Request validation",
        "status": "In Progress",
        "statusDetail": "Pending for validation"
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("Validation requested successfully.")
    else:
        print(f"Failed to request validation. Status Code: {response.status_code}, Response: {response.text}")

def approve_validation():
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Approve",
        "status": "In Progress",
        "statusDetail": "Pending for publishing"
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("Validation approved successfully.")
    else:
        print(f"Failed to approve validation. Status Code: {response.status_code}, Response: {response.text}")

def publish_api_dev(json_obj):
    url = basePath + "/" + api_id + "/versions/" + version
   
    body = {
        "action": "Publish",
        "status": "In Progress",
        "statusDetail": "Publishing non production",
        "deployment": json_obj["DEV"]
    }
    
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("API published successfully in DEV environment.")
    else:
        print(f"Failed to publish API. Status Code: {response.status_code}, Response: {response.text}")
        
def publish_api_test(json_obj):
    
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Promote",
        "status": "Published",
        "statusDetail": "Promoting",
        "deployment": json_obj["TEST"]
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("API published successfully in TEST environment.")
    else:
        print(f"Failed to publish API. Status Code: {response.status_code}, Response: {response.text}")

def publish_api_preprod(json_obj):
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Promote",
        "status": "Published",
        "statusDetail": "Promoting",
        "deployment": json_obj["PREPROD"]
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("API published successfully in TEST environment.")
    else:
        print(f"Failed to publish API. Status Code: {response.status_code}, Response: {response.text}")


def ready_to_go_live(json_obj):
       
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Ready for go-live",
        "status": "Published",
        "statusDetail": "Pending for go-live",
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("API ready to go live.")
    else:
        print(f"Failed to get api ready to go live. Status Code: {response.status_code}, Response: {response.text}")

def publish_api_prod(json_obj):
    url = basePath + "/" + api_id + "/versions/" + version
    
    body = {
        "action": "Go live",
        "status": "Published",
        "statusDetail": "Going live",
        "deployment": json_obj["PROD"]
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print("API published successfully in PROD environment.")
    else:
        print(f"Failed to publish API. Status Code: {response.status_code}, Response: {response.text}")
        
        
def write_DMLmashery_api(masheryId,version,environment,environmentId):
    print(f"Writing SQL file for environment: {environment}")
    with open("DMLmashery_api.sql","r+", encoding='utf-8') as fi:
            dml = fi.read();
            riga = f"VALUES('{masheryId}', '{api_id}', current_timestamp, null, '{environmentId}', '{version}', current_timestamp),"
            fi.write(f"\n{riga}")

########################################################################################################################################################################################################################

token = get_access_token()

#turn true if preprod env exists for APIs
existsPreprodEnv=False

# Variabile globale 
api_id = None
basePath = "https://nopro-api.apishare.cloud/api-management/apis"
version = None

# Header comune per tutte le richieste
headers = {
    "Content-Type": "application/json",
    "requestId": "00000000-0000-0000-0000-000000000000",
    "sessionId": "00000000-0000-0000-0000-000000000000",
    "x-api-key": "KAtBDiOii64OfWhYFZb3w8uxS6Ud4axi8zGilMsH",
    "Authorization": f"Bearer {token}"
}

# Leggi il file JSON generato
with open("LoadThisFile.json", "r+") as f:
    data = json.load(f)

print("Creating SQL file")
with open("DMLmashery_api.sql","w") as file:
    file.write("INSERT INTO as_mashery_api(gatewayid, apiid, created, control_center_uri, environmentid, api_version, updated) ")
    print("SQL file created")

# Itera su ogni oggetto nel file JSON
for obj in data:

    print("Creating API")
    create_api(obj)
    
    print("Uploading swagger")
    upload_swagger(obj)
    
    print("Adding Meta-Data")
    add_metadata()
    
    print("Proposing Concept")
    propose_concept()
    
    print("Accepting Concept")
    accept_concept()
    
    print("Requesting Validation")
    request_validation()
    
    print("Approving Validation")
    approve_validation()
    
    environmentPublishedCount = 0
    
    print("Publishing API in DEV")
    publish_api_dev(obj)
    environmentPublishedCount = environmentPublishedCount+1
    
    time_waited =0 
    
    while time_waited < 120:
        if check_api_status()==environmentPublishedCount:
            break
        else:
            print(f"API not ready! Published in: {check_api_status()} environments instead of: {environmentPublishedCount} and time waited: {time_waited}")
            time.sleep(5)
            time_waited=time_waited + 5
            
    if time_waited < 120:
        write_DMLmashery_api(obj["masheryIdDEV"],obj["version"],"DEV",obj["DEV"]["environmentId"])
        time_waited=0
        print("Publishing API in TEST")
        publish_api_test(obj)
        environmentPublishedCount = environmentPublishedCount+1
    else:
        print(f"Waited {time_waited} seconds and nothing happened, SHUTTING DOWN")
        quit()
    
    #Se esiste ambiente di preprod
    if existsPreprodEnv:
        while time_waited<120:
            if check_api_status()==environmentPublishedCount:
                break
            else:
                print(f"API not ready! Published in: {check_api_status()} environments instead of: {environmentPublishedCount} and time waited: {time_waited}")
                time.sleep(5)
                time_waited=time_waited + 5
        if time_waited < 120:
            write_DMLmashery_api(obj["masheryIdTEST"],obj["version"],"TEST",obj["TEST"]["environmentId"])
            time_waited=0
            print("Publishing API in PREPROD")
            publish_api_preprod(obj)
        else:
            print(f"Waited {time_waited} seconds and nothing happened, SHUTTING DOWN")
            quit()
            
    #ripeti while 
    while time_waited<120:
        if check_api_status()==environmentPublishedCount:
            break
        else:
            print(f"API not ready! Published in: {check_api_status()} environments instead of: {environmentPublishedCount} and time waited: {time_waited}")
            time.sleep(5)
            time_waited=time_waited + 5
    if time_waited < 120:
        if existsPreprodEnv:
            write_DMLmashery_api(obj["masheryIdPREPROD"],obj["version"],"PREPROD",obj["PREPROD"]["environmentId"])
        else:
            write_DMLmashery_api(obj["masheryIdTEST"],obj["version"],"TEST",obj["TEST"]["environmentId"])
        time_waited=0
        print("Getting API Ready-to go-live")
        ready_to_go_live(obj)
    else:
        print(f"Waited {time_waited} seconds and nothing happened, SHUTTING DOWN")
        quit()
    
    print("Publishing API in PROD")
    publish_api_prod(obj)
    environmentPublishedCount = environmentPublishedCount+1
    
    #ripeti while 
    while time_waited<120:
        if check_api_status()==environmentPublishedCount:
            break
        else:
            print(f"API not ready! Published in: {check_api_status()} environments instead of: {environmentPublishedCount} and time waited: {time_waited}")
            time.sleep(5)
            time_waited=time_waited + 5
            
    if time_waited < 120:
        time_waited=0
        write_DMLmashery_api(obj["masheryIdPROD"],obj["version"],"PROD",obj["PROD"]["environmentId"])
    else:
        print(f"Waited {time_waited} seconds and nothing happened, SHUTTING DOWN")
        quit()

with open ("DMLmashery_api.sql","r+",encoding='utf-8') as fil:
    contenuto = fil.read()
    if contenuto.endswith(","):
        contenuto = contenuto.rstrip(",")
        fil.seek(0)  # Sposta il cursore all'inizio del file
        fil.write(contenuto)  # Sovrascrive il file con il nuovo contenuto
        fil.truncate()  # Troncamento del file per rimuovere il contenuto restante
        
with open("LoadThisFile.json", "w") as f:
    json.dump(data, f, indent=4)

print("All Operations Done")