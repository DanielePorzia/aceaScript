import json
import pandas as pd
import requests
import base64

def get_access_token():

    grant_type="password"
    client_id = "nckn7tn9ca49pxcjpyspkk9s"
    client_secret = "SUfCejzyrN"
    username = "kp_serviceaccount"
    password = "Sup3rS3gret@2024!"
    scope = "729547fd-4db4-4840-8de1-bb8a03daec13"
    
    # URL dell'endpoint per ottenere il token di accesso
    url = "https://api.mashery.com/v3/token"
    
    # Codifica le credenziali del client in Base64
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Intestazioni della richiesta
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    # Dati della richiesta
    data = {
        "grant_type": grant_type,
        "username": username,
        "password": password,
        "scope": scope
    }

    # Effettua la richiesta POST per ottenere il token
    response = requests.post(url, headers=headers, data=data)
    
    # Verifica se la richiesta ha avuto successo (HTTP Status 200)
    if response.status_code == 200:
        # Decodifica la risposta JSON
        token = response.json().get("access_token")
        return token
        
    else:
        # Stampa l'errore se la richiesta fallisce
        print(f"Errore nella richiesta: {response.status_code} - {response.text}")
        return None
        
def fetch_services(bearer_token,limit):
    filter = "&filter=organization.name:Areti" #Cambia con filtro desiderato
    url = f"https://api.mashery.com/v3/rest/services?limit={limit}&fields=name,id,description{filter}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Errore chiamando API per services")
        return None

# Funzione per chiamare l'API Mashery con un Bearer Token
def fetch_endpoints(service_id, bearer_token):
    url = f"https://api.mashery.com/v3/rest/services/{service_id}/endpoints?fields=publicDomains,requestPathAlias,name,outboundTransportProtocol,systemDomains"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Errore chiamando API per service ID {service_id}: {response.status_code} - {response.text}")
        return None


token = get_access_token()
print(f"Token: {token}")

json_api_list = fetch_services(token,300)

# Legge il file Excel
file_excel = "FileAcea.xlsx"
df = pd.read_excel(file_excel)
ListaNonTrovati=[]
counter = 0

columns_to_convert = [
    "description",
    "publicServersDEV", "privateServerUrlDEV", "masheryIdDEV",
    "publicServersTEST", "privateServerUrlTEST", "masheryIdTEST",
    "publicServersPREPROD", "privateServerUrlPREPROD", "masheryIdPREPROD",
    "publicServersPROD", "privateServerUrlPROD", "masheryIdPROD"
]

# Converti le colonne al tipo stringa
df[columns_to_convert] = df[columns_to_convert].astype(str)

# Iterazione su ogni oggetto nel file JSON
for obj in json_api_list:
    name = obj["name"]
    service_id = obj["id"]
    description = obj["description"]

    # Recupera gli endpoints dalla API di Mashery usando il Bearer Token
    endpoints = fetch_endpoints(service_id, token)

    if not endpoints:
        continue

    # Estrazione del nome da confrontare
    json_name_part = name.rsplit("-", 1)[0]

    # Trovare match nel file Excel
    matches = df[df['NomeExcelFornito'].apply(lambda x: str(x).rsplit("-", 1)[0].lower()) == json_name_part.lower()]

    if not matches.empty:
        counter = counter +1
        print(f"{counter}. {name} trovato")

        # Creazione della lista di oggetti JSON dalla risposta Mashery
        publicDomainsList = []
        
        for endpoint in endpoints:
            # Aggiunta di controlli per verificare la presenza dei dati
            domains = endpoint.get("publicDomains", [{}])
            if domains:
                for domain in domains:
                    if domain.get("address") not in publicDomainsList:
                        publicDomainsList.append(domain.get("address",""))
            
            protocol = endpoint.get("outboundTransportProtocol")
            systemDomains = endpoint.get("systemDomains")
            
            privateServerUrlList = []
            if systemDomains:
                for systemDomain in systemDomains:
                    if systemDomain.get("address") not in privateServerUrlList:
                        privateServerUrlList.append(protocol + "://" + systemDomain.get("address"))
            
        # Inserimento nel file Excel in base al suffisso del nome
        for idx in matches.index:
            df.at[idx,"description"] = description
            if name.endswith("qb"):
                df.at[idx, "publicServersDEV"] = ', '.join(publicDomainsList)
                df.at[idx, "privateServerUrlDEV"] = ', '.join(privateServerUrlList)
                df.at[idx,"masheryIdDEV"] = service_id
            elif name.endswith("qa"):
                df.at[idx, "publicServersTEST"] =  ', '.join(publicDomainsList)
                df.at[idx, "privateServerUrlTEST"] = ', '.join(privateServerUrlList)
                df.at[idx,"masheryIdTEST"] = service_id
            elif name.endswith("preprod"):
                df.at[idx, "publicServersPREPROD"] =  ', '.join(publicDomainsList)
                df.at[idx, "privateServerUrlPREPROD"] = ', '.join(privateServerUrlList)
                df.at[idx,"masheryIdPREPROD"] = service_id
            elif name.endswith("prod"):
                df.at[idx, "publicServersPROD"] =  ', '.join(publicDomainsList)
                df.at[idx, "privateServerUrlPROD"] = ', '.join(privateServerUrlList)
                df.at[idx,"masheryIdPROD"] = service_id
    
    else:
        ListaNonTrovati.append(name)
# Salva il file Excel modificato senza creare un nuovo file
df.to_excel(file_excel, index=False)

print("Operazione completata!")
print(f"Lista non trovati: {ListaNonTrovati}")