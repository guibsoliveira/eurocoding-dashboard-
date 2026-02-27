"""
kpi_engine.py – Cálculo de KPIs financeiros e operacionais.

Recebe DataFrames do reader.py e retorna dicionários estruturados
com todos os indicadores para uso no dashboard, relatório e análise.
"""

from __future__ import annotations
from datetime import datetime, timedelta
import pandas as pd
from config.settings import MONTHS_PT


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _safe_pct(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)


def _wow_growth(current: float, previous: float) -> float:
    """Variação percentual semana a semana."""
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


def _top_n(series: pd.Series, n: int = 5) -> list[dict]:
    """Retorna os top N valores de uma série com contagem."""
    counts = series.value_counts().head(n)
    return [{"nome": k, "quantidade": int(v)} for k, v in counts.items()]


# ─── KPIs Diários ─────────────────────────────────────────────────────────────

def daily_kpis(df: pd.DataFrame, date: datetime | None = None) -> dict:
    """KPIs do dia especificado (padrão: ontem)."""
    target = date or (datetime.today() - timedelta(days=1))
    target_date = target.date()

    day_df = df[df["data"].dt.date == target_date]

    return {
        "data": target_date.strftime("%d/%m/%Y"),
        "total_servicos": len(day_df),
        "receita": round(day_df["total"].sum(), 2),
        "custo":   round(day_df["custo_peca"].sum() + day_df["terceiros"].sum(), 2),
        "lucro":   round(day_df["lucro"].sum(), 2),
        "margem_pct": _safe_pct(day_df["lucro"].sum(), day_df["total"].sum()),
    }


# ─── KPIs Semanais ────────────────────────────────────────────────────────────

def weekly_kpis(df: pd.DataFrame, week_offset: int = 1) -> dict:
    """
    KPIs da semana.
    week_offset=1 → semana passada (padrão para relatório de segunda)
    week_offset=0 → semana atual
    """
    today = datetime.today()
    ref_monday = today - timedelta(days=today.weekday() + 7 * week_offset)
    week_start = ref_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end   = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    week_df = df[(df["data"] >= week_start) & (df["data"] <= week_end)]
    prev_start = week_start - timedelta(days=7)
    prev_end   = week_start - timedelta(seconds=1)
    prev_df = df[(df["data"] >= prev_start) & (df["data"] <= prev_end)]

    receita   = round(week_df["total"].sum(), 2)
    prev_rec  = round(prev_df["total"].sum(), 2)
    lucro     = round(week_df["lucro"].sum(), 2)
    prev_luc  = round(prev_df["lucro"].sum(), 2)
    n_servicos = len(week_df)
    ticket_medio = round(receita / n_servicos, 2) if n_servicos > 0 else 0.0

    # Receita por dia da semana
    receita_por_dia = {}
    for i in range(7):
        d = week_start + timedelta(days=i)
        ddf = week_df[week_df["data"].dt.date == d.date()]
        receita_por_dia[d.strftime("%d/%m")] = round(ddf["total"].sum(), 2)

    return {
        "periodo_inicio": week_start.strftime("%d/%m/%Y"),
        "periodo_fim":    week_end.strftime("%d/%m/%Y"),
        "semana_iso":     week_start.isocalendar()[1],
        "total_servicos": n_servicos,
        "receita":        receita,
        "custo":          round(week_df["custo_peca"].sum() + week_df["terceiros"].sum(), 2),
        "lucro":          lucro,
        "margem_pct":     _safe_pct(lucro, receita),
        "ticket_medio":   ticket_medio,
        "crescimento_wow_receita": _wow_growth(receita, prev_rec),
        "crescimento_wow_lucro":   _wow_growth(lucro, prev_luc),
        "receita_por_dia": receita_por_dia,
        "top_servicos":   _top_n(week_df["servico"], 5),
        "top_marcas":     _top_n(week_df["marca"], 5),
        "performance_parceiros": _partner_performance(week_df),
        "registros": week_df.to_dict("records"),
    }


# ─── KPIs Mensais ─────────────────────────────────────────────────────────────

