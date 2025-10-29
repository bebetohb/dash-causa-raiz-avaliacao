# ------------------------------------------------------
# 📊 DASHBOARD: Causa Raiz x Avaliação (Azure DevOps)
# ------------------------------------------------------
# Autor: Humberto Bravo
# Última atualização: 28/10/2025
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
def get_work_items(organization, project, query_id, pat):
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
            st.warning(f"Erro ao buscar detalhes: {details_resp.status_code}")
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
                "Avaliação": fields.get("Custom.df595db0-b245-4da1-8c98-45ab05ed33cf")
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
project2 = os.getenv("PROJECT2")
query_id2 = os.getenv("QUERY_ID2")

if not all([organization, pat, project1, query_id1, project2, query_id2]):
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
    df1 = get_work_items(organization, project1, query_id1, pat)
    df1["Origem"] = "Visibilidade"

    df2 = get_work_items(organization, project2, query_id2, pat)
    df2["Origem"] = "BU Inteligência Colaborativa"

    df = pd.concat([df1, df2], ignore_index=True)

if df.empty:
    st.warning("Nenhum work item encontrado nos projetos informados.")
    st.stop()


# ======================================================
# 🗓️ FILTRO DE PERÍODO
# ======================================================
for col in ["Created Date", "Closed Date"]:
    df[col] = pd.to_datetime(df[col], errors="coerce").dt.tz_localize(None)

st.subheader("📅 Filtro de Período")

hoje = dt.date.today()
start_date, end_date = st.date_input(
    "Selecione o período de criação da ESC",
    value=(hoje, hoje),
)

df_periodo = df[
    (df["Created Date"] >= pd.to_datetime(start_date)) &
    (df["Created Date"] <= pd.to_datetime(end_date))
].copy()


# ======================================================
# 📋 GRID ROLÁVEL + GRÁFICOS
# ======================================================
st.subheader("📋 Work Items no Período")

if df_periodo.empty:
    st.warning("Nenhum Work Item encontrado para o período selecionado.")
else:
    st.dataframe(df_periodo, use_container_width=True, height=350)

    st.divider()
    st.subheader("📈 Análises do Período")

    encerradas = df_periodo[df_periodo["State"].fillna("").str.lower().isin(["closed", "done", "encerrada"])]
    total_encerradas = len(encerradas)
    st.markdown(f"**No período selecionado foram encerradas {total_encerradas} ESC(s).**")

    causa_avaliacao = df_periodo.groupby(["Causa Raiz", "Avaliação"], dropna=False).size().reset_index(name="Total")

    if not causa_avaliacao.empty:
        fig1 = px.bar(
            causa_avaliacao,
            x="Causa Raiz",
            y="Total",
            color="Avaliação",
            title="Causa Raiz x Avaliação",
            text="Total",
        )
        fig1.update_layout(
            height=800,
            margin=dict(l=50, r=50, t=50, b=100),
            xaxis_title="Causa Raiz",
            yaxis_title="Total de Chamados",
            legend_title="Avaliação",
            bargap=0.25,
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Nenhuma causa raiz encontrada no período.")

    st.subheader("🏆 Top 5: Causa Raiz x Avaliação")
    top5 = (
        df_periodo.groupby(["Causa Raiz", "Avaliação"], dropna=False)
        .size()
        .reset_index(name="Total")
        .sort_values(by="Total", ascending=False)
        .head(5)
    )

    if not top5.empty:
        ranking_text = ""
        for i, row in enumerate(top5.itertuples(index=False), 1):
            ranking_text += f"{i}. {row[0]} : {row[1]} → ({row[2]})\n"

        st.markdown(f"```\n{ranking_text}\n```")
    else:
        st.info("Nenhuma causa raiz encontrada para gerar o ranking.")
