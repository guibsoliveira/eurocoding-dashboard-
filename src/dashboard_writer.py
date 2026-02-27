"""
dashboard_writer.py – Escrita e formatação da aba PAINEL EXECUTIVO no Google Sheets.

Atualiza (ou cria) a aba com KPIs formatados, tabelas de ranking e
análise do período. Os gráficos nativos do Sheets são criados via
Google Sheets API batchUpdate na primeira execução e atualizados
automaticamente pelas referências de intervalo.
"""

from __future__ import annotations
import gspread
from datetime import datetime
from gspread.utils import rowcol_to_a1
from config.settings import COMPANY_NAME, PRIMARY_COLOR, ACCENT_COLOR, SHEETS
from src.reader import get_worksheet

# ─── Cores (formato hex para gspread) ────────────────────────────────────────
_DARK_BLUE   = {"red": 0.102, "green": 0.137, "blue": 0.494}  # #1a237e
_CYAN        = {"red": 0.0,   "green": 0.737, "blue": 0.831}  # #00bcd4
_WHITE       = {"red": 1.0,   "green": 1.0,   "blue": 1.0}
_LIGHT_GRAY  = {"red": 0.949, "green": 0.949, "blue": 0.949}  # #f2f2f2
_GREEN       = {"red": 0.18,  "green": 0.545, "blue": 0.341}  # #2e8b57
_RED         = {"red": 0.776, "green": 0.157, "blue": 0.157}  # #c62828
_YELLOW      = {"red": 1.0,   "green": 0.843, "blue": 0.0}    # #ffd700
_DARK_TEXT   = {"red": 0.2,   "green": 0.2,   "blue": 0.2}


def _fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_pct(value: float) -> str:
    arrow = "▲" if value >= 0 else "▼"
    return f"{arrow} {abs(value):.1f}%"


def _cell_format(
    bg: dict | None = None,
    bold: bool = False,
    font_size: int = 10,
    fg: dict | None = None,
    h_align: str = "LEFT",
) -> dict:
    fmt = {
        "textFormat": {
            "bold": bold,
            "fontSize": font_size,
            "foregroundColor": fg or _DARK_TEXT,
        },
        "horizontalAlignment": h_align,
        "verticalAlignment": "MIDDLE",
        "wrapStrategy": "WRAP",
    }
    if bg:
        fmt["backgroundColor"] = bg
    return fmt


# ─── Write helpers ────────────────────────────────────────────────────────────

def _write_range(ws: gspread.Worksheet, row: int, col: int, data: list[list]):
    """Escreve uma grade de dados a partir de (row, col) [1-indexed]."""
    if not data:
        return
    end_row = row + len(data) - 1
    end_col = col + max(len(r) for r in data) - 1
    rng = f"{rowcol_to_a1(row, col)}:{rowcol_to_a1(end_row, end_col)}"
    ws.update(rng, data, value_input_option="USER_ENTERED")


def _batch_format(ws: gspread.Worksheet, requests: list[dict]):
    """Aplica formatos em lote via Sheets API."""
    if not requests:
        return
    ws.spreadsheet.batch_update({"requests": requests})


def _format_range_request(ws: gspread.Worksheet, r1: int, c1: int, r2: int, c2: int, fmt: dict) -> dict:
    return {
        "repeatCell": {
            "range": {
                "sheetId": ws.id,
                "startRowIndex": r1 - 1,
                "endRowIndex": r2,
                "startColumnIndex": c1 - 1,
                "endColumnIndex": c2,
            },
            "cell": {"userEnteredFormat": fmt},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)",
        }
    }


# ─── Dashboard principal ──────────────────────────────────────────────────────

