import os
from dotenv import load_dotenv

load_dotenv(override=True)  # override=True garante que .env prevalece sobre variáveis do sistema

# ─── Google Sheets ───────────────────────────────────────────────────────────
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1VVLzeF4GUyrkSi9KBEYVMdmkRKcZCfRlvLloNO-injA")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "config/credentials.json")

# GIDs confirmados via inspeção da planilha
SHEETS = {
    "relatorios_2024": {"name": "RELATÓRIOS 2024",   "gid": 1886390625},
    "relatorios_2025": {"name": "RELATÓRIOS 2025",   "gid": 1103362625},
    "clientes_2025":   {"name": "CLIENTES2025",      "gid": 1797119256},
    "estoque_2025":    {"name": "ESTOQUE2025",        "gid": 1477425085},
    "clientes_2026":   {"name": "CLIENTES2026",      "gid": 1998908621},
    "estoque_2026":    {"name": "ESTOQUE2026",        "gid": 773335477},
    "relatorios_2026": {"name": "RELATÓRIOS2026",    "gid": 1230187570},
    "painel":          {"name": "PAINEL EXECUTIVO",  "gid": None},  # criado pelo sistema
}

# Estrutura de colunas das abas CLIENTES e ESTOQUE
# Headers estão na LINHA 3 (índice 2), dados a partir da LINHA 4
CLIENTES_HEADER_ROW = 2   # índice 0-based
CLIENTES_DATA_START = 3   # índice 0-based

CLIENTES_COLS = {
    "data":        1,   # B – Data (ex: "6-jan.")
    "carro":       2,   # C – Carro
    "servico":     3,   # D – Serviço
    "id":          4,   # E – ID (peça/serviço)
    "nome_peca":   5,   # F – Nome da peça
    "custo_peca":  6,   # G – Custo da peça
    "venda_peca":  7,   # H – Venda da peça
    "mo":          8,   # I – Valor da M.O (mão de obra)
    "terceiros":   9,   # J – Terceiros
    "total":       10,  # K – Valor total
    "lucro":       11,  # L – Lucro
    "parceiro":    12,  # M – Parceiro
    "obs":         13,  # N – OBS
}

# ─── Anthropic / Claude ───────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# True somente quando a chave real estiver configurada no .env
ANTHROPIC_AVAILABLE = bool(
    ANTHROPIC_API_KEY and ANTHROPIC_API_KEY not in ("", "sk-ant-your-key-here")
)

CLAUDE_MODEL = "claude-opus-4-5"

# ─── E-mail ───────────────────────────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
DIRECTOR_EMAIL = os.getenv("DIRECTOR_EMAIL", "")

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587

# ─── Empresa ─────────────────────────────────────────────────────────────────
COMPANY_NAME = "Eurocoding"
COMPANY_TAGLINE = "Especialista em Retrofit e Tecnologia Automotiva Premium"
PRIMARY_COLOR = (26, 35, 126)    # azul escuro (RGB)
ACCENT_COLOR  = (0, 188, 212)    # ciano (RGB)

# ─── Relatórios ───────────────────────────────────────────────────────────────
REPORTS_DIR = "reports"
REPORTS_2025_DIR = "reports/historico_2025"

MONTHS_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março",     4: "abril",
    5: "maio",    6: "junho",     7: "julho",      8: "agosto",
    9: "setembro",10: "outubro",  11: "novembro",  12: "dezembro",
}

DATE_MONTHS_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4,
    "mai": 5, "jun": 6, "jul": 7, "ago": 8,
    "set": 9, "out": 10, "nov": 11, "dez": 12,
}
