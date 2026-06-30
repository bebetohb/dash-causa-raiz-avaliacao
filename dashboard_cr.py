# ------------------------------------------------------
# 📊 DASHBOARD: Causa Raiz x Avaliação (Azure DevOps)
# ------------------------------------------------------
# Autor: Humberto Bravo
# Última atualização: 30/06/2026
# ------------------------------------------------------

import os
import requests
import pandas as pd
import streamlit as st
import datetime as dt
import plotly.express as px
from dotenv import load_dotenv


# ======================================================
# 🔌 FUNÇÃO: Buscar Work Items no Azure DevOps
# ======================================================
@st.cache_data(
    ttl=300,
    show_spinner="Carregando ESC's por período..."
)
def get_work_items(
    organization,
    project,
    query_id,
    pat
):
    base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql/{query_id}?api-version=7.0"
    headers = {"Content-Type": "application/json"}
    response = requests.get(base_url, headers=headers, auth=("", pat))

    if response.status_code != 200:
        st.error(f"Erro ao buscar work items: {response.status_code}")
        st.text(response.text)
        return pd.DataFrame()

    data = response.json()
    work_items = data.get("workItems", [])
    if not work_items:
        return pd.DataFrame()

    ids = [str(item["id"]) for item in work_items]
    df_total = pd.DataFrame()

    for i in range(0, len(ids), 100):
        batch = ids[i:i+100]
        ids_str = ",".join(batch)
        url_details = f"https://dev.azure.com/{organization}/_apis/wit/workitems?ids={ids_str}&$expand=Fields&api-version=7.0"
        details_resp = requests.get(url_details, headers=headers, auth=("", pat))

        if details_resp.status_code != 200:
            st.warning(
    f"Erro ao buscar detalhes: {details_resp.status_code} | IDs {batch[0]} até {batch[-1]}"
            )                  
            continue

        details_data = details_resp.json()
        for item in details_data.get("value", []):
            fields = item.get("fields", {})
            df_total = pd.concat([df_total, pd.DataFrame([{
                "ID": item.get("id"),
                "Work Item Type": fields.get("System.WorkItemType"),
                "Title": fields.get("System.Title"),
                "Assigned To": (
                    fields.get("System.AssignedTo", {}).get("displayName")
                    if isinstance(fields.get("System.AssignedTo"), dict)
                    else fields.get("System.AssignedTo")
                ),
                "State": fields.get("System.State"),
                "Created Date": fields.get("System.CreatedDate"),
                "Closed Date": fields.get("Microsoft.VSTS.Common.ClosedDate"),
                "Causa Raiz": fields.get("Custom.dny_Causa_raiz"),
                "Avaliação": fields.get("Custom.df595db0-b245-4da1-8c98-45ab05ed33cf"),
                "Area Path": fields.get("System.AreaPath")     
            }])], ignore_index=True)

    return df_total


# ======================================================
# 🔐 CONFIGURAÇÕES SEGURAS (carregadas do arquivo pat.env)
# ======================================================
load_dotenv("pat.env")

organization = os.getenv("ORGANIZATION")
pat = os.getenv("PAT")

# Projetos e Queries
project1 = os.getenv("PROJECT1")
query_id1 = os.getenv("QUERY_ID1")

if not all([organization, pat, project1, query_id1]):
    st.error("⚠️ Erro: variáveis ausentes. Verifique o arquivo 'pat.env'.")
    st.stop()


# ======================================================
# 🧱 INTERFACE STREAMLIT
# ======================================================
st.set_page_config(page_title="Dashboard Causa Raiz", layout="wide")
st.title("📊 Dashboard - Causa Raiz x Avaliação")

# ------------------------------------------------------
# 🔄 Carregamento inicial
# ------------------------------------------------------
with st.spinner("Aguarde: carregando dados dos projetos do Azure DevOps..."):

    ultima_atualizacao = dt.datetime.now()

    st.caption(
    f"Última atualização: {ultima_atualizacao:%d/%m/%Y %H:%M}"
    )

    st.divider()

    df1 = get_work_items(organization, project1, query_id1, pat)
    df1["Origem"] = "BU Inteligência Colaborativa"

    df = pd.concat([df1], ignore_index=True)

if df.empty:
    st.warning("Nenhum work item encontrado nos projetos informados.")
    st.stop()

# ======================================================
# 🏷️ CLASSIFICAÇÃO DE PRODUTO
# ======================================================

AREAS_INDIRETO = [
    "BU Inteligência Colaborativa\\Indireto",
    "Visibilidade\\Sustentacao Indireto"
]

