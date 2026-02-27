"""
run.py – Orquestrador principal do sistema de dashboard Eurocoding.

Modos de execução:
  --mode daily       Atualiza o PAINEL EXECUTIVO no Google Sheets (agendado: todo dia 08h)
  --mode weekly      Gera relatório PDF + envia por e-mail (agendado: toda segunda-feira 08h)
  --mode summary2025 Gera o balanço anual de 2025 em PDF (executar uma única vez)
  --mode manual      Roda tudo sem enviar e-mail (para testes e uso ad-hoc)

Agendamento sugerido (Windows Task Scheduler):
  08:00 todo dia       → py run.py --mode daily
  08:00 toda segunda   → py run.py --mode weekly
"""

import argparse
import sys
from datetime import datetime

from src.reader import load_clientes, load_estoque
from src.kpi_engine import daily_kpis, weekly_kpis, monthly_kpis, annual_kpis, stock_alerts
from src.analyst import generate_daily_analysis, generate_weekly_analysis, generate_annual_analysis
from src.dashboard_writer import update_dashboard
from src.report_generator import generate_weekly_report, generate_annual_report
from src.email_sender import send_weekly_report


def run_daily():
    """Atualiza o PAINEL EXECUTIVO com dados do dia."""
    print(f"\n{'='*50}")
    print(f"  EUROCODING – Atualização Diária  {datetime.now().strftime('%d/%m/%Y')}")
    print(f"{'='*50}")

    print("[1/5] Lendo planilha 2026...")
    df_clientes = load_clientes(2026)
    df_estoque  = load_estoque(2026)

    print("[2/5] Calculando KPIs...")
    kpi_day     = daily_kpis(df_clientes)
    kpi_week    = weekly_kpis(df_clientes, week_offset=0)
    kpi_month   = monthly_kpis(df_clientes, year=2026)
    alerts      = stock_alerts(df_estoque)

    print("[3/5] Gerando análise do período...")
    analysis = generate_daily_analysis(kpi_day)

    print("[4/5] Atualizando PAINEL EXECUTIVO no Google Sheets...")
    update_dashboard(kpi_week, kpi_month, alerts, analysis)

    print("[5/5] Pronto!")
    print(f"  Receita do dia: R$ {kpi_day['receita']:,.2f}")
    print(f"  Serviços: {kpi_day['total_servicos']}")
    print(f"  Margem: {kpi_day['margem_pct']}%")
    if alerts:
        print(f"  ⚠ {len(alerts)} alerta(s) de estoque")


def run_weekly(send_email: bool = True):
    """Gera relatório semanal, salva PDF e envia por e-mail."""
    print(f"\n{'='*50}")
    print(f"  EUROCODING – Relatório Semanal  {datetime.now().strftime('%d/%m/%Y')}")
    print(f"{'='*50}")

    print("[1/6] Lendo planilha 2026...")
    df_clientes = load_clientes(2026)
    df_estoque  = load_estoque(2026)

    print("[2/6] Calculando KPIs semanais e mensais...")
    kpi_week  = weekly_kpis(df_clientes, week_offset=1)
    kpi_month = monthly_kpis(df_clientes, year=2026)
    alerts    = stock_alerts(df_estoque)

    print("[3/6] Gerando análise executiva...")
    analysis = generate_weekly_analysis(kpi_week, alerts)

    print("[4/6] Atualizando PAINEL EXECUTIVO no Google Sheets...")
    update_dashboard(kpi_week, kpi_month, alerts, analysis)

    print("[5/6] Gerando relatório PDF...")
    pdf_path = generate_weekly_report(kpi_week, kpi_month, analysis, alerts)

    if send_email:
        print("[6/6] Enviando e-mail ao diretor...")
        send_weekly_report(pdf_path, kpi_week, analysis, alerts)
    else:
        print("[6/6] Envio de e-mail ignorado (modo manual).")

    print(f"\n  Relatório salvo em: {pdf_path}")
    print(f"  Período: {kpi_week['periodo_inicio']} a {kpi_week['periodo_fim']}")
    print(f"  Receita: R$ {kpi_week['receita']:,.2f}  |  Margem: {kpi_week['margem_pct']}%")
    print(f"  Serviços: {kpi_week['total_servicos']}  |  Ticket médio: R$ {kpi_week['ticket_medio']:,.2f}")


def run_summary_2025():
    """Gera o balanço anual de 2025 (executar uma única vez)."""
    print(f"\n{'='*50}")
    print(f"  EUROCODING – Balanço Anual 2025")
    print(f"{'='*50}")

    print("[1/4] Lendo planilha 2025...")
    df_clientes_2025 = load_clientes(2025)
    df_clientes_2026 = load_clientes(2026)

    print("[2/4] Calculando KPIs anuais...")
    kpi_2025         = annual_kpis(df_clientes_2025, 2025)
    kpi_2026_partial = annual_kpis(df_clientes_2026, 2026)

    print("[3/4] Gerando análise executiva anual...")
    analysis = generate_annual_analysis(kpi_2025, kpi_2026_partial)

    print("[4/4] Gerando PDF do balanço anual...")
    pdf_path = generate_annual_report(kpi_2025, analysis)

    print(f"\n  Balanço anual 2025 salvo em: {pdf_path}")
    print(f"  Receita total 2025: R$ {kpi_2025['receita']:,.2f}")
    print(f"  Lucro total 2025:   R$ {kpi_2025['lucro']:,.2f}")
    print(f"  Total de serviços:  {kpi_2025['total_servicos']}")


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Dashboard Automatizado – Eurocoding"
    )
    parser.add_argument(
        "--mode",
        choices=["daily", "weekly", "summary2025", "manual"],
        required=True,
        help=(
            "daily: atualiza painel (todo dia 08h) | "
            "weekly: relatório + e-mail (toda segunda 08h) | "
            "summary2025: balanço anual 2025 | "
            "manual: execução completa sem enviar e-mail"
        ),
    )
    args = parser.parse_args()

    try:
        if args.mode == "daily":
            run_daily()
        elif args.mode == "weekly":
            run_weekly(send_email=True)
        elif args.mode == "summary2025":
            run_summary_2025()
        elif args.mode == "manual":
            run_weekly(send_email=False)
    except KeyboardInterrupt:
        print("\n[Interrompido pelo usuário]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERRO] {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()
