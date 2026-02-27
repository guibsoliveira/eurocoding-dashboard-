# Eurocoding Dashboard

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![Google Sheets API](https://img.shields.io/badge/Google%20Sheets-API%20v4-green?logo=googlesheets)](https://developers.google.com/sheets)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema automatizado de dashboard executivo e relatórios semanais para a **Eurocoding** — Especialista em Retrofit e Tecnologia Automotiva Premium.

---

## Visão Geral

A Eurocoding opera com uma planilha Google Sheets onde são registrados diariamente os serviços realizados, financeiro, estoque de peças e informações de clientes. Este sistema lê esses dados automaticamente, calcula KPIs, gera análises executivas e entrega relatórios profissionais ao diretor sem nenhuma intervenção manual.

```
Funcionário insere dados no Sheets
          │
          ▼
  Python roda todo dia 08h
  → Calcula KPIs
  → Gera análise executiva (PT-BR)
  → Atualiza aba PAINEL EXECUTIVO com gráficos nativos
          │
          ▼ (toda segunda-feira)
  Gera relatório PDF profissional
  → Salva em reports/2026/{mês}/semana_XX.pdf
  → Envia por e-mail ao diretor
```

---

## Funcionalidades

- **PAINEL EXECUTIVO no Google Sheets** — atualizado automaticamente com KPIs, rankings e análise do período
- **Relatório PDF semanal** — capa, cards de KPI, gráficos (receita diária, top serviços, parceiros) e análise executiva
- **E-mail semanal automatizado** — HTML bonito no corpo + PDF como anexo, toda segunda-feira
- **Versionamento de relatórios** — organizado por `reports/{ano}/{mês}/semana_XX_YYYY-MM-DD.pdf`
- **Balanço anual 2025** — relatório completo do histórico do ano anterior
- **Alertas de estoque** — detecta itens críticos e destaca no painel e no e-mail
- **Análise em linguagem natural** — narrativa executiva gerada automaticamente em português do Brasil

---

## KPIs Calculados

| Indicador | Frequência |
|-----------|-----------|
| Receita bruta | Diário / Semanal / Mensal |
| Margem de lucro (%) | Diário / Semanal / Mensal |
| Ticket médio | Semanal / Mensal |
| Top 5 serviços | Semanal / Mensal |
| Top 5 marcas atendidas | Semanal / Mensal |
| Performance por parceiro | Semanal / Mensal |
| Crescimento WoW / MoM | Semanal / Mensal |
| Comparativo YoY (2025 vs 2026) | Mensal |
| Alertas de estoque crítico | Diário |

---

## Stack Técnica

| Tecnologia | Uso |
|-----------|-----|
| `gspread` + `google-auth` | Leitura e escrita no Google Sheets via Service Account |
| `pandas` | Processamento e análise dos dados tabulares |
| `anthropic` | Geração de análise executiva em PT-BR |
| `matplotlib` | Gráficos para o relatório PDF |
| `fpdf2` | Composição do PDF profissional |
| `smtplib` | Envio de e-mail via Gmail |
| `python-dotenv` | Gerenciamento de variáveis de ambiente |

---

## Setup

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/eurocoding-dashboard.git
cd eurocoding-dashboard
```

### 2. Criar ambiente virtual e instalar dependências

```bash
py -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Configurar credenciais Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e habilite as APIs:
   - **Google Sheets API**
   - **Google Drive API**
3. Crie uma **Service Account** e baixe o JSON de credenciais
4. Salve como `config/credentials.json`
5. Compartilhe a planilha com o e-mail da service account (com permissão de **Editor**)

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com seus dados:

```
GOOGLE_SHEET_ID=sua_planilha_id
GOOGLE_CREDENTIALS_PATH=config/credentials.json
ANTHROPIC_API_KEY=sk-ant-sua-chave
GMAIL_USER=seu@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
DIRECTOR_EMAIL=diretor@eurocoding.com.br
```

> **Gmail App Password:** Acesse Conta Google → Segurança → Verificação em duas etapas → Senhas de app

### 5. Testar a instalação

```bash
py run.py --mode manual
```

---

## Uso

```bash
# Atualiza o PAINEL EXECUTIVO no Sheets (agendar: todo dia 08h)
py run.py --mode daily

# Gera relatório semanal + envia e-mail (agendar: toda segunda 08h)
py run.py --mode weekly

# Executa tudo sem enviar e-mail (para testes)
py run.py --mode manual

# Gera o balanço anual de 2025 (executar uma única vez)
py run.py --mode summary2025
```

---

## Agendamento Automático (Windows Task Scheduler)

1. Abra o **Agendador de Tarefas** do Windows
2. Crie duas tarefas:

**Tarefa diária:**
- Gatilho: Todo dia às 08:00
- Ação: `py C:\caminho\run.py --mode daily`

**Tarefa semanal:**
- Gatilho: Toda segunda-feira às 08:00
- Ação: `py C:\caminho\run.py --mode weekly`

---

## Estrutura do Projeto

```
eurocoding-dashboard/
├── config/
│   ├── credentials.json          # ← não commitado
│   └── settings.py               # configurações centralizadas
├── src/
│   ├── reader.py                 # Google Sheets → DataFrames
│   ├── kpi_engine.py             # cálculo de KPIs
│   ├── analyst.py                # análise executiva PT-BR
│   ├── dashboard_writer.py       # atualiza PAINEL EXECUTIVO
│   ├── report_generator.py       # gera PDF semanal e anual
│   └── email_sender.py           # envia e-mail com PDF
├── reports/                      # ← não commitado
│   ├── historico_2025/
│   └── 2026/{mês}/
├── .env                          # ← não commitado
├── .env.example
├── requirements.txt
└── run.py
```

---

## Licença

MIT © 2026 — Desenvolvido para [Eurocoding](https://eurocoding.com.br)
