"""
analyst.py – Geração de análise executiva em português do Brasil.

Envia os KPIs calculados para a API do Claude e retorna uma narrativa
profissional e objetiva para o diretor da Eurocoding.
Nenhuma referência a IA ou Claude aparece na saída gerada.
"""

import json
import anthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, COMPANY_NAME, COMPANY_TAGLINE


def _build_weekly_prompt(kpis: dict, alerts: list[dict]) -> str:
    alerts_text = ""
    if alerts:
        items = "\n".join(f"- {a['item']}" for a in alerts)
        alerts_text = f"\nAlertas de estoque crítico:\n{items}\n"

    return f"""Você é o analista de negócios da {COMPANY_NAME}, {COMPANY_TAGLINE}.

Redija um relatório executivo semanal em português do Brasil para o diretor da empresa.
O tom deve ser profissional, direto e objetivo. Use linguagem clara, sem jargões.
Estruture exatamente assim:

**RESUMO DA SEMANA**
[2-3 frases com os números mais importantes: receita, quantidade de serviços, margem]

**DESTAQUES POSITIVOS**
[Até 3 pontos em bullets sobre o que foi bem: serviços mais realizados, parceiros, marcas]

**PONTOS DE ATENÇÃO**
[Até 2 pontos sobre o que requer atenção: queda de receita, terceiros elevados, etc.]

**PERSPECTIVA**
[1 parágrafo breve com observação estratégica sobre o período e próxima semana]

Dados da semana ({kpis.get('periodo_inicio')} a {kpis.get('periodo_fim')}):
{json.dumps(kpis, ensure_ascii=False, indent=2)}
{alerts_text}

Importante: use valores em R$ formatados (ex: R$ 1.500,00). Não mencione ferramentas ou sistemas de análise.
"""


def _build_daily_prompt(kpis: dict) -> str:
    return f"""Você é o analista de negócios da {COMPANY_NAME}, {COMPANY_TAGLINE}.

Escreva um resumo executivo BREVE do dia {kpis.get('data')} em português do Brasil.
Máximo de 3 parágrafos curtos. Tom profissional e direto.

Inclua: total de serviços realizados, receita do dia, margem de lucro.
Se não houve movimentação, informe isso de forma objetiva.

Dados do dia:
{json.dumps(kpis, ensure_ascii=False, indent=2)}

Não mencione ferramentas, sistemas ou fontes de análise.
"""


def _build_annual_prompt(kpis_2025: dict, kpis_2026_partial: dict | None = None) -> str:
    comparison = ""
    if kpis_2026_partial:
        comparison = f"\nDados parciais de 2026 (para comparação):\n{json.dumps(kpis_2026_partial, ensure_ascii=False, indent=2)}"

    return f"""Você é o analista de negócios da {COMPANY_NAME}, {COMPANY_TAGLINE}.

Redija um balanço anual completo de 2025 em português do Brasil para o diretor.
Tom profissional e estratégico. Estruture assim:

**BALANÇO ANUAL 2025**

**Resumo do Ano**
[Principais números: receita total, total de serviços, margem, ticket médio]

**Evolução Mensal**
[Destaque os meses de maior e menor receita, tendências observadas]

**Serviços e Especialidades**
[Quais serviços dominaram o portfólio da empresa]

**Performance por Parceiro**
[Análise da contribuição de cada parceiro]

**Principais Conquistas**
[3 pontos de destaque do ano]

**Oportunidades para 2026**
[2-3 recomendações baseadas nos dados de 2025]

Dados anuais de 2025:
{json.dumps(kpis_2025, ensure_ascii=False, indent=2)}
{comparison}

Use R$ formatado. Não mencione ferramentas ou sistemas de análise.
"""


def generate_weekly_analysis(kpis: dict, alerts: list[dict]) -> str:
    """Gera a análise executiva semanal."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_weekly_prompt(kpis, alerts)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_daily_analysis(kpis: dict) -> str:
    """Gera o resumo executivo diário."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_daily_prompt(kpis)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_annual_analysis(kpis_2025: dict, kpis_2026_partial: dict | None = None) -> str:
    """Gera o balanço anual de 2025."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_annual_prompt(kpis_2025, kpis_2026_partial)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
