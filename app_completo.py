#!/usr/bin/env python
"""
Interface Web Completa com CRUD e Histórico
Squad de Agentes Inteligentes
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Adiciona o diretório src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
load_dotenv(override=True)

# Importar database
from database import get_db

# Importar auth
from auth import login_user, register_user, reset_password, logout_user, check_auth

# Utils
from utils.backup_manager import BackupManager

# Configuração da página
st.set_page_config(
    page_title="Squad de Agentes IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado - Identidade Visual Nuclea
st.markdown("""
<style>
    html, body, .stApp, p, span, div, h1, h2, h3, h4, h5, h6 {
        font-family: 'ABCFavorit', 'ABCFavoritVariant', 'Inter', sans-serif;
    }
    code, pre, code span, pre span {
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: #000000;
        color: #FFFFFF;
        border-radius: 8px;
        border-bottom: 4px solid #66FFCC;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #66FFCC;
    }
    .demanda-card {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #66FFCC;
        background-color: #F5F5F5;
        color: #000000;
        margin: 0.5rem 0;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        background: #000000;
        color: #FFFFFF;
        border: 1px solid #66FFCC;
        text-align: center;
    }
    
    /* CTAs */
    .stButton > button[data-baseweb="button"]:has(span) {
        border-radius: 8px !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #66FFCC !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4DE6B3 !important;
    }
