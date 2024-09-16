import pandas as pd
import json
import os
import requests

def get_access_token():

    print("Getting Access Token")
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
        print(f"Token: {token}")
        return token
        
    else:
        # Stampa l'errore se la richiesta fallisce
        print(f"Errore nella richiesta: {response.status_code} - {response.text}")
        return None
        
def trasform_domains(token, listDomains, environmentId, gatewayId):
    
    basePath = "https://nopro-api.apishare.cloud/apigateway-management/domains"
    url = basePath + f"?filter=gateways.gatewayId:{gatewayId};environment.environmentId:{environmentId}"
    
    headers = {
    "Content-Type": "application/json",
    "requestId": "00000000-0000-0000-0000-000000000000",
    "sessionId": "00000000-0000-0000-0000-000000000000",
    "x-api-key": "KAtBDiOii64OfWhYFZb3w8uxS6Ud4axi8zGilMsH",
    "Authorization": f"Bearer {token}"
}

    response = requests.get(url,headers=headers)
    
     # Verifica se la richiesta ha avuto successo (HTTP Status 200)
    if response.status_code == 200:
        # Fai cose
        for domain in listDomains:
            for responseDomain in response.json():
                if domain.get("domainId") == responseDomain.get("name"):
                    domain["domainId"] = responseDomain.get("domainId")
        return listDomains
        
    else:
        # Stampa l'errore se la richiesta fallisce
        print(f"Errore nella richiesta: {response.status_code} - {response.text}")
        return None

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# TODO: Variabili Comuni Aggiustarle in base al caso
integrationPatternId = "0a1a2eab-a885-4586-8ae9-38a17cf9037f"
authorizationTypeId = "f36880e9-9455-477d-b37b-e62254c99eec"
environmentIdDEV = "9c64453b-2028-40dd-aec2-db12583614ae"
environmentIdTEST = "25bd7aed-f4a0-4f4d-a0b3-0a6570eb73c9"
environmentIdPREPROD = "9fa2cc39-7d1b-4ae7-a690-58259a1d28a6"
environmentIdPROD = "2d68ccc1-792e-46b1-8c91-a8f8a3312651"
gatewayId = "e17938e6-5875-49ae-9047-a7fa4f524937" #ACEA: "e17938e6-5875-49ae-9047-a7fa4f529078"


bearer_token = get_access_token()
file_excel = "FileAcea.xlsx"
df = pd.read_excel(file_excel)

# Specifica il percorso della cartella contenente le cartelle Swagger
base_folder = r"ApiShare"  

# Lista per salvare le API
json_list = []

# Itera su ogni riga
for index, row in df.iterrows():
    # Sottostringa per trovare la cartella corrispondente
    swagger_folder_name = row["nomeCartella"].rsplit("-", 1)[0]  
    swagger_folder_path = os.path.join(base_folder, swagger_folder_name)

    # Inizializzare variabili per fileName e body
    swagger_file_name = None
    swagger_body = None
    contentType = None
    
    # Verifica se lo Swagger è presente e se la cartella esiste
    if  os.path.exists(swagger_folder_path):
        # Trova il file nella cartella corrispondente
        swagger_files = os.listdir(swagger_folder_path)
        
        # Assicurati di prendere solo il primo file trovato
        if swagger_files:
            swagger_file_name = swagger_files[0]           # Supponiamo che ci sia solo un file
            swagger_file_path = os.path.join(swagger_folder_path, swagger_file_name)

            # Leggi il contenuto del file
            with open(swagger_file_path, 'r', encoding='utf-8') as f:
                swagger_body = f.read()
            if swagger_files[0].rsplit(".",1)[1] == "json":
                contentType = "application/json"
            if swagger_files[0].rsplit(".",1)[1] == "wsdl":
                contentType = "text/xml"
                
# FINE SWAGGER PART

# INIZIO CREAZIONE JSON
    description = None
    if pd.isna(row["description"]):
        description = "             "
    else:
        description = row["description"]
    
    # Crea un oggetto JSON per ogni riga
    json_obj = {
        "apiOwner": row["apiOwner"],
        "description": description,
        "developer": row["developer"],
        "groupId": row["groupId"],
        "integrationPatternId": integrationPatternId,
        "name": row["apiName"],
        "producers": [row["producerId"]],
        "version": row["apiVersion"],
        "fileName": str(swagger_file_name).rsplit(".",1)[0],  # Usa il nome del file trovato
        "contentType": contentType,
        "body": swagger_body,  # Usa il contenuto del file trovato
        "ApiShareId": "",
        "authorizationType":[authorizationTypeId]

    }

# INIZIO DEPLOYMENT PART
    
    if not pd.isna(row["masheryIdDEV"]):
        publicServersDomainDEV = []
        for domain in row["publicServersDEV"].split(", "):
            publicServersDomainDEV.append({"domainId":domain,"basePath":"/"})
        deploymentDEV = {
            "environmentId": environmentIdDEV,
            "gatewayId": gatewayId,
            "privateServerUrls": [row["privateServerUrlDEV"]],
            "publicServers": trasform_domains(bearer_token,publicServersDomainDEV,environmentIdDEV,gatewayId)
        }
        json_obj["masheryIdDEV"] = row["masheryIdDEV"]
        json_obj["DEV"] = deploymentDEV
        
    if not pd.isna(row["masheryIdTEST"]):
        publicServersDomainTEST = []
        for domain in row["publicServersTEST"].split(", "):
            publicServersDomainTEST.append({"domainId":domain,"basePath":"/"})
        deploymentTEST = {
            "environmentId": environmentIdTEST ,
            "gatewayId": gatewayId,
            "privateServerUrls": [row['privateServerUrlTEST']],
            "publicServers": trasform_domains(bearer_token,publicServersDomainTEST,environmentIdTEST,gatewayId)
        }
        json_obj["masheryIdTEST"] = row["masheryIdTEST"]
        json_obj["TEST"] = deploymentTEST
    
    if not pd.isna(row["masheryIdPREPROD"]):
        publicServersDomainPREPROD = []
        for domain in row["publicServersPREPROD"].split(", "):
            publicServersDomainPREPROD.append({"domainId":domain,"basePath":"/"})
        deploymentPREPROD = {
            "environmentId": environmentIdPREPROD,
            "gatewayId": gatewayId,
            "privateServerUrls": [row['privateServerUrlPREPROD']],
            "publicServers": trasform_domains(bearer_token,publicServersDomainPREPROD,environmentIdPREPROD,gatewayId)
        }
        json_obj["masheryIdPREPROD"] = row["masheryIdPREPROD"]
        json_obj["PREPROD"] = deploymentPREPROD
        
    if not pd.isna(row["masheryIdPROD"]):
        publicServersDomainPROD = []
        for domain in row["publicServersPROD"].split(", "):
            publicServersDomainPROD.append({"domainId":domain,"basePath":"/"})
        deploymentPROD = {
            "environmentId": environmentIdPROD,
            "gatewayId": gatewayId,
            "privateServerUrls": [row['privateServerUrlPROD']],
            "publicServers": trasform_domains(bearer_token,publicServersDomainPROD,environmentIdPROD,gatewayId)
        }
        json_obj["masheryIdPROD"] = row["masheryIdPROD"]
        json_obj["PROD"] = deploymentPROD
    
    # Aggiungi l'oggetto JSON alla lista
    json_list.append(json_obj)

# Scrivi la lista di oggetti JSON in un file
output_file = "LoadThisFile.json"
with open(output_file, "w") as f:
    json.dump(json_list, f, indent=4)

print(f"File JSON creato con successo: {output_file}")
