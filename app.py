"""
app.py – Interface web Eurocoding Dashboard

Como usar:
  Duplo clique em start.bat  OU  py -m streamlit run app.py

Páginas:
  🚀 Executar   – botões para rodar cada modo + log em tempo real
  📊 KPIs       – métricas ao vivo direto da planilha
  📁 Relatórios – lista e download dos PDFs gerados
  📦 Git        – commit e push sem abrir o terminal
  🔧 Setup      – checklist de configuração
"""

import sys
import subprocess
import time
import os
import importlib
from pathlib import Path
from datetime import datetime

import streamlit as st

# ─── Config da página ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Eurocoding Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).parent

# ─── CSS customizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Remove padding do topo */
  .block-container { padding-top: 1rem !important; }

  /* Botões de ação grandes */
  .stButton > button {
    width: 100%;
    height: 80px;
    font-size: 15px;
    font-weight: bold;
    border-radius: 10px;
    border: 2px solid #CC0000;
    background-color: #1A1A1A;
    color: #FFD700;
    transition: all 0.2s ease;
  }
  .stButton > button:hover {
    background-color: #CC0000;
    color: #FFD700;
    border-color: #FFD700;
    transform: scale(1.02);
  }

  /* Cards de KPI */
  .kpi-card {
    background: #1A1A1A;
    border: 1px solid #CC0000;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 8px;
  }
  .kpi-label { color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
  .kpi-value { color: #FFD700; font-size: 28px; font-weight: bold; margin: 6px 0; }
  .kpi-delta-pos { color: #4CAF50; font-size: 12px; }
  .kpi-delta-neg { color: #CC0000; font-size: 12px; }

  /* Log de execução */
  .log-box {
    background: #0A0A0A;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 12px;
    font-family: monospace;
    font-size: 13px;
    color: #00FF41;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
  }

  /* Linha separadora vermelha */
  hr { border-color: #CC0000 !important; }

  /* Status badges */
  .badge-ok  { color: #4CAF50; font-weight: bold; }
  .badge-err { color: #CC0000; font-weight: bold; }
  .badge-warn{ color: #FFD700; font-weight: bold; }

  /* Sidebar */
  section[data-testid="stSidebar"] { background-color: #0D0D0D; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo (renomeie seu arquivo para logo.png na pasta do projeto)
    logo_path = PROJECT_ROOT / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:16px 0 8px;">
          <span style="color:#CC0000; font-size:28px; font-weight:900;">EURO</span><span style="color:#FFD700; font-size:28px; font-weight:900;">CODING</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#999; font-size:11px; text-align:center;'>Especialista em Retrofit e<br>Tecnologia Automotiva Premium</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    pagina = st.radio(
        "Navegação",
        ["🚀 Executar", "📊 KPIs ao Vivo", "📁 Relatórios", "📦 Git & Versões", "🔧 Setup & Status"],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#555; font-size:10px; text-align:center;'>v1.0 · {datetime.now().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)


# ─── Helper: rodar subprocesso e capturar saída ───────────────────────────────
def _run_mode(mode: str, placeholder, token: str = ""):
    """Executa run.py --mode {mode} e transmite saída linha a linha."""
    env = os.environ.copy()

    cmd = [sys.executable, str(PROJECT_ROOT / "run.py"), "--mode", mode]
    lines = [f"▶ Iniciando modo: {mode}  [{datetime.now().strftime('%H:%M:%S')}]", ""]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
        )
        for line in proc.stdout:
            lines.append(line.rstrip())
            placeholder.markdown(
                f'<div class="log-box">' + "\n".join(lines[-60:]) + "</div>",
                unsafe_allow_html=True,
            )
        proc.wait()
        success = proc.returncode == 0
    except Exception as e:
        lines.append(f"ERRO: {e}")
        success = False

    lines.append("")
    lines.append("✅ Concluído com sucesso!" if success else "❌ Erro durante a execução.")
    placeholder.markdown(
        f'<div class="log-box">' + "\n".join(lines[-60:]) + "</div>",
        unsafe_allow_html=True,
    )
    return success


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 1 – EXECUTAR
# ═══════════════════════════════════════════════════════════════════════════════
if pagina == "🚀 Executar":
    st.markdown("## 🚀 Painel de Controle")
    st.markdown("Clique no modo desejado. O log de execução aparece em tempo real abaixo.")
    st.markdown("<hr>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        btn_daily = st.button("☀️ Atualizar\nDiário\n(só Sheets)", key="daily")
    with col2:
        btn_weekly = st.button("📧 Relatório\nSemanal\n(PDF + E-mail)", key="weekly")
    with col3:
        btn_manual = st.button("🧪 Manual\n(Teste)\n(sem e-mail)", key="manual")
    with col4:
        btn_2025 = st.button("📜 Balanço\n2025\n(uma vez)", key="sum2025")

    st.markdown("<br>", unsafe_allow_html=True)

    # Explicação de cada modo
    with st.expander("ℹ️ O que cada botão faz?", expanded=False):
        st.markdown("""
| Botão | O que faz | Quando usar |
|-------|-----------|-------------|
| **☀️ Diário** | Atualiza o PAINEL EXECUTIVO no Google Sheets com KPIs do dia | Agendado todo dia 08h |
| **📧 Semanal** | Gera PDF da semana + envia e-mail ao diretor | Agendado toda segunda 08h |
| **🧪 Manual** | Faz tudo (Sheets + PDF) mas **não envia e-mail** | Para testes |
| **📜 Balanço 2025** | Relatório anual completo de 2025 em PDF | Executar uma única vez |
        """)

    log_placeholder = st.empty()
    log_placeholder.markdown('<div class="log-box">Aguardando execução...</div>', unsafe_allow_html=True)

    if btn_daily:
        with st.spinner("Executando modo diário..."):
            _run_mode("daily", log_placeholder)

    if btn_weekly:
        with st.spinner("Gerando relatório semanal e enviando e-mail..."):
            _run_mode("weekly", log_placeholder)

    if btn_manual:
        with st.spinner("Executando modo manual (sem e-mail)..."):
            _run_mode("manual", log_placeholder)

    if btn_2025:
        with st.spinner("Gerando balanço anual de 2025..."):
            _run_mode("summary2025", log_placeholder)


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 2 – KPIs AO VIVO
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📊 KPIs ao Vivo":
    st.markdown("## 📊 KPIs ao Vivo")
    st.markdown("Dados lidos diretamente da planilha Google Sheets em tempo real.")
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()

    @st.cache_data(ttl=300, show_spinner="Lendo planilha...")
    def _load_data():
        sys.path.insert(0, str(PROJECT_ROOT))
        from src.reader import load_clientes, load_estoque
        from src.kpi_engine import weekly_kpis, monthly_kpis, stock_alerts
        df_c = load_clientes(2026)
        df_e = load_estoque(2026)
        wk = weekly_kpis(df_c, week_offset=0)
        mo = monthly_kpis(df_c, year=2026)
        al = stock_alerts(df_e)
        return df_c, df_e, wk, mo, al

    try:
        df_c, df_e, wk, mo, alerts = _load_data()

        # ── KPI Cards ──────────────────────────────────────────────────────────
        def _brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".","," ).replace("X",".")
        def _delta_html(v):
            arrow = "▲" if v >= 0 else "▼"
            cls = "kpi-delta-pos" if v >= 0 else "kpi-delta-neg"
            return f'<span class="{cls}">{arrow} {abs(v):.1f}% vs semana anterior</span>'

        c1, c2, c3, c4 = st.columns(4)
        cards = [
            (c1, "Receita da Semana",  _brl(wk.get("receita", 0)),      _delta_html(wk.get("crescimento_wow_receita", 0))),
            (c2, "Margem de Lucro",    f"{wk.get('margem_pct', 0):.1f}%", ""),
            (c3, "Serviços na Semana", str(wk.get("total_servicos", 0)),  ""),
            (c4, "Ticket Médio",       _brl(wk.get("ticket_medio", 0)),   ""),
        ]
        for col, label, value, delta in cards:
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{value}</div>
                  {delta}
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gráfico + Tabelas ───────────────────────────────────────────────────
        left, right = st.columns([3, 2])

        with left:
            st.markdown("#### Receita por Dia (Semana Atual)")
            rp_dia = wk.get("receita_por_dia", {})
            if rp_dia and any(v > 0 for v in rp_dia.values()):
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(7, 3))
                fig.patch.set_facecolor("#1A1A1A")
                ax.set_facecolor("#0D0D0D")
                bars = ax.bar(list(rp_dia.keys()), list(rp_dia.values()), color="#CC0000", edgecolor="#FFD700", linewidth=0.5)
                ax.bar_label(bars, labels=[_brl(v) for v in rp_dia.values()], padding=3, fontsize=7, color="#FFD700")
                ax.tick_params(colors="#FFD700", labelsize=8)
                ax.spines[["top","right","left","bottom"]].set_color("#333")
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Nenhuma receita registrada na semana atual.")

        with right:
            st.markdown("#### Top Serviços")
            top_s = wk.get("top_servicos", [])
            if top_s:
                for s in top_s:
                    st.markdown(f"**{s['nome']}** — {s['quantidade']} serviço(s)")
            else:
                st.info("Nenhum dado disponível.")

            st.markdown("#### Top Marcas")
            top_m = wk.get("top_marcas", [])
            if top_m:
                for m in top_m:
                    st.markdown(f"**{m['nome']}** — {m['quantidade']} atendimento(s)")

        # ── Parceiros ──────────────────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### Performance por Parceiro (Semana)")
        partners = wk.get("performance_parceiros", [])
        if partners:
            import pandas as pd
            df_p = pd.DataFrame(partners)
            df_p.columns = ["Parceiro", "Serviços", "Receita (R$)", "Custo (R$)", "Lucro (R$)", "Margem (%)"]
            st.dataframe(df_p, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado de parceiros na semana atual.")

        # ── Alertas ────────────────────────────────────────────────────────────
        if alerts:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.error(f"⚠️ **{len(alerts)} alerta(s) de estoque crítico:**")
            for a in alerts:
                st.markdown(f"🔴 **{a['item']}** — {a.get('obs', '')}")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.info("Verifique se o `.env` e o `credentials.json` estão configurados corretamente (página 🔧 Setup).")


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 3 – RELATÓRIOS
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📁 Relatórios":
    st.markdown("## 📁 Relatórios Gerados")
    st.markdown("Todos os PDFs salvos automaticamente pelo sistema.")
    st.markdown("<hr>", unsafe_allow_html=True)

    reports_dir = PROJECT_ROOT / "reports"
    pdfs = sorted(reports_dir.rglob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not pdfs:
        st.info("Nenhum relatório encontrado ainda. Execute o modo **Manual** ou **Semanal** para gerar o primeiro.")
    else:
        st.markdown(f"**{len(pdfs)} relatório(s) encontrado(s)**")
        st.markdown("<br>", unsafe_allow_html=True)

        for pdf in pdfs:
            mtime = datetime.fromtimestamp(pdf.stat().st_mtime)
            size_kb = pdf.stat().st_size / 1024
            rel_path = pdf.relative_to(PROJECT_ROOT)

            col_info, col_dl = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                **📄 {pdf.name}**
                <br><span style='color:#999; font-size:12px;'>📁 {rel_path.parent}  ·  📅 {mtime.strftime('%d/%m/%Y %H:%M')}  ·  💾 {size_kb:.1f} KB</span>
                """, unsafe_allow_html=True)
            with col_dl:
                with open(pdf, "rb") as f:
                    st.download_button(
                        label="⬇ Baixar",
                        data=f.read(),
                        file_name=pdf.name,
                        mime="application/pdf",
                        key=str(pdf),
                    )
            st.markdown("<hr style='margin:6px 0; opacity:0.2;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 4 – GIT & VERSÕES
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📦 Git & Versões":
    st.markdown("## 📦 Git & Versões")
    st.markdown("Gerencie commits e envie melhorias para o GitHub sem abrir o terminal.")
    st.markdown("<hr>", unsafe_allow_html=True)

    def _git(args: list[str]) -> str:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        return (r.stdout + r.stderr).strip()

    # ── Status atual ──────────────────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.markdown("#### 📋 Status atual")
        status = _git(["status", "--short"])
        if status:
            st.markdown(f'<div class="log-box">{status}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ Tudo commitado — sem alterações pendentes.")

    with right:
        st.markdown("#### 🕐 Últimos commits")
        log = _git(["log", "--oneline", "-10"])
        st.markdown(f'<div class="log-box">{log}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Novo commit ───────────────────────────────────────────────────────────
    st.markdown("#### 💾 Criar novo commit e enviar ao GitHub")

    msg = st.text_input(
        "Mensagem do commit",
        placeholder="ex: feat: adicionar novo KPI de ticket médio",
        help="Use verbos no imperativo: feat, fix, docs, chore, refactor",
    )

    with st.expander("🔑 Token GitHub (se o push falhar por autenticação)", expanded=False):
        st.markdown("""
        Se o push retornar erro 403, cole aqui um **Classic Token** com escopo `repo`:
        > github.com → Settings → Developer settings → **Tokens (classic)** → Generate new token
        """)
        token_input = st.text_input("Token (ghp_...)", type="password", key="github_token")

    col_commit, col_push, col_both = st.columns(3)
    commit_log = st.empty()

    with col_commit:
        if st.button("💾 Só Commit (sem push)"):
            if not msg:
                st.warning("Escreva uma mensagem de commit antes de continuar.")
            else:
                lines = []
                lines.append(_git(["add", "."]))
                lines.append(_git(["commit", "-m", msg]))
                commit_log.markdown(
                    f'<div class="log-box">' + "\n".join(l for l in lines if l) + "</div>",
                    unsafe_allow_html=True,
                )

    with col_push:
        if st.button("🚀 Só Push (commits já feitos)"):
            lines = []
            if token_input:
                cred = PROJECT_ROOT / ".git" / "_tmp_cred"
                cred.write_text(f"https://guibsoliveira:{token_input}@github.com\n")
                lines.append(_git(["-c", f"credential.helper=store --file={cred}", "push", "origin", "master"]))
                cred.unlink(missing_ok=True)
            else:
                lines.append(_git(["push", "origin", "master"]))
            commit_log.markdown(
                f'<div class="log-box">' + "\n".join(l for l in lines if l) + "</div>",
                unsafe_allow_html=True,
            )

    with col_both:
        if st.button("🚀 Commit + Push"):
            if not msg:
                st.warning("Escreva uma mensagem de commit antes de continuar.")
            else:
                lines = []
                lines.append(_git(["add", "."]))
                lines.append(_git(["commit", "-m", msg]))
                if token_input:
                    cred = PROJECT_ROOT / ".git" / "_tmp_cred"
                    cred.write_text(f"https://guibsoliveira:{token_input}@github.com\n")
                    lines.append(_git(["-c", f"credential.helper=store --file={cred}", "push", "origin", "master"]))
                    cred.unlink(missing_ok=True)
                else:
                    lines.append(_git(["push", "origin", "master"]))
                commit_log.markdown(
                    f'<div class="log-box">' + "\n".join(l for l in lines if l) + "</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Como funciona a arquitetura ───────────────────────────────────────────
    st.markdown("#### 💡 Arquitetura do Projeto")
    with st.expander("Entender como o código está organizado", expanded=False):
        st.markdown("""
```
app.py              ← VOCÊ ESTÁ AQUI (interface visual)
     │ chama
run.py              ← Orquestrador: coordena o fluxo completo
     │
     ├── src/reader.py         Lê a planilha e converte em tabela de dados
     ├── src/kpi_engine.py     Calcula os KPIs (receita, margem, ticket médio...)
     ├── src/analyst.py        Envia KPIs para o Claude e recebe análise em PT-BR
     ├── src/dashboard_writer.py  Escreve o PAINEL EXECUTIVO no Sheets
     ├── src/report_generator.py  Cria o PDF semanal com gráficos
     └── src/email_sender.py   Envia o e-mail com PDF para o diretor
```

**Princípio de Responsabilidade Única:**
Cada arquivo faz **uma coisa só**. Se você quiser:
- 📊 Adicionar um KPI → edite apenas `kpi_engine.py`
- 🎨 Mudar o layout do PDF → edite apenas `report_generator.py`
- 📧 Mudar o corpo do e-mail → edite apenas `email_sender.py`
- 📖 Mudar como os dados são lidos → edite apenas `reader.py`

**Como adicionar uma melhoria:**
1. Edite o arquivo correto
2. Escreva uma mensagem de commit descritiva aqui
3. Clique em **Commit + Push**
4. A melhoria aparece no GitHub automaticamente ✅
        """)


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 5 – SETUP & STATUS
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "🔧 Setup & Status":
    st.markdown("## 🔧 Setup & Status")
    st.markdown("Checklist completo de configuração. Tudo em verde = pronto para rodar.")
    st.markdown("<hr>", unsafe_allow_html=True)

    def _check(condition: bool, ok_msg: str, err_msg: str, fix: str = ""):
        if condition:
            st.markdown(f'<span class="badge-ok">✅ {ok_msg}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge-err">❌ {err_msg}</span>', unsafe_allow_html=True)
            if fix:
                st.markdown(f"<small style='color:#999;margin-left:24px;'>→ {fix}</small>", unsafe_allow_html=True)

    # ── Arquivos essenciais ────────────────────────────────────────────────────
    st.markdown("#### 📁 Arquivos")
    creds = PROJECT_ROOT / "config" / "credentials.json"
    creds_double = PROJECT_ROOT / "config" / "credentials.json.json"
    env_file = PROJECT_ROOT / ".env"

    _check(creds.exists(), "config/credentials.json encontrado",
           "config/credentials.json NÃO encontrado",
           "Baixe do Google Cloud Console e salve em config/credentials.json" +
           (" (⚠️ você tem credentials.json.json — renomeie!)" if creds_double.exists() else ""))

    if creds_double.exists() and not creds.exists():
        st.markdown('<span class="badge-warn">⚠️ Arquivo existe com extensão dupla: credentials.json.json → renomeie para credentials.json</span>', unsafe_allow_html=True)

    _check(env_file.exists(), ".env encontrado",
           ".env NÃO encontrado",
           "Copie .env.example para .env e preencha os valores")

    # ── Variáveis de ambiente ──────────────────────────────────────────────────
    st.markdown("#### 🔑 Variáveis de Ambiente (.env)")
    if env_file.exists():
        from dotenv import dotenv_values
        env_vals = dotenv_values(str(env_file))
        required = {
            "ANTHROPIC_API_KEY": "Chave da API Claude (console.anthropic.com)",
            "GMAIL_USER": "E-mail Gmail para envio",
            "GMAIL_APP_PASSWORD": "Senha de app do Gmail (16 dígitos)",
            "DIRECTOR_EMAIL": "E-mail do destinatário do relatório",
        }
        for key, desc in required.items():
            val = env_vals.get(key, "")
            filled = bool(val and val not in ("sk-ant-your-key-here", "xxxx-xxxx-xxxx-xxxx",
                                               "seu_email@gmail.com", "diretor@eurocoding.com.br"))
            _check(filled, f"{key} configurado", f"{key} NÃO configurado", f"{desc}")
    else:
        st.info("Crie o arquivo .env primeiro (copie .env.example).")

    # ── Dependências ────────────────────────────────────────────────────────────
    st.markdown("#### 📦 Dependências Python")
    deps = ["gspread", "pandas", "anthropic", "matplotlib", "fpdf", "dotenv", "streamlit", "schedule"]
    for dep in deps:
        try:
            importlib.import_module(dep if dep != "dotenv" else "dotenv")
            _check(True, f"{dep} instalado", "")
        except ImportError:
            _check(False, "", f"{dep} NÃO instalado", f"Execute: py -m pip install -r requirements.txt")

    # ── Próximas ações ─────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 🗺️ Ordem de configuração")
    st.markdown("""
1. **Renomear** `credentials.json.json` → `credentials.json` (se aparecer ⚠️ acima)
2. **Criar `.env`**: copiar `.env.example` e preencher as 4 variáveis
3. **Instalar dependências**: abrir CMD na pasta do projeto e rodar `py -m pip install -r requirements.txt`
4. **Compartilhar a planilha** com o e-mail da service account (permissão Editor)
5. **Testar**: ir na página **🚀 Executar** → clicar **🧪 Manual**
6. **Conferir resultados**: Google Sheets → aba PAINEL EXECUTIVO / pasta `reports/`
7. **Agendar**: Windows Task Scheduler (ver instruções no README.md)
    """)