def monthly_kpis(df: pd.DataFrame, month: int | None = None, year: int = 2026) -> dict:
    """KPIs do mês especificado (padrão: mês atual)."""
    month = month or datetime.today().month
    month_df = df[(df["data"].dt.month == month) & (df["data"].dt.year == year)]

    prev_month = month - 1 if month > 1 else 12
    prev_year  = year if month > 1 else year - 1
    prev_df = df[(df["data"].dt.month == prev_month) & (df["data"].dt.year == prev_year)]

    receita  = round(month_df["total"].sum(), 2)
    prev_rec = round(prev_df["total"].sum(), 2)
    lucro    = round(month_df["lucro"].sum(), 2)
    n_servicos = len(month_df)
    ticket_medio = round(receita / n_servicos, 2) if n_servicos > 0 else 0.0

    # Receita por semana do mês
    receita_por_semana = {}
    for wk in sorted(month_df["semana"].unique()):
        wdf = month_df[month_df["semana"] == wk]
        receita_por_semana[f"Sem {int(wk)}"] = round(wdf["total"].sum(), 2)

    return {
        "mes": MONTHS_PT[month].capitalize(),
        "mes_numero": month,
        "ano": year,
        "total_servicos": n_servicos,
        "receita":        receita,
        "custo":          round(month_df["custo_peca"].sum() + month_df["terceiros"].sum(), 2),
        "lucro":          lucro,
        "margem_pct":     _safe_pct(lucro, receita),
        "ticket_medio":   ticket_medio,
        "crescimento_mom": _wow_growth(receita, prev_rec),
        "receita_por_semana": receita_por_semana,
        "top_servicos":   _top_n(month_df["servico"], 5),
        "top_marcas":     _top_n(month_df["marca"], 5),
        "performance_parceiros": _partner_performance(month_df),
    }


# ─── KPIs Anuais ──────────────────────────────────────────────────────────────

def annual_kpis(df: pd.DataFrame, year: int) -> dict:
    """KPIs consolidados do ano inteiro."""
    year_df = df[df["data"].dt.year == year]
    receita = round(year_df["total"].sum(), 2)
    lucro   = round(year_df["lucro"].sum(), 2)
    n_servicos = len(year_df)

    # Receita mensal
    receita_mensal = {}
    for m in range(1, 13):
        mdf = year_df[year_df["data"].dt.month == m]
        if not mdf.empty:
            receita_mensal[MONTHS_PT[m].capitalize()] = round(mdf["total"].sum(), 2)

    return {
        "ano": year,
        "total_servicos": n_servicos,
        "receita":        receita,
        "lucro":          lucro,
        "margem_pct":     _safe_pct(lucro, receita),
        "ticket_medio":   round(receita / n_servicos, 2) if n_servicos > 0 else 0.0,
        "receita_mensal": receita_mensal,
        "top_servicos":   _top_n(year_df["servico"], 10),
        "top_marcas":     _top_n(year_df["marca"], 10),
        "performance_parceiros": _partner_performance(year_df),
    }


# ─── Performance por Parceiro ─────────────────────────────────────────────────

def _partner_performance(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    grouped = df.groupby("parceiro").agg(
        servicos=("total", "count"),
        receita=("total", "sum"),
        custo_terceiros=("terceiros", "sum"),
        lucro=("lucro", "sum"),
    ).reset_index()
    grouped = grouped.sort_values("receita", ascending=False)
    result = []
    for _, row in grouped.iterrows():
        result.append({
            "parceiro":   row["parceiro"],
            "servicos":   int(row["servicos"]),
            "receita":    round(float(row["receita"]), 2),
            "custo":      round(float(row["custo_terceiros"]), 2),
            "lucro":      round(float(row["lucro"]), 2),
            "margem_pct": _safe_pct(float(row["lucro"]), float(row["receita"])),
        })
    return result


# ─── Alertas de Estoque ───────────────────────────────────────────────────────

def stock_alerts(estoque_df: pd.DataFrame) -> list[dict]:
    """
    Retorna peças em alerta.
    Considera alerta quando Custo da peça > 0 e Valor total = 0
    (indica que a peça foi usada e pode estar em falta), ou quando
    o campo de observações menciona 'falta' / 'esgotado' / 'baixo'.
    """
    if estoque_df.empty:
        return []

    alerts = []
    for _, row in estoque_df.iterrows():
        obs = str(row.get("obs", "")).lower()
        nome = str(row.get("nome_peca", "") or row.get("servico", "")).strip()
        if not nome or nome == "-":
            continue
        is_critical = (
            "falta" in obs or "esgotad" in obs or "baixo" in obs or
            (row.get("custo_peca", 0) > 0 and row.get("total", 0) == 0)
        )
        if is_critical:
            alerts.append({
                "item":     nome,
                "parceiro": row.get("parceiro", ""),
                "obs":      row.get("obs", ""),
            })
    return alerts
