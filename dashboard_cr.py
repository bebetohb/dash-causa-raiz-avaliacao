import requests
import pandas as pd
import streamlit as st
import datetime as dt
import plotly.express as px

# ------------------------------------------------------
# ⚙️ CONFIGURAÇÕES DO AZURE DEVOPS
# ------------------------------------------------------

organization = "" #ORGANIZACAO
project = "" #PROJETO
query_id = "" #ID DA QUERIE
pat = "" #INSERIR A KEY

# ------------------------------------------------------
# 🔌 FUNÇÃO: Buscar Work Items
# ------------------------------------------------------
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

    # IDs em lotes (evita erro 414)
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
            df_total = pd.concat([
                df_total,
                pd.DataFrame([{
                    "ID": item.get("id"),
                    "Work Item Type": fields.get("System.WorkItemType"),
                    "Title": fields.get("System.Title"),
                    "Assigned To": fields.get("System.AssignedTo", {}).get("displayName") if isinstance(fields.get("System.AssignedTo"), dict) else fields.get("System.AssignedTo"),
                    "State": fields.get("System.State"),
                    "Created Date": fields.get("System.CreatedDate"),
                    "Closed Date": fields.get("Microsoft.VSTS.Common.ClosedDate"),
                    "Causa Raiz": fields.get("Custom.dny_Causa_raiz"),
                    "Avaliação": fields.get("Custom.df595db0-b245-4da1-8c98-45ab05ed33cf")
                }])
            ], ignore_index=True)

    return df_total

# ------------------------------------------------------
# 🧱 INTERFACE STREAMLIT
# ------------------------------------------------------
st.set_page_config(page_title="Dashboard Causa Raiz", layout="wide")
st.title("📊 Dashboard - Causa Raiz das ESCs")

with st.spinner("Carregando dados do Azure DevOps..."):
    df = get_work_items(organization, project, query_id, pat)

if df.empty:
    st.warning("Nenhum work item encontrado. Verifique a query ou permissões.")
    st.stop()

# ------------------------------------------------------
# 🗓️ FILTRO DE PERÍODO (INICIA NO DIA ATUAL)
# ------------------------------------------------------
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

# ------------------------------------------------------
# 📋 GRID ROLÁVEL
# ------------------------------------------------------
st.subheader("📋 Work Items no Período")

if df_periodo.empty:
    st.warning("Nenhum Work Item encontrado para o período selecionado.")
else:
    st.dataframe(
        df_periodo,
        use_container_width=True,
        height=350,
    )

    # ------------------------------------------------------
    # 📈 MÉTRICAS E GRÁFICOS
    # ------------------------------------------------------
    st.divider()
    st.subheader("📈 Análises do Período")

    # 1️⃣ Total de ESCs encerradas
    # Substitui NaN por string vazia antes de aplicar o lower e o isin
    encerradas = df_periodo[
    df_periodo["State"].fillna("").str.lower().isin(["closed", "done", "encerrada"])
]

    total_encerradas = len(encerradas)
    st.markdown(f"**No período selecionado foram encerradas {total_encerradas} ESC(s).**")

    # 2️⃣ Causa Raiz x Avaliação
    causa_avaliacao = df_periodo.groupby(
        ["Causa Raiz", "Avaliação"], dropna=False
    ).size().reset_index(name="Total")

    if not causa_avaliacao.empty:
        fig1 = px.bar(
            causa_avaliacao,
            x="Causa Raiz",
            y="Total",
            color="Avaliação",
            title="Causa Raiz x Avaliação",
            text="Total",
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Nenhuma causa raiz encontrada no período.")

    # 3️⃣ TOP 5 Causas Raiz
    top5 = (
        df_periodo.groupby("Causa Raiz")
        .size()
        .reset_index(name="Total")
        .sort_values(by="Total", ascending=False)
        .head(5)
    )

    if not top5.empty:
        fig2 = px.pie(
            top5,
            names="Causa Raiz",
            values="Total",
            title="Top 5 Causas Raiz",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Não há causas suficientes para gerar o Top 5.")