def update_dashboard(
    weekly_kpis: dict,
    monthly_kpis: dict,
    stock_alerts: list[dict],
    analysis_text: str,
):
    """
    Atualiza (ou cria) a aba PAINEL EXECUTIVO com todos os dados do período.
    """
    ws = get_worksheet(SHEETS["painel"]["name"])
    ws.clear()

    now = datetime.now().strftime("%d/%m/%Y às %H:%M")
    rows_written: list[tuple[int, int, list[list]]] = []  # (row, col, data)
    fmt_requests: list[dict] = []

    row = 1

    # ── Cabeçalho ──────────────────────────────────────────────────────────────
    _write_range(ws, row, 1, [
        [f"🚗 {COMPANY_NAME.upper()} – PAINEL EXECUTIVO 2026"],
        [f"Atualizado em: {now}"],
        [""],
    ])
    fmt_requests.append(_format_range_request(ws, row, 1, row, 6,
        _cell_format(bg=_DARK_BLUE, bold=True, font_size=14, fg=_WHITE, h_align="CENTER")))
    fmt_requests.append(_format_range_request(ws, row + 1, 1, row + 1, 6,
        _cell_format(bg=_CYAN, font_size=9, fg=_WHITE, h_align="CENTER")))
    row += 3

    # ── Bloco KPIs Financeiros ────────────────────────────────────────────────
    wk = weekly_kpis
    mo = monthly_kpis

    kpi_headers = [["RECEITA SEMANA", "MARGEM SEMANA", "SERVIÇOS SEMANA", "TICKET MÉDIO",
                     "RECEITA MÊS", "MARGEM MÊS"]]
    kpi_values = [[
        _fmt_brl(wk.get("receita", 0)),
        f"{wk.get('margem_pct', 0):.1f}%",
        str(wk.get("total_servicos", 0)),
        _fmt_brl(wk.get("ticket_medio", 0)),
        _fmt_brl(mo.get("receita", 0)),
        f"{mo.get('margem_pct', 0):.1f}%",
    ]]
    growth_row = [[
        _fmt_pct(wk.get("crescimento_wow_receita", 0)),
        "",
        "",
        "",
        _fmt_pct(mo.get("crescimento_mom", 0)),
        "",
    ]]

    _write_range(ws, row, 1, kpi_headers + kpi_values + growth_row)
    fmt_requests.append(_format_range_request(ws, row, 1, row, 6,
        _cell_format(bg=_DARK_BLUE, bold=True, font_size=9, fg=_WHITE, h_align="CENTER")))
    fmt_requests.append(_format_range_request(ws, row + 1, 1, row + 1, 6,
        _cell_format(bg=_LIGHT_GRAY, bold=True, font_size=12, h_align="CENTER")))

    # Colorir crescimento positivo/negativo
    wow_r = wk.get("crescimento_wow_receita", 0)
    mom_r = mo.get("crescimento_mom", 0)
    for col_idx, val in [(1, wow_r), (5, mom_r)]:
        color = _GREEN if val >= 0 else _RED
        fmt_requests.append(_format_range_request(ws, row + 2, col_idx, row + 2, col_idx,
            _cell_format(fg=color, bold=True, h_align="CENTER")))

    row += 4

    # ── Top Serviços e Marcas ──────────────────────────────────────────────────
    _write_range(ws, row, 1, [["📊 TOP SERVIÇOS (SEMANA)", "", "", "🚗 TOP MARCAS (SEMANA)"]])
    fmt_requests.append(_format_range_request(ws, row, 1, row, 4,
        _cell_format(bg=_DARK_BLUE, bold=True, fg=_WHITE, h_align="CENTER")))
    row += 1

    top_s = wk.get("top_servicos", [])
    top_m = wk.get("top_marcas", [])
    max_rows = max(len(top_s), len(top_m), 1)

    table_data = []
    for i in range(max_rows):
        s = top_s[i] if i < len(top_s) else {"nome": "", "quantidade": ""}
        m = top_m[i] if i < len(top_m) else {"nome": "", "quantidade": ""}
        table_data.append([s["nome"], str(s["quantidade"]) if s["nome"] else "",
                           "", m["nome"], str(m["quantidade"]) if m["nome"] else ""])

    _write_range(ws, row, 1, table_data)
    for r_offset in range(max_rows):
        bg = _WHITE if r_offset % 2 == 0 else _LIGHT_GRAY
        fmt_requests.append(_format_range_request(ws, row + r_offset, 1, row + r_offset, 5,
            _cell_format(bg=bg)))
    row += max_rows + 1

    # ── Performance Parceiros ─────────────────────────────────────────────────
    _write_range(ws, row, 1, [["🤝 PERFORMANCE POR PARCEIRO (SEMANA)"]])
    fmt_requests.append(_format_range_request(ws, row, 1, row, 5,
        _cell_format(bg=_DARK_BLUE, bold=True, fg=_WHITE, h_align="CENTER")))
    row += 1

    partner_header = [["Parceiro", "Serviços", "Receita", "Custo Terceiros", "Lucro", "Margem"]]
    _write_range(ws, row, 1, partner_header)
    fmt_requests.append(_format_range_request(ws, row, 1, row, 6,
        _cell_format(bg=_CYAN, bold=True, fg=_WHITE, h_align="CENTER")))
    row += 1

    partners = wk.get("performance_parceiros", [])
    for i, p in enumerate(partners):
        bg = _WHITE if i % 2 == 0 else _LIGHT_GRAY
        _write_range(ws, row, 1, [[
            p["parceiro"],
            str(p["servicos"]),
            _fmt_brl(p["receita"]),
            _fmt_brl(p["custo"]),
            _fmt_brl(p["lucro"]),
            f"{p['margem_pct']:.1f}%",
        ]])
        fmt_requests.append(_format_range_request(ws, row, 1, row, 6, _cell_format(bg=bg)))
        row += 1
    row += 1

    # ── Análise do Período ────────────────────────────────────────────────────
    _write_range(ws, row, 1, [["📋 ANÁLISE DO PERÍODO"]])
    fmt_requests.append(_format_range_request(ws, row, 1, row, 6,
        _cell_format(bg=_DARK_BLUE, bold=True, fg=_WHITE)))
    row += 1

    analysis_lines = analysis_text.split("\n")
    for line in analysis_lines:
        _write_range(ws, row, 1, [[line]])
        row += 1
    row += 1

    # ── Alertas de Estoque ────────────────────────────────────────────────────
    if stock_alerts:
        _write_range(ws, row, 1, [["⚠️ ALERTAS DE ESTOQUE"]])
        fmt_requests.append(_format_range_request(ws, row, 1, row, 6,
            _cell_format(bg=_RED, bold=True, fg=_WHITE)))
        row += 1
        for alert in stock_alerts:
            _write_range(ws, row, 1, [[f"🔴 {alert['item']}", alert.get("obs", "")]])
            fmt_requests.append(_format_range_request(ws, row, 1, row, 2,
                _cell_format(bg={"red": 1.0, "green": 0.9, "blue": 0.9})))
            row += 1

    # Aplicar todos os formatos em lote
    _batch_format(ws, fmt_requests)

    # Ajustar largura das colunas
    try:
        ws.spreadsheet.batch_update({"requests": [
            {"updateDimensionProperties": {
                "range": {"sheetId": ws.id, "dimension": "COLUMNS",
                          "startIndex": 0, "endIndex": 6},
                "properties": {"pixelSize": 180},
                "fields": "pixelSize",
            }},
        ]})
    except Exception:
        pass

    print(f"[OK] PAINEL EXECUTIVO atualizado em {now}")
