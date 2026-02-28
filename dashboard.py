import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from clases_legales import AgendaSemaforo
from registrointerfaz import modulo_registro

def main():
    st.set_page_config(page_title="Legal Manager PA", layout="wide")
    conn = st.connection("supabase", type=SupabaseConnection)

    # --- LOGIN SIMPLE ---
    if 'auth' not in st.session_state:
        st.title("🔐 Acceso al Despacho")
        user = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Entrar"):
            try:
                res = conn.auth.sign_in_with_password({"email": user, "password": pw})
                st.session_state['auth'] = res.user
                st.rerun()
            except: st.error("Error de acceso")
        st.stop()

    # --- DASHBOARD ---
    st.sidebar.title("⚖️ Menú Legal")
    opcion = st.sidebar.radio("Ir a:", ["Panel de Control", "Registros"])
    if st.sidebar.button("Salir"):
        del st.session_state['auth']
        st.rerun()

    if opcion == "Panel de Control":
        st.title("📊 Agenda Judicial (Semáforo)")
        agenda = AgendaSemaforo(conn)
        datos = agenda.obtener_alertas()
        
        if datos:
            df = pd.DataFrame(datos)
            def color_rows(val):
                if "🔴" in str(val): return 'color: red; font-weight: bold'
                if "🟡" in str(val): return 'color: orange; font-weight: bold'
                if "🟢" in str(val): return 'color: green; font-weight: bold'
                return ''
            st.table(df.style.applymap(color_rows, subset=['Estado']))
        else:
            st.info("No hay alarmas pendientes.")
            
    elif opcion == "Registros":
        modulo_registro(conn)

if __name__ == "__main__":
    main()