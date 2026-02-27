"""
report_generator.py – Geração de relatório PDF semanal e anual.

Usa matplotlib para gráficos e fpdf2 para composição do PDF.
Output: reports/2026/{mes}/semana_{n}_{YYYY-MM-DD}.pdf
        reports/historico_2025/resumo_anual_2025.pdf
"""

from __future__ import annotations
import os
import io
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from config.settings import (
    COMPANY_NAME, COMPANY_TAGLINE, MONTHS_PT,
    REPORTS_DIR, REPORTS_2025_DIR, PRIMARY_COLOR, ACCENT_COLOR,
)

# ─── Cores (0-1 float para matplotlib, 0-255 para fpdf) ──────────────────────
_MPL_BLUE  = tuple(c / 255 for c in PRIMARY_COLOR)   # (0.102, 0.137, 0.494)
_MPL_CYAN  = tuple(c / 255 for c in ACCENT_COLOR)    # (0.0, 0.737, 0.831)
_MPL_GRAY  = (0.85, 0.85, 0.85)


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ─── Gráficos ─────────────────────────────────────────────────────────────────

def _chart_daily_revenue(receita_por_dia: dict) -> bytes:
    """Gráfico de barras: receita por dia da semana."""
    dates = list(receita_por_dia.keys())
    values = list(receita_por_dia.values())

    fig, ax = plt.subplots(figsize=(8, 3.5))
    bars = ax.bar(dates, values, color=_MPL_BLUE, edgecolor="white", linewidth=0.5)
    ax.bar_label(bars, labels=[_fmt_brl(v) for v in values], padding=4,
                 fontsize=7, color="#333333")
    ax.set_title("Receita por Dia da Semana", fontsize=12, pad=10, color="#1a237e")
    ax.set_ylabel("R$", fontsize=9)
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _chart_top_services(top_servicos: list[dict]) -> bytes:
    """Gráfico de pizza: top serviços."""
    if not top_servicos:
        return b""
    labels = [s["nome"] for s in top_servicos]
    sizes  = [s["quantidade"] for s in top_servicos]
    colors = [_MPL_BLUE, _MPL_CYAN, (0.2, 0.6, 0.4), (0.9, 0.7, 0.1), (0.7, 0.3, 0.3)]

    fig, ax = plt.subplots(figsize=(5.5, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors[:len(labels)],
        autopct="%1.0f%%", startangle=140,
        textprops={"fontsize": 9},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Serviços Realizados", fontsize=11, color="#1a237e")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _chart_partners(partners: list[dict]) -> bytes:
    """Gráfico de barras horizontais: receita por parceiro."""
    if not partners:
        return b""
    names   = [p["parceiro"] for p in partners]
    receita = [p["receita"] for p in partners]

    fig, ax = plt.subplots(figsize=(7, max(2.5, len(names) * 0.6)))
    bars = ax.barh(names, receita, color=_MPL_CYAN, edgecolor="white")
    ax.bar_label(bars, labels=[_fmt_brl(v) for v in receita],
                 padding=5, fontsize=8, color="#333333")
    ax.set_title("Receita por Parceiro", fontsize=11, color="#1a237e")
    ax.set_xlabel("R$", fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _chart_monthly_revenue(receita_mensal: dict) -> bytes:
    """Gráfico de barras: receita mensal do ano."""
    if not receita_mensal:
        return b""
    months = list(receita_mensal.keys())
    values = list(receita_mensal.values())

    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(months, values, color=_MPL_BLUE, edgecolor="white")
    ax.bar_label(bars, labels=[_fmt_brl(v) for v in values],
                 padding=4, fontsize=7, rotation=45, color="#333333")
    ax.set_title("Receita Mensal 2025", fontsize=12, color="#1a237e")
    ax.set_ylabel("R$", fontsize=9)
    ax.tick_params(axis="x", labelsize=8, rotation=30)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


# ─── PDF Builder ──────────────────────────────────────────────────────────────

class _EurocodingPDF(FPDF):
    def __init__(self, title: str):
        super().__init__()
        self._title = title
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*PRIMARY_COLOR)
        self.rect(0, 0, 210, 12, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 3)
        self.cell(0, 6, f"{COMPANY_NAME}  |  {self._title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"Página {self.page_no()}", align="C")

    def cover_page(self, subtitle: str, period: str):
        self.add_page()
        # Fundo azul escuro
        self.set_fill_color(*PRIMARY_COLOR)
        self.rect(0, 0, 210, 297, "F")
        # Logo / Nome
        self.set_font("Helvetica", "B", 36)
        self.set_text_color(*ACCENT_COLOR)
        self.set_y(80)
        self.cell(0, 20, COMPANY_NAME.upper(), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 13)
        self.set_text_color(220, 220, 220)
        self.cell(0, 8, COMPANY_TAGLINE, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Linha divisória
        self.ln(8)
        self.set_draw_color(*ACCENT_COLOR)
        self.set_line_width(0.8)
        self.line(40, self.get_y(), 170, self.get_y())
        self.ln(12)
        # Título do relatório
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, subtitle, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(200, 200, 200)
        self.cell(0, 8, period, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        # Data de geração
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(170, 170, 170)
        self.cell(0, 6, f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section_title(self, text: str):
        self.set_fill_color(*PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {text}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def kpi_cards(self, cards: list[dict]):
        """Renderiza cards de KPI em linha."""
        card_w = (self.epw - 6 * (len(cards) - 1)) / len(cards)
        x_start = self.l_margin
        y = self.get_y()
        for i, card in enumerate(cards):
            x = x_start + i * (card_w + 6)
            self.set_fill_color(245, 247, 255)
            self.set_draw_color(*ACCENT_COLOR)
            self.set_line_width(0.4)
            self.rect(x, y, card_w, 22, "FD")
            self.set_xy(x + 2, y + 2)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(100, 100, 100)
            self.cell(card_w - 4, 4, card["label"].upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_xy(x + 2, y + 7)
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(*PRIMARY_COLOR)
            self.cell(card_w - 4, 8, card["value"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if "delta" in card:
                self.set_xy(x + 2, y + 16)
                self.set_font("Helvetica", "", 8)
                color = (30, 140, 90) if card.get("delta_positive", True) else (200, 40, 40)
                self.set_text_color(*color)
                self.cell(card_w - 4, 5, card["delta"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(y + 26)
        self.set_text_color(0, 0, 0)

    def add_image_bytes(self, img_bytes: bytes, w: float = 170):
        if not img_bytes:
            return
        import tempfile, uuid
        tmp = Path(tempfile.gettempdir()) / f"eurocoding_{uuid.uuid4().hex}.png"
        tmp.write_bytes(img_bytes)
        self.image(str(tmp), x=self.l_margin, w=w)
        tmp.unlink(missing_ok=True)
        self.ln(4)

    def analysis_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(4)

    def records_table(self, records: list[dict]):
        """Tabela com os registros da semana."""
        headers = ["Data", "Carro", "Serviço", "Parceiro", "Total", "Lucro"]
        col_widths = [22, 45, 52, 30, 25, 22]

        self.set_fill_color(*ACCENT_COLOR)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8)
        for h, w in zip(headers, col_widths):
            self.cell(w, 7, h, fill=True, border=0)
        self.ln()

        self.set_font("Helvetica", "", 7.5)
        for i, rec in enumerate(records):
            self.set_fill_color(245, 247, 255) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_text_color(40, 40, 40)
            date_str = rec["data"].strftime("%d/%m") if hasattr(rec["data"], "strftime") else str(rec["data"])[:5]
            row_data = [
                date_str,
                str(rec.get("carro", ""))[:22],
                str(rec.get("servico", ""))[:28],
                str(rec.get("parceiro", ""))[:16],
                _fmt_brl(rec.get("total", 0)),
                _fmt_brl(rec.get("lucro", 0)),
            ]
            for val, w in zip(row_data, col_widths):
                self.cell(w, 6, val, fill=True, border=0)
            self.ln()
        self.ln(4)

    def alerts_block(self, alerts: list[dict]):
        if not alerts:
            return
        self.set_fill_color(255, 235, 235)
        self.set_draw_color(200, 40, 40)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(200, 40, 40)
        self.cell(0, 8, "  ⚠  ALERTAS DE ESTOQUE", fill=True, border=1,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 0, 0)
        for a in alerts:
            self.cell(0, 6, f"  • {a['item']}  {a.get('obs', '')}",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(4)


# ─── Geração de Relatórios ────────────────────────────────────────────────────

def _get_report_path(week_kpis: dict) -> Path:
    period_start = datetime.strptime(week_kpis["periodo_inicio"], "%d/%m/%Y")
    year = period_start.year
    month_name = MONTHS_PT[period_start.month]
    week_n = week_kpis["semana_iso"]
    date_str = period_start.strftime("%Y-%m-%d")
    path = Path(REPORTS_DIR) / str(year) / month_name
    path.mkdir(parents=True, exist_ok=True)
    return path / f"semana_{week_n:02d}_{date_str}.pdf"


def generate_weekly_report(
    weekly_kpis: dict,
    monthly_kpis: dict,
    analysis_text: str,
    stock_alerts: list[dict],
) -> Path:
    """Gera o PDF do relatório semanal e retorna o caminho do arquivo."""
    period = f"{weekly_kpis['periodo_inicio']} a {weekly_kpis['periodo_fim']}"
    week_n = weekly_kpis["semana_iso"]

    pdf = _EurocodingPDF(f"Relatório Semanal – Semana {week_n}")
    pdf.cover_page(f"Relatório Semanal", f"Semana {week_n}  ·  {period}")
    pdf.add_page()

    # KPI Cards
    pdf.section_title("Indicadores da Semana")
    wk = weekly_kpis
    wow_r = wk.get("crescimento_wow_receita", 0)
    cards = [
        {"label": "Receita", "value": _fmt_brl(wk["receita"]),
         "delta": f"{'▲' if wow_r >= 0 else '▼'} {abs(wow_r):.1f}% vs semana anterior",
         "delta_positive": wow_r >= 0},
        {"label": "Margem de Lucro", "value": f"{wk['margem_pct']:.1f}%"},
        {"label": "Serviços", "value": str(wk["total_servicos"])},
        {"label": "Ticket Médio", "value": _fmt_brl(wk["ticket_medio"])},
    ]
    pdf.kpi_cards(cards)

    # Gráfico receita diária
    pdf.section_title("Receita por Dia")
    chart = _chart_daily_revenue(wk.get("receita_por_dia", {}))
    pdf.add_image_bytes(chart, w=175)

    # Gráficos serviços + parceiros lado a lado
    pdf.section_title("Serviços e Parceiros")
    chart_s = _chart_top_services(wk.get("top_servicos", []))
    chart_p = _chart_partners(wk.get("performance_parceiros", []))
    if chart_s:
        pdf.add_image_bytes(chart_s, w=85)
    if chart_p:
        pdf.add_image_bytes(chart_p, w=85)

    # Análise do período
    pdf.add_page()
    pdf.section_title("Análise do Período")
    pdf.analysis_text(analysis_text)

    # Tabela de registros
    records = wk.get("registros", [])
    if records:
        pdf.section_title(f"Serviços Realizados ({len(records)} registros)")
        pdf.records_table(records)

    # Alertas de estoque
    if stock_alerts:
        pdf.alerts_block(stock_alerts)

    output_path = _get_report_path(weekly_kpis)
    pdf.output(str(output_path))
    print(f"[OK] Relatório semanal gerado: {output_path}")
    return output_path


def generate_annual_report(annual_kpis: dict, analysis_text: str) -> Path:
    """Gera o PDF do balanço anual de 2025."""
    year = annual_kpis.get("ano", 2025)
    path = Path(REPORTS_2025_DIR)
    path.mkdir(parents=True, exist_ok=True)
    output_path = path / f"resumo_anual_{year}.pdf"

    pdf = _EurocodingPDF(f"Balanço Anual {year}")
    pdf.cover_page(f"Balanço Anual {year}", "Resumo Completo de Desempenho")
    pdf.add_page()

    # KPI Cards anuais
    pdf.section_title(f"Indicadores do Ano {year}")
    cards = [
        {"label": "Receita Total", "value": _fmt_brl(annual_kpis["receita"])},
        {"label": "Lucro Total",   "value": _fmt_brl(annual_kpis["lucro"])},
        {"label": "Margem Média",  "value": f"{annual_kpis['margem_pct']:.1f}%"},
        {"label": "Total de Serviços", "value": str(annual_kpis["total_servicos"])},
    ]
    pdf.kpi_cards(cards)

    # Gráfico mensal
    pdf.section_title("Evolução Mensal da Receita")
    chart = _chart_monthly_revenue(annual_kpis.get("receita_mensal", {}))
    pdf.add_image_bytes(chart, w=175)

    # Gráficos serviços + parceiros
    pdf.section_title("Serviços Realizados no Ano")
    chart_s = _chart_top_services(annual_kpis.get("top_servicos", []))
    if chart_s:
        pdf.add_image_bytes(chart_s, w=110)

    pdf.section_title("Performance por Parceiro")
    chart_p = _chart_partners(annual_kpis.get("performance_parceiros", []))
    if chart_p:
        pdf.add_image_bytes(chart_p, w=175)

    # Análise
    pdf.add_page()
    pdf.section_title(f"Análise Executiva – {year}")
    pdf.analysis_text(analysis_text)

    pdf.output(str(output_path))
    print(f"[OK] Balanço anual gerado: {output_path}")
    return output_path