AREAS_DIRETO = [
    "BU Inteligência Colaborativa\\Direto - Industria",
    "Visibilidade\\Visibilidade Direto",
    "BU Inteligência Colaborativa\\Direto - Mercado e Varejo",
    "NeoRetail Ops"
]

def definir_produto(area):

    if area in AREAS_DIRETO:
        return "Visibilidade Direto"

    if area in AREAS_INDIRETO:
        return "Visibilidade Indireto"

    return "Outros"

df["Produto"] = df["Area Path"].apply(definir_produto)

# ======================================================
# 🗓️ FILTRO DE PERÍODO
# ======================================================
for col in ["Created Date", "Closed Date"]:
    df[col] = pd.to_datetime(df[col], errors="coerce").dt.tz_localize(None)

hoje = dt.date.today()
inicio_padrao = hoje - dt.timedelta(days=30)

with st.expander("📅 Filtros", expanded=True):

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        start_date, end_date = st.date_input(
            "Período",
            value=(inicio_padrao, hoje)
        )

    with col2:
        produtos = st.multiselect(
            "Produto",
            options=sorted(df["Produto"].dropna().unique()),
            default=sorted(df["Produto"].dropna().unique())
        )

    with col3:
        st.write("")
        st.write("")

        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()

df_periodo = df[
    (df["Created Date"] >= pd.to_datetime(start_date)) &
    (df["Created Date"] <= pd.to_datetime(end_date))
].copy()

df_periodo = df_periodo[
    df_periodo["Produto"].isin(produtos)
]

causas = sorted(
    df_periodo["Causa Raiz"]
    .dropna()
    .unique()
)

causa_filtro = st.multiselect(
    "Filtrar por Causa Raiz",
    options=causas,
    default=causas
)

df_periodo = df_periodo[
    df_periodo["Causa Raiz"].isin(causa_filtro)
]

# ======================================================
# 📋 GRID ROLÁVEL + GRÁFICOS
# ======================================================
st.subheader("📋 Work Items no Período")

if df_periodo.empty:

    st.warning(
        "Nenhum Work Item encontrado para os filtros selecionados."
    )

    st.stop()
else:
    st.dataframe(df_periodo, use_container_width=True, height=350)

    st.divider()
    st.subheader("📈 Análises do Período")

    encerradas = df_periodo[
    df_periodo["State"]
    .fillna("")
    .str.lower()
    .isin(["closed", "done", "encerrada"])
]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "ESCs Total",
    len(df_periodo)
)

col2.metric(
    "Direto",
    len(
        df_periodo[
            df_periodo["Produto"] ==
            "Visibilidade Direto"
        ]
    )
)

col3.metric(
    "Indireto",
    len(
        df_periodo[
            df_periodo["Produto"] ==
            "Visibilidade Indireto"
        ]
    )
)

col4.metric(
    "Encerradas",
    len(encerradas)
)

causa_avaliacao = (
    df_periodo.groupby(
        ["Causa Raiz", "Avaliação"],
        dropna=False
    )
    .size()
    .reset_index(name="Total")
)

if not causa_avaliacao.empty:

    ordem = (
        causa_avaliacao.groupby("Causa Raiz")["Total"]
        .sum()
        .sort_values()
        .index
    )

    fig1 = px.bar(
        causa_avaliacao,
        y="Causa Raiz",
        x="Total",
        color="Avaliação",
        orientation="h",
        text="Total",
        category_orders={
            "Causa Raiz": ordem
        }
    )

    fig1.update_layout(
        title="📈 Causa Raiz x Avaliação",
        height=700,
        yaxis_title="",
        xaxis_title="Total de ESCs",
        legend_title="Avaliação"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.subheader(
    "🏆 Ranking de Ofensores"
)

ranking = (
    df_periodo.groupby(
        ["Causa Raiz", "Avaliação"],
        dropna=False
    )
    .size()
    .reset_index(name="Total")
    .sort_values(
        "Total",
        ascending=False
    )
)

ranking.insert(
    0,
    "Ranking",
    range(
        1,
        len(ranking) + 1
    )
)

st.dataframe(
    ranking,
    use_container_width=True,
    height=350
)

st.subheader(
    "🔍 Detalhamento por Causa Raiz"
)

causa_selecionada = st.selectbox(
    "Selecione uma causa raiz",
    sorted(
        df_periodo["Causa Raiz"]
        .dropna()
        .unique()
    )
)

detalhamento = df_periodo[
    df_periodo["Causa Raiz"]
    == causa_selecionada
]

st.dataframe(
    detalhamento,
    use_container_width=True,
    height=350
)