</style>
""", unsafe_allow_html=True)

# Estado da aplicação
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'execucao_completa' not in st.session_state:
    st.session_state.execucao_completa = False
if 'demanda_id_atual' not in st.session_state:
    st.session_state.demanda_id_atual = None
if 'modo_edicao' not in st.session_state:
    st.session_state.modo_edicao = False
if 'demanda_editando' not in st.session_state:
    st.session_state.demanda_editando = None
if 'limpar_formulario' not in st.session_state:
    st.session_state.limpar_formulario = False

# Authentication Check
if not check_auth():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Squad de Agentes Inteligentes</h1>
        <p>Acesso Restrito</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
        
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.auth_mode == "login":
            st.markdown("### Login")
            email = st.text_input("Email", placeholder="seu@email.com", key="login_email")
            password = st.text_input("Senha", type="password", key="login_pass")
            
            if st.button("Entrar", type="primary", use_container_width=True):
                if email and password:
                    user, error = login_user(email, password)
                    if user:
                        st.success("Login efetuado com sucesso!")
                        st.rerun()
                    else:
                        st.error(error)
                else:
                    st.warning("Preencha email e senha.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Criar Conta", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()
            with col_b:
                if st.button("Esqueci a Senha", use_container_width=True):
                    st.session_state.auth_mode = "forgot"
                    st.rerun()

        elif st.session_state.auth_mode == "register":
            st.markdown("### Criar Conta")
            email = st.text_input("Email", placeholder="seu@email.com", key="reg_email")
            password = st.text_input("Senha", type="password", key="reg_pass")
            password_confirm = st.text_input("Confirmar Senha", type="password", key="reg_pass2")
            
            if st.button("Registrar", type="primary", use_container_width=True):
                if email and password and password == password_confirm:
                    success, msg = register_user(email, password)
                    if success:
                        st.success(msg)
                        st.session_state.auth_mode = "login"
                    else:
                        st.error(msg)
                elif password != password_confirm:
                    st.warning("As senhas não coincidem.")
                else:
                    st.warning("Preencha todos os campos.")
                    
            if st.button("Voltar ao Login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

        elif st.session_state.auth_mode == "forgot":
            st.markdown("### Recuperar Senha")
            email = st.text_input("Email", placeholder="seu@email.com", key="forgot_email")
            
            if st.button("Enviar E-mail de Recuperação", type="primary", use_container_width=True):
                if email:
                    success, msg = reset_password(email)
                    if success:
                        st.success(msg)
                        st.session_state.auth_mode = "login"
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha o e-mail.")
                    
            if st.button("Voltar ao Login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
                
    st.stop() # Interrompe a execução para não logados

# Inicializar banco de dados
db = get_db()

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>🤖 Squad de Agentes Inteligentes</h1>
    <p>Sistema Multi-Agente com Histórico e Gerenciamento de Demandas</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"👤 **Logado como:** {st.session_state.user.email if st.session_state.user else 'Usuário'}")
    if st.button("🚪 Sair", use_container_width=True):
        logout_user()
        st.rerun()
        
    st.markdown("---")
    
    st.header("ℹ️ Sobre o Sistema")
    st.markdown("""
    **4 Agentes IA colaborando:**

    1. 👔 **Product Owner**
    2. 📋 **Analista de Sistemas**
    3. 💻 **Fox Full-Stack Developer**
    4. ✅ **Quality Assurance**

    ---
    """)

    # Estatísticas
    user_id_filtro = None if st.session_state.db_user.get('role') == 'admin' else st.session_state.db_user['id']
    stats = db.obter_estatisticas(user_id=user_id_filtro)

    st.markdown("### 📊 Estatísticas")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", stats['total_demandas'])
    with col2:
        st.metric("Executadas", stats['total_executadas'])

    if stats.get('por_status'):
        st.markdown("**Por Status:**")
        for status, count in stats['por_status'].items():
            emoji = {"pendente": "⏳", "executando": "⚙️", "concluida": "✅", "erro": "❌"}.get(status, "📋")
            st.text(f"{emoji} {status.capitalize()}: {count}")

    st.markdown("---")

    # Verificar conectividade
    import os
    gemini_ok = bool(os.getenv('GEMINI_API_KEY'))
    jira_ok = bool(os.getenv('JIRA_URL') and os.getenv('JIRA_API_KEY'))

    st.markdown(f"""
    ### 🔧 Configuração
    - Gemini API: {"✅" if gemini_ok else "❌"}
    - Jira API: {"✅" if jira_ok else "⚠️ Opcional"}
    """)

# Tabs principais
tabs_names = [
    "📝 Nova Demanda",
    "📚 Histórico",
    "📊 Execução",
    "📄 Resultados"
]
if st.session_state.db_user and st.session_state.db_user.get('role') == 'admin':
    tabs_names.append("👑 Admin")

tabs = st.tabs(tabs_names)
tab1, tab2, tab3, tab4 = tabs[:4]
tab_admin = tabs[4] if len(tabs) > 4 else None

# ============================================================================
# TAB 1: NOVA DEMANDA
# ============================================================================
with tab1:
    st.header("📝 Criar Nova Demanda")

    # Se solicitou limpar formulário, resetar tudo
    if st.session_state.limpar_formulario:
        st.session_state.modo_edicao = False
        st.session_state.demanda_editando = None
        st.session_state.limpar_formulario = False

    # Se estiver editando uma demanda existente
    if st.session_state.modo_edicao and st.session_state.demanda_editando:
        st.info(f"✏️ Editando demanda #{st.session_state.demanda_editando['id']}")

        demanda_atual = st.session_state.demanda_editando
        titulo_default = demanda_atual['titulo']
        descricao_default = demanda_atual['descricao']
        jira_default = bool(demanda_atual['usar_jira'])
        project_default = demanda_atual['project_key'] or "LOCAL"
        tags_default = ", ".join(demanda_atual.get('tags', []))
    else:
        # Valores padrão para novo formulário
        titulo_default = ""
        descricao_default = ""
        jira_default = False
        project_default = "LOCAL"
        tags_default = ""

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Detalhes da Demanda")

        demanda_titulo = st.text_input(
            "Título da Demanda",
            value=titulo_default,
            key="input_titulo",
            placeholder="Ex: Implementar validação de CPF"
        )

        demanda_descricao = st.text_area(
            "Descrição Detalhada",
            value=descricao_default,
            height=300,
            key="input_descricao"
        )

        # Tags
        tags_input = st.text_input(
            "Tags (separadas por vírgula)",
            value=tags_default,
            placeholder="python, validação, backend",
            help="Tags para organizar suas demandas"
        )

    with col2:
        st.subheader("Configurações")

        usar_jira = st.checkbox(
            "Usar integração Jira",
            value=jira_default,
            key="input_jira"
        )

        if usar_jira:
            project_key = st.text_input(
                "Chave do Projeto Jira",
                value=project_default if project_default != "LOCAL" else "AUTO",
                key="input_project"
            )
        else:
            project_key = "LOCAL"
            st.info("💡 **Modo Local**: Sem Jira")

    st.markdown("---")

    # Botões de ação
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 1])

    with col_btn1:
        if st.session_state.modo_edicao:
            if st.button("💾 Atualizar Demanda", use_container_width=True, type="primary"):
                # Validação
                if not demanda_titulo or not demanda_descricao:
                    st.error("❌ Preencha título e descrição!")
                else:
                    # Processar tags
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

                # Atualizar no banco
                success = db.atualizar_demanda(
                    demanda_id=st.session_state.demanda_editando['id'],
                    titulo=demanda_titulo,
                    descricao=demanda_descricao,
                    usar_jira=usar_jira,
                    project_key=project_key,
                    tags=tags,
                    user_id=st.session_state.db_user['id']
                )

                if success:
                    st.success("✅ Demanda atualizada!")
                    st.session_state.modo_edicao = False
                    st.session_state.demanda_editando = None
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar demanda")
        else:
            if st.button("💾 Salvar Demanda", use_container_width=True):
                if not demanda_titulo or not demanda_descricao:
                    st.error("❌ Preencha título e descrição!")
                else:
                    # Processar tags
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

                    # Salvar no banco
                    demanda_id = db.criar_demanda(
                        titulo=demanda_titulo,
                        descricao=demanda_descricao,
                        user_id=st.session_state.db_user['id'],
                        usar_jira=usar_jira,
                        project_key=project_key,
                        tags=tags
                    )

                    st.success(f"✅ Demanda #{demanda_id} salva com sucesso!")
                    st.session_state.demanda_id_atual = demanda_id

    with col_btn2:
        executar_btn = st.button(
            "🚀 Executar Squad",
            type="primary",
            use_container_width=True,
            key="btn_executar"
        )

    with col_btn3:
        if st.session_state.modo_edicao:
            if st.button("❌ Cancelar Edição", use_container_width=True):
                st.session_state.modo_edicao = False
                st.session_state.demanda_editando = None
                st.rerun()

    with col_btn4:
        if st.button("🗑️ Limpar Formulário", use_container_width=True):
            # Marcar flag para limpar no próximo render
            st.session_state.limpar_formulario = True
            st.session_state.modo_edicao = False
            st.session_state.demanda_editando = None
            st.rerun()

# ============================================================================
# TAB 2: HISTÓRICO
# ============================================================================
with tab2:
    st.header("📚 Histórico de Demandas")

    # Filtros
    col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])

    with col_filter1:
        termo_pesquisa = st.text_input(
            "🔍 Pesquisar",
            placeholder="Digite para pesquisar..."
        )

    with col_filter2:
        filtro_status = st.selectbox(
            "Status",
            ["Todos", "Pendente", "Executando", "Concluída", "Erro"]
        )

    with col_filter3:
        limite = st.selectbox(
            "Mostrar",
            [10, 25, 50, 100],
            index=1
        )

    st.markdown("---")

    # Buscar demandas
    user_id_filtro = None if st.session_state.db_user.get('role') == 'admin' else st.session_state.db_user['id']
    
    if termo_pesquisa:
        demandas = db.pesquisar_demandas(termo_pesquisa, user_id=user_id_filtro, limit=limite)
    elif filtro_status != "Todos":
        demandas = db.listar_demandas(status=filtro_status.lower(), user_id=user_id_filtro, limit=limite)
    else:
        demandas = db.listar_demandas(user_id=user_id_filtro, limit=limite)

    if not demandas:
        st.info("📭 Nenhuma demanda encontrada")
    else:
        st.markdown(f"**{len(demandas)} demanda(s) encontrada(s)**")

        for demanda in demandas:
            with st.expander(
                f"#{demanda['id']} - {demanda['titulo']} "
                f"({'✅' if demanda['status'] == 'concluida' else '⏳'})"
            ):
                col_info, col_actions = st.columns([3, 1])

                with col_info:
                    st.markdown(f"**ID:** {demanda['id']}")
                    st.markdown(f"**Status:** {demanda['status'].capitalize()}")
                    st.markdown(f"**Criada em:** {demanda['created_at']}")

                    if demanda['executed_at']:
                        st.markdown(f"**Executada em:** {demanda['executed_at']}")

                    if demanda['tags']:
                        tags_str = ", ".join(f"`{tag}`" for tag in demanda['tags'])
                        st.markdown(f"**Tags:** {tags_str}")

                    st.markdown("**Descrição:**")
                    st.text(demanda['descricao'][:200] + "..." if len(demanda['descricao']) > 200 else demanda['descricao'])

                with col_actions:
                    # Botão Editar
                    if st.button("✏️ Editar", key=f"edit_{demanda['id']}", use_container_width=True):
                        st.session_state.modo_edicao = True
                        st.session_state.demanda_editando = demanda
                        st.rerun()

                    # Botão Ver Resultados
                    if demanda['status'] == 'concluida':
                        if st.button("📄 Ver Resultados", key=f"view_{demanda['id']}", use_container_width=True):
                            resultados = db.obter_resultados(demanda['id'])
                            st.session_state.resultados = resultados
                            st.session_state.execucao_completa = True
                            st.session_state.demanda_id_atual = demanda['id']
                            # Mudar para aba de resultados (índice 3)
                            st.info("📄 Veja os resultados na aba 'Resultados'")

                    # Botão Executar
                    if demanda['status'] != 'executando':
                        if st.button("🚀 Executar", key=f"exec_{demanda['id']}", use_container_width=True):
                            st.session_state.demanda_id_atual = demanda['id']
                            st.session_state.modo_edicao = False
                            st.session_state.demanda_editando = None
                            # Preparar execução
                            st.info("🚀 Vá para a aba 'Execução' para acompanhar")

                    # Botão Deletar
                    if st.button("🗑️ Deletar", key=f"del_{demanda['id']}", use_container_width=True):
                        uid_trava = None if st.session_state.db_user.get('role') == 'admin' else st.session_state.db_user['id']
                        if db.deletar_demanda(demanda['id'], user_id=uid_trava):
                            st.success(f"✅ Demanda #{demanda['id']} deletada!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao deletar")

# ============================================================================
# TAB 3: EXECUÇÃO
# ============================================================================
with tab3:
    st.header("📊 Execução em Andamento")

    # Verificar se há demanda para executar
    if executar_btn or (st.session_state.demanda_id_atual and not st.session_state.execucao_completa):

        # Se clicou no botão executar, salvar/atualizar demanda se necessário
        if executar_btn:
            if not demanda_titulo or not demanda_descricao:
                st.error("❌ Por favor, preencha o título e descrição da demanda!")
                st.stop()

            # Processar tags
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

            # Se está em modo de edição, atualizar a demanda existente
            if st.session_state.modo_edicao and st.session_state.demanda_editando:
                demanda_id = st.session_state.demanda_editando['id']

                # Atualizar demanda no banco
                db.atualizar_demanda(
                    demanda_id=demanda_id,
                    titulo=demanda_titulo,
                    descricao=demanda_descricao,
                    usar_jira=usar_jira,
                    project_key=project_key,
                    tags=tags,
                    user_id=st.session_state.db_user['id']
                )

                st.session_state.demanda_id_atual = demanda_id
                st.session_state.modo_edicao = False
                st.session_state.demanda_editando = None

                st.success(f"✅ Demanda #{demanda_id} atualizada e será executada!")

            # Se não há demanda_id_atual, criar uma nova
            elif not st.session_state.demanda_id_atual:
                demanda_id = db.criar_demanda(
                    titulo=demanda_titulo,
                    descricao=demanda_descricao,
                    user_id=st.session_state.db_user['id'],
                    usar_jira=usar_jira,
                    project_key=project_key,
                    tags=tags
                )
                st.session_state.demanda_id_atual = demanda_id
                st.success(f"✅ Demanda #{demanda_id} criada e será executada!")
            else:
                demanda_id = st.session_state.demanda_id_atual

            # Obter dados atualizados da demanda
            demanda = db.obter_demanda(st.session_state.demanda_id_atual)
            if not demanda:
                st.error("❌ Demanda não encontrada!")
                st.stop()

            demanda_titulo = demanda['titulo']
            demanda_descricao = demanda['descricao']
            usar_jira = bool(demanda['usar_jira'])
            project_key = demanda['project_key']

        st.info(f"🔄 Executando demanda #{st.session_state.demanda_id_atual}")

        # Atualizar status para executando
        db.atualizar_status(st.session_state.demanda_id_atual, 'executando')

        # Container para progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Container para logs em tempo real
        status_container = st.status("🤖 Squad trabalhando...", expanded=True)
        
        # Containers para cada agente
        st.subheader("🔄 Pipeline de Execução")
        po_container = st.empty()
        analista_container = st.empty()
        dev_container = st.empty()
        qa_container = st.empty()

        resultados = {}

        try:
            from squad_de_agentes_inteligentes___mvp_desenvolvimento_agil.crew_runner import executar_crew_com_tracking

            def atualizar_progresso(step, agent_name, message):
                progress_bar.progress(step / 4)
                status_text.text(f"🔄 {agent_name}: {message}")
                status_container.write(f"**{agent_name}**: {message}")

                # Atualizar cards
                if step >= 1:
                    po_container.success("✅ Product Owner - Concluído")
                elif step == 1:
                    po_container.info("⚙️ Product Owner - Trabalhando...")
                else:
                    po_container.warning("⏳ Product Owner - Pendente")

                if step >= 2:
                    analista_container.success("✅ Analista de Sistemas - Concluído")
                elif step == 2:
                    analista_container.info("⚙️ Analista de Sistemas - Trabalhando...")
                else:
                    analista_container.warning("⏳ Analista de Sistemas - Pendente")

                if step >= 3:
                    dev_container.success("✅ Fox Full-Stack Developer - Concluído")
                elif step == 3:
                    dev_container.info("⚙️ Fox Full-Stack Developer - Trabalhando...")
                else:
                    dev_container.warning("⏳ Fox Full-Stack Developer - Pendente")

                if step >= 4:
                    qa_container.success("✅ Quality Assurance - Concluído")
                elif step == 4:
                    qa_container.info("⚙️ Quality Assurance - Trabalhando...")
                else:
                    qa_container.warning("⏳ Quality Assurance - Pendente")

            # Inicializar cards
            atualizar_progresso(0, "Sistema", "Iniciando...")

            # Executar crew
            with status_container:
                resultados = executar_crew_com_tracking(
                    demanda_titulo=demanda_titulo,
                    demanda_descricao=demanda_descricao,
                    usar_jira=usar_jira,
                    project_key=project_key,
                    progress_callback=atualizar_progresso
                )
            
            # Finalizar status
            status_container.update(label="✅ Execução concluída!", state="complete", expanded=False)

            # Salvar resultados no banco
            status_text.text(f"💾 Salvando resultados de {len(resultados)} agente(s)...")
            for agente, resultado in resultados.items():
                db.salvar_resultado(st.session_state.demanda_id_atual, agente, resultado)
                status_text.text(f"✅ {agente} salvo!")

            # Atualizar status
            db.atualizar_status(st.session_state.demanda_id_atual, 'concluida', marcar_executada=True)
            status_text.text("✅ Status atualizado para 'concluída'")

            # Realizar backup automático (Story 2.1)
            try:
                bm = BackupManager()
                bm.criar_backup()
                bm.limpar_backups_antigos(manter_ultimos=10)
                status_text.text("💾 Backup automático realizado!")
            except Exception as e:
                st.warning(f"⚠️ Erro ao criar backup: {e}")

            # Finalização
            progress_bar.progress(1.0)
            status_text.text("✅ Execução concluída com sucesso!")

            st.session_state.resultados = resultados
            st.session_state.execucao_completa = True

            st.success("🎉 **Execução concluída!** Veja os resultados na aba 'Resultados'.")

        except Exception as e:
            st.error(f"❌ **Erro durante execução:** {str(e)}")
            db.atualizar_status(st.session_state.demanda_id_atual, 'erro')
            st.exception(e)

    else:
        st.info("👈 Selecione uma demanda no histórico ou crie uma nova para executar")

# ============================================================================
# TAB 4: RESULTADOS
# ============================================================================
with tab4:
    st.header("📄 Resultados da Execução")

    if not st.session_state.execucao_completa or not st.session_state.resultados:
        st.info("⏳ Aguardando conclusão da execução...")
    else:
        st.success(f"🎉 Resultados da demanda #{st.session_state.demanda_id_atual}")

        # Sub-tabs para resultados
        result_tab1, result_tab2, result_tab3, result_tab4, result_tab5 = st.tabs([
            "📋 Product Owner",
            "📋 Analista",
            "💻 Desenvolvedor",
            "✅ QA",
            "💾 Exportar"
        ])

        with result_tab1:
            st.markdown("### 👔 Product Owner - User Story")
            st.markdown(st.session_state.resultados.get("Product Owner", "Sem resultado"))

        with result_tab2:
            st.markdown("### 📋 Analista de Sistemas - Especificação Técnica")
            st.markdown(st.session_state.resultados.get("Analista de Sistemas", "Sem resultado"))

        with result_tab3:
            st.markdown("### 💻 Fox Full-Stack Developer - Código e Testes")
            
            tab_preview, tab_code = st.tabs(["👁️ Preview", "📝 Code"])
            with tab_preview:
                dev_result = st.session_state.resultados.get("Fox Full-Stack Developer", st.session_state.resultados.get("Desenvolvedor Python", "Sem resultado"))
                import re
                import streamlit.components.v1 as components
                html_match = re.search(r'```html\n(.*?)\n```', dev_result, re.DOTALL)
                if html_match:
                    components.html(html_match.group(1), height=600, scrolling=True)
                else:
                    # Faz o fallback renderizando markdown normal, mas dividindo st.code para os blocos de código
                    parts = re.split(r'(```[\s\S]*?```)', dev_result)
                    for part in parts:
                        if part.startswith('```') and part.endswith('```'):
                            match = re.match(r'```(\w*)\n([\s\S]*?)\n*```', part)
                            if match:
                                lang = match.group(1)
                                code_str = match.group(2)
                                st.code(code_str, language=lang if lang else "python")
                            else:
                                st.markdown(part)
                        elif part.strip():
                            st.markdown(part)
            with tab_code:
                st.code(dev_result, language="markdown")

        with result_tab4:
            st.markdown("### ✅ Quality Assurance - Relatório de Qualidade")
            st.markdown(st.session_state.resultados.get("Quality Assurance", "Sem resultado"))

        with result_tab5:
            st.markdown("### 💾 Exportar Resultados")

            # Obter dados da demanda
            demanda = db.obter_demanda(st.session_state.demanda_id_atual) if st.session_state.demanda_id_atual else None

            col_dl1, col_dl2 = st.columns(2)

            with col_dl1:
                # JSON
                export_data = {
                    "demanda_id": st.session_state.demanda_id_atual,
                    "demanda": demanda,
                    "resultados": st.session_state.resultados,
                    "exportado_em": datetime.now().isoformat()
                }
                results_json = json.dumps(export_data, indent=2, ensure_ascii=False)

                st.download_button(
                    label="📥 Download JSON",
                    data=results_json,
                    file_name=f"demanda_{st.session_state.demanda_id_atual}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col_dl2:
                # Markdown
                results_md = f"""# Resultado do Squad de Agentes\n\n"""
                results_md += f"""**ID da Demanda:** {st.session_state.demanda_id_atual}\n\n"""
                results_md += f"""**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"""

                if demanda:
                    results_md += f"""**Título:** {demanda['titulo']}\n\n"""
                    results_md += f"""**Descrição:**\n{demanda['descricao']}\n\n"""
                    results_md += f"""---\n\n"""

                for agent_name, result in st.session_state.resultados.items():
                    results_md += f"\n## {agent_name}\n\n{result}\n\n---\n\n"""

                st.download_button(
                    label="📥 Download Markdown",
                    data=results_md,
                    file_name=f"demanda_{st.session_state.demanda_id_atual}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            # Botão para nova execução
            st.markdown("---")
            if st.button("🔄 Nova Execução", type="primary", use_container_width=True):
                st.session_state.resultados = None
                st.session_state.execucao_completa = False
                st.session_state.demanda_id_atual = None
                st.rerun()

# ============================================================================
# TAB 5: ADMIN (Se aplicável)
# ============================================================================
if tab_admin:
    with tab_admin:
        st.header("👑 Área Administrativa")
        st.markdown("Gerecie os usuários cadastrados e o controle de acesso ao The Squad-AI.")
        
        usuarios = db.listar_usuarios()
        
        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
        else:
            for usr in usuarios:
                with st.expander(f"{usr['email']} ({usr['role'].upper()}) - {usr['status'].upper()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {usr['id']}")
                        st.write(f"**Email:** {usr['email']}")
                        st.write(f"**Role:** {usr['role']}")
                        st.write(f"**Status Crtl:** {usr['status']}")
                        st.write(f"**Cadastrado em:** {usr['created_at']}")
                    with col2:
                        # Actions
                        if usr['status'] == 'pendente':
                            if st.button("✅ Aprovar Acesso", key=f"apv_{usr['id']}", type="primary"):
                                db.atualizar_status_usuario(usr['id'], "aprovado")
                                st.rerun()
                            if st.button("🚫 Bloquear Acesso", key=f"blq1_{usr['id']}"):
                                db.atualizar_status_usuario(usr['id'], "bloqueado")
                                st.rerun()
                        elif usr['status'] == 'aprovado':
                            if usr['email'].lower() != 'romarck@gmail.com': # protecao do master
                                if st.button("🚫 Bloquear Acesso", key=f"blq2_{usr['id']}"):
                                    db.atualizar_status_usuario(usr['id'], "bloqueado")
                                    st.rerun()
                                if usr['role'] == 'user':
                                    if st.button("Promover para Admin", key=f"prm_{usr['id']}"):
                                        db.atualizar_status_usuario(usr['id'], "aprovado", "admin")
                                        st.rerun()
                                else:
                                    if st.button("Rebaixar para User", key=f"reb_{usr['id']}"):
                                        db.atualizar_status_usuario(usr['id'], "aprovado", "user")
                                        st.rerun()
                            else:
                                st.warning("Administrador mestre não pode ser bloqueado ou rebaixado.")
                        elif usr['status'] == 'bloqueado':
                            if st.button("✅ Desbloquear e Aprovar", key=f"dbp_{usr['id']}", type="primary"):
                                db.atualizar_status_usuario(usr['id'], "aprovado")
                                st.rerun()

