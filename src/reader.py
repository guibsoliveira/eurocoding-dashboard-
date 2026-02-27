"""
reader.py – Leitura da planilha Google Sheets via Service Account.

Estrutura confirmada da planilha (abas CLIENTES/ESTOQUE):
  Linha 1 – vazia (apenas totais acumulados nas colunas financeiras)
  Linha 2 – rótulos de seção
  Linha 3 – cabeçalhos das colunas (Data, Carro, Serviço, ...)
  Linha 4+ – registros de serviços/lançamentos
"""

import re
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from config.settings import (
    SHEET_ID, CREDENTIALS_PATH,
    CLIENTES_HEADER_ROW, CLIENTES_DATA_START,
    CLIENTES_COLS, DATE_MONTHS_PT, SHEETS,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


def _parse_brl(value: str) -> float:
    """Converte 'R$ 1.500,00' ou '-' para float."""
    if not value or str(value).strip() in ("-", "", "R$ -"):
        return 0.0
    cleaned = re.sub(r"[R$\s]", "", str(value)).replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_date(raw: str, year: int) -> datetime | None:
    """
    Converte '6-jan.' → datetime(year, 1, 6).
    Aceita variações como '6-jan', '06-jan.', '6-jan.'.
    """
    if not raw or str(raw).strip() == "":
        return None
    raw = str(raw).strip().rstrip(".")
    parts = raw.split("-")
    if len(parts) != 2:
        return None
    try:
        day = int(parts[0])
        month_key = parts[1].lower()[:3]
        month = DATE_MONTHS_PT.get(month_key)
        if month is None:
            return None
        return datetime(year, month, day)
    except (ValueError, TypeError):
        return None


def _sheet_to_df(worksheet: gspread.Worksheet, year: int) -> pd.DataFrame:
    """
    Lê a worksheet e retorna um DataFrame limpo com os registros de serviços.
    Ignora as primeiras 3 linhas (metadados/cabeçalhos) e linhas vazias.
    """
    all_rows = worksheet.get_all_values()
    data_rows = all_rows[CLIENTES_DATA_START:]

    records = []
    for row in data_rows:
        if len(row) <= CLIENTES_COLS["data"]:
            continue

        raw_date = row[CLIENTES_COLS["data"]].strip()
        if not raw_date or raw_date in ("-", "Data"):
            continue

        date = _parse_date(raw_date, year)
        if date is None:
            continue

        def col(key):
            idx = CLIENTES_COLS[key]
            return row[idx] if idx < len(row) else ""

        records.append({
            "data":       date,
            "carro":      col("carro").strip(),
            "servico":    col("servico").strip(),
            "id":         col("id").strip(),
            "nome_peca":  col("nome_peca").strip(),
            "custo_peca": _parse_brl(col("custo_peca")),
            "venda_peca": _parse_brl(col("venda_peca")),
            "mo":         _parse_brl(col("mo")),
            "terceiros":  _parse_brl(col("terceiros")),
            "total":      _parse_brl(col("total")),
            "lucro":      _parse_brl(col("lucro")),
            "parceiro":   col("parceiro").strip(),
            "obs":        col("obs").strip(),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["data"] = pd.to_datetime(df["data"])
    df["marca"] = df["carro"].apply(_extract_brand)
    df["semana"] = df["data"].dt.isocalendar().week.astype(int)
    df["mes"] = df["data"].dt.month
    return df


def _extract_brand(carro: str) -> str:
    """Extrai a marca do campo 'carro' (ex: 'BMW M240i' → 'BMW')."""
    brands = ["BMW", "VW", "VOLKSWAGEN", "AUDI", "MINI", "PORSCHE", "MERCEDES", "TOYOTA", "HONDA"]
    upper = carro.upper()
    for b in brands:
        if upper.startswith(b):
            return b if b != "VOLKSWAGEN" else "VW"
    return carro.split()[0].upper() if carro else "Outros"


def load_clientes(year: int = 2026) -> pd.DataFrame:
    """Carrega a aba CLIENTES do ano especificado."""
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID)
    tab_key = f"clientes_{year}"
    tab_name = SHEETS[tab_key]["name"]
    ws = sheet.worksheet(tab_name)
    return _sheet_to_df(ws, year)


def load_estoque(year: int = 2026) -> pd.DataFrame:
    """Carrega a aba ESTOQUE do ano especificado."""
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID)
    tab_key = f"estoque_{year}"
    tab_name = SHEETS[tab_key]["name"]
    ws = sheet.worksheet(tab_name)
    return _sheet_to_df(ws, year)


def load_relatorios(year: int = 2026) -> list[list]:
    """Retorna os valores brutos da aba RELATÓRIOS (para histórico)."""
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID)
    tab_key = f"relatorios_{year}"
    tab_name = SHEETS[tab_key]["name"]
    ws = sheet.worksheet(tab_name)
    return ws.get_all_values()


def get_worksheet(name: str) -> gspread.Worksheet:
    """Retorna um worksheet pelo nome (para escrita no dashboard)."""
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID)
    try:
        return sheet.worksheet(name)
    except gspread.WorksheetNotFound:
        return sheet.add_worksheet(title=name, rows=200, cols=20)
