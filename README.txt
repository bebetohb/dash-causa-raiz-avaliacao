# 📊 Dashboard Causa Raiz - Azure DevOps

Este projeto é um dashboard interativo em **Python + Streamlit** que consome dados diretamente do **Azure DevOps**, exibindo estatísticas e gráficos sobre **Work Items (ESCs)**, suas causas raiz, avaliações e status.

---

## 🚀 **Funcionalidades**

- 🔎 Consulta automática de Work Items via API do Azure DevOps  
- 📅 Filtro de período baseado em **Created Date** e **Closed Date**  
- 📋 Visualização tabular com rolagem (10 registros por página)  
- 📈 Gráficos interativos (Plotly) mostrando:
  - Total de ESCs encerradas por período  
  - Distribuição por **Causa Raiz** e **Avaliação**  
  - Top 5 Causas Raiz do período selecionado  

---

## 🧩 **Tecnologias Utilizadas**

- [Python 3.10+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Requests](https://requests.readthedocs.io/en/latest/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## ⚙️ **Informações sobre o Projeto**

O projeto está disponível no GitHub, repositório: https://github.com/bebetohb/dash-causa-raiz-avaliacao.git

Ele também foi hospedado no Streamlit Community Cloud: https://share.streamlit.io/

⚠️ **Informações Importantes:**

1. É necessário uma Querie criada no Azure DevOps com os WorkItems, pois é dela que os dados serão carregados

2. Token no Azure DevOps com permissão de Work Items → Read.

3. Arquivo nomeado com "pat.env" que irá armazenar os dados da conexão com a API
   O arquivo NÃO pode subir para o GitHub, pois contém os dados do TOKEN!
   
   O arquivo deve ser criado na raiz do projeto e com o seguinte modelo:

	ORGANIZATION=
	PAT=
	# Projeto 1
	PROJECT1=
	QUERY_ID1=

🧠 **Como Rodar o Dashboard**

1. Clone o projeto.

2. Baixe os pacotes Python que estão no arquivo requirements.txt

3. Dentro da pasta do projeto, rode o comando(certificar-se que o arquivo pat.env está configurado):

streamlit run dashboard_cr.py

Isso abrirá automaticamente o dashboard no navegador, geralmente em 👉 http://localhost:8501

🧰 **Estrutura do Projeto**

dashboard-causa-raiz/
│
├── .gitignore #Ignora arquivos sensíveis
├── README.md #Este arquivo
├── Rodar_Dashboard_-_Clique_Aqui.bat #Execução do dashboard direta(Altere o caminho)
├── dashboard_cr.py #Código principal do dashboard
└── requirements.txt #Dependências do projeto
└── pat.env.exemplo #Exemplo do pat

🤝 **Contribuições**

Sinta-se à vontade para abrir issues e pull requests com melhorias ou correções.
Este projeto foi criado para auxiliar times que utilizam o Azure DevOps no acompanhamento de Causas Raiz e Avaliações de ESC's.

🧑‍💻 **Autor**

Humberto Bravo

📧 Contato: https://www.linkedin.com/in/humbertobravohb/
📍 Projeto pessoal de automação e análise de indicadores DevOps.