"""
email_sender.py – Envio do relatório semanal por e-mail via Gmail SMTP.

O corpo do e-mail é um HTML formatado com os KPIs resumidos.
O PDF completo é enviado como anexo.
"""

from __future__ import annotations
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime

from config.settings import (
    GMAIL_USER, GMAIL_APP_PASSWORD, DIRECTOR_EMAIL,
    GMAIL_SMTP_HOST, GMAIL_SMTP_PORT,
    COMPANY_NAME, COMPANY_TAGLINE, PRIMARY_COLOR, ACCENT_COLOR,
)


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _build_html_body(kpis: dict, analysis_text: str, stock_alerts: list[dict]) -> str:
    """Gera o corpo HTML do e-mail com KPIs e análise resumida."""
    wk = kpis
    color_blue = f"#{PRIMARY_COLOR[0]:02x}{PRIMARY_COLOR[1]:02x}{PRIMARY_COLOR[2]:02x}"
    color_cyan  = f"#{ACCENT_COLOR[0]:02x}{ACCENT_COLOR[1]:02x}{ACCENT_COLOR[2]:02x}"

    # Cards de KPI
    cards_html = ""
    cards = [
        ("Receita da Semana",  _fmt_brl(wk.get("receita", 0))),
        ("Margem de Lucro",    f"{wk.get('margem_pct', 0):.1f}%"),
        ("Total de Serviços",  str(wk.get("total_servicos", 0))),
        ("Ticket Médio",       _fmt_brl(wk.get("ticket_medio", 0))),
    ]
    for label, value in cards:
        cards_html += f"""
        <td style="text-align:center; padding:12px; background:#f5f7ff;
                   border-radius:8px; min-width:100px;">
          <div style="font-size:11px; color:#666; text-transform:uppercase;
                      letter-spacing:0.5px;">{label}</div>
          <div style="font-size:20px; font-weight:bold; color:{color_blue};
                      margin-top:4px;">{value}</div>
        </td>"""

    # Variação WoW
    wow = wk.get("crescimento_wow_receita", 0)
    wow_color = "#2e8b57" if wow >= 0 else "#c62828"
    wow_arrow = "▲" if wow >= 0 else "▼"
    wow_text = f"{wow_arrow} {abs(wow):.1f}% em relação à semana anterior"

    # Top serviços
    top_services_html = ""
    for s in wk.get("top_servicos", [])[:5]:
        top_services_html += f"""
        <tr>
          <td style="padding:6px 10px; border-bottom:1px solid #eee;">{s['nome']}</td>
          <td style="padding:6px 10px; text-align:center; border-bottom:1px solid #eee;">
            <b>{s['quantidade']}</b>
          </td>
        </tr>"""

    # Performance parceiros
    partners_html = ""
    for p in wk.get("performance_parceiros", [])[:5]:
        partners_html += f"""
        <tr>
          <td style="padding:6px 10px; border-bottom:1px solid #eee;">{p['parceiro']}</td>
          <td style="padding:6px 10px; text-align:right; border-bottom:1px solid #eee;">
            {_fmt_brl(p['receita'])}
          </td>
          <td style="padding:6px 10px; text-align:right; border-bottom:1px solid #eee;">
            {p['margem_pct']:.1f}%
          </td>
        </tr>"""

    # Alertas
    alerts_html = ""
    if stock_alerts:
        items_html = "".join(
            f'<li style="color:#c62828;">{a["item"]}</li>' for a in stock_alerts
        )
        alerts_html = f"""
        <div style="background:#fff0f0; border-left:4px solid #c62828;
                    padding:12px 16px; margin:16px 0; border-radius:4px;">
          <b style="color:#c62828;">⚠ Alertas de Estoque</b>
          <ul style="margin:8px 0 0 0; padding-left:20px;">{items_html}</ul>
        </div>"""

    # Análise resumida (primeiros 600 chars)
    short_analysis = analysis_text[:600] + ("..." if len(analysis_text) > 600 else "")
    short_analysis_html = short_analysis.replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif; max-width:680px; margin:0 auto;
             background:#f4f6f9; padding:20px;">

  <!-- Header -->
  <div style="background:{color_blue}; padding:24px 30px; border-radius:8px 8px 0 0;">
    <h1 style="color:white; margin:0; font-size:22px;">{COMPANY_NAME}</h1>
    <p style="color:{color_cyan}; margin:4px 0 0; font-size:12px;">{COMPANY_TAGLINE}</p>
  </div>

  <!-- Subtítulo -->
  <div style="background:{color_cyan}; padding:10px 30px;">
    <p style="color:white; margin:0; font-size:13px; font-weight:bold;">
      📊 Relatório Semanal – Semana {wk.get('semana_iso', '')}
      ({wk.get('periodo_inicio', '')} a {wk.get('periodo_fim', '')})
    </p>
  </div>

  <!-- Conteúdo -->
  <div style="background:white; padding:24px 30px; border-radius:0 0 8px 8px;">

    <!-- KPI Cards -->
    <table style="width:100%; border-collapse:separate; border-spacing:8px; margin-bottom:4px;">
      <tr>{cards_html}</tr>
    </table>
    <p style="text-align:center; font-size:12px; color:{wow_color}; margin:4px 0 20px;">
      {wow_text}
    </p>

    <!-- Top Serviços -->
    <h3 style="color:{color_blue}; border-bottom:2px solid {color_cyan};
               padding-bottom:6px; font-size:14px;">Top Serviços da Semana</h3>
    <table style="width:100%; border-collapse:collapse; font-size:13px;">
      <tr style="background:{color_blue}; color:white;">
        <th style="padding:8px 10px; text-align:left;">Serviço</th>
        <th style="padding:8px 10px; text-align:center;">Qtd</th>
      </tr>
      {top_services_html}
    </table>

    <!-- Parceiros -->
    <h3 style="color:{color_blue}; border-bottom:2px solid {color_cyan};
               padding-bottom:6px; font-size:14px; margin-top:20px;">Performance por Parceiro</h3>
    <table style="width:100%; border-collapse:collapse; font-size:13px;">
      <tr style="background:{color_blue}; color:white;">
        <th style="padding:8px 10px; text-align:left;">Parceiro</th>
        <th style="padding:8px 10px; text-align:right;">Receita</th>
        <th style="padding:8px 10px; text-align:right;">Margem</th>
      </tr>
      {partners_html}
    </table>

    {alerts_html}

    <!-- Análise -->
    <h3 style="color:{color_blue}; border-bottom:2px solid {color_cyan};
               padding-bottom:6px; font-size:14px; margin-top:20px;">Análise do Período</h3>
    <p style="font-size:13px; color:#444; line-height:1.6;">{short_analysis_html}</p>

    <p style="font-size:11px; color:#aaa; text-align:center; margin-top:24px;">
      O relatório completo com gráficos está em anexo (PDF).<br>
      Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
    </p>
  </div>

</body>
</html>"""


def send_weekly_report(
    pdf_path: Path,
    weekly_kpis: dict,
    analysis_text: str,
    stock_alerts: list[dict],
):
    """Envia o relatório semanal por e-mail com PDF como anexo."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not DIRECTOR_EMAIL:
        print("[AVISO] Credenciais de e-mail não configuradas. Pulando envio.")
        return

    week_n = weekly_kpis.get("semana_iso", "")
    start  = weekly_kpis.get("periodo_inicio", "")
    end    = weekly_kpis.get("periodo_fim", "")
    subject = f"Relatório Semanal {COMPANY_NAME} – Semana {week_n} ({start} a {end})"

    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_USER
    msg["To"]      = DIRECTOR_EMAIL
    msg["Subject"] = subject

    html_body = _build_html_body(weekly_kpis, analysis_text, stock_alerts)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Anexar PDF
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f'attachment; filename="{pdf_path.name}"',
        )
        msg.attach(attachment)

    with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)

    print(f"[OK] E-mail enviado para {DIRECTOR_EMAIL}")
