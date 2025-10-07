import requests
from requests.auth import HTTPBasicAuth
import json

# ------------------------------------------------------
# CONFIGURAÇÃO
# ------------------------------------------------------
organization = "" #ORGANIZACAO
project = "" #PROJETO
query_id = "" #ID DA QUERIE
pat = "" #INSERIR A KEY

# ------------------------------------------------------
# FUNÇÃO PARA PEGAR WORK ITEMS
# ------------------------------------------------------
def get_work_items_debug(organization, project, query_id, pat):
    # 1️⃣ Buscar IDs da query
    wiql_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql/{query_id}?api-version=7.0"
    wiql_resp = requests.get(wiql_url, auth=HTTPBasicAuth('', pat))
    if wiql_resp.status_code != 200:
        print("Erro ao buscar WIQL:", wiql_resp.status_code)
        print(wiql_resp.text)
        return

    work_items = wiql_resp.json().get("workItems", [])
    if not work_items:
        print("Nenhum work item encontrado")
        return

    # 2️⃣ Buscar detalhes
    ids = [str(wi["id"]) for wi in work_items]
    ids_str = ",".join(ids[:10])  # pega só os 10 primeiros para teste
    url_details = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems?ids={ids_str}&$expand=fields&api-version=7.0"
    details_resp = requests.get(url_details, auth=HTTPBasicAuth('', pat))
    details_data = details_resp.json()

    # 3️⃣ Debug: mostrar todas as chaves dos campos
    for item in details_data.get("value", []):
        fields = item.get("fields", {})
        print(json.dumps(fields.keys(), indent=2))  # imprime de forma legível

# ------------------------------------------------------
# RODAR FUNÇÃO
# ------------------------------------------------------
get_work_items_debug(organization, project, query_id, pat)