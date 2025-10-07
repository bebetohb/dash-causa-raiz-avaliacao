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

## ⚙️ **Configuração do Projeto**

### 1. Clonar o repositório

git clone https://github.com/seu-usuario/dashboard-causa-raiz.git
cd dashboard-causa-raiz

### 2. Criar e ativar o ambiente virtual

python -m venv venv
venv\Scripts\activate    # Windows
# ou
source venv/bin/activate  # Linux/Mac

### 3. Instalar as dependências

pip install -r requirements.txt

### Se você ainda não criou o arquivo requirements.txt, use:

pip install streamlit requests pandas plotly python-dotenv
pip freeze > requirements.txt

### 4. Configuração do Token (PAT)

Crie um arquivo chamado pat.env na raiz do projeto com o seguinte conteúdo:

ini
AZURE_PAT=seu_token_aqui

⚠️ **Importante:**

Este arquivo NÃO deve ser enviado ao GitHub (já está listado no .gitignore).

Gere o token no Azure DevOps com permissão de Work Items → Read.

O token tem validade configurável (ex: 30, 90, 180 dias).

É necessário ter uma consulta pré-configurada no queries do Azure DevOps.

🧠 **Como Rodar o Dashboard**

Dentro da pasta do projeto, rode o comando:

streamlit run dashboard_cr.py

Isso abrirá automaticamente o dashboard no navegador, geralmente em:

👉 http://localhost:8501

🧰 **Estrutura do Projeto**

dashboard-causa-raiz/
│
├── dashboard_cr.py        # Código principal do dashboard
├── pat.env                # Token local (ignorado pelo Git)
├── requirements.txt       # Dependências do projeto
├── .gitignore             # Ignora arquivos sensíveis
└── README.md              # Este arquivo

🤝 **Contribuições**

Sinta-se à vontade para abrir issues e pull requests com melhorias ou correções.
Este projeto foi criado para auxiliar times que utilizam o Azure DevOps no acompanhamento de Causas Raiz e Avaliações de ESCs.

🧑‍💻 **Autor**

Humberto Bravo

📧 Contato: https://www.linkedin.com/in/humbertobravohb/
📍 Projeto pessoal de automação e análise de indicadores DevOps.