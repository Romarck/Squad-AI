import os
import streamlit as st
from supabase import create_client, Client
from database import get_db

@st.cache_resource
def init_supabase() -> Client:
    """Initialize and return the Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

def login_user(email, password):
    supabase = init_supabase()
    if not supabase:
        return None, "Configuração do Supabase ausente nas variáveis de ambiente."
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            db = get_db()
            db_user = db.sync_user(response.user.id, response.user.email)
            
            if db_user['status'] != 'aprovado':
                supabase.auth.sign_out()
                return None, f"Acesso negado. Status do cadastro: {db_user['status'].upper()}"
            
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.session_state.db_user = db_user
            return response.user, None
        return None, "Falha na autenticação."
    except Exception as e:
        return None, f"Erro ao fazer login. Verifique suas credenciais."

def register_user(email, password):
    supabase = init_supabase()
    if not supabase:
        return False, "Configuração do Supabase ausente nas variáveis de ambiente."
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            db = get_db()
            db.sync_user(response.user.id, response.user.email)
            return True, "Cadastro realizado com sucesso! Aguarde a aprovação do Administrador."
        return False, "Falha no cadastro."
    except Exception as e:
        return False, f"Erro ao fazer cadastro: {str(e)}"

def reset_password(email):
    supabase = init_supabase()
    if not supabase:
        return False, "Configuração do Supabase ausente."
    try:
        supabase.auth.reset_password_email(email)
        return True, "Email de recuperação enviado com sucesso (se o e-mail estiver cadastrado)."
    except Exception as e:
        return False, f"Erro ao enviar recuperação: {str(e)}"

def logout_user():
    supabase = init_supabase()
    if supabase:
        try:
            supabase.auth.sign_out()
        except:
            pass
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.db_user = None

def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "db_user" not in st.session_state:
        st.session_state.db_user = None
    return st.session_state.authenticated
