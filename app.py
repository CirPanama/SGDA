import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date

# --- CONEXIÓN DIRECTA ---
SUPABASE_URL = "https://kkusdbapdlrplfvlkgrr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtrdXNkYmFwZGxycGxmdmxrZ3JyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2MTU4MzUsImV4cCI6MjA4NzE5MTgzNX0.aezaYsRS_g_dFBFdN1TE3ljICq0O3asrqMpMgmEXni0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 1. MÓDULO DE AUTENTICACIÓN ---
def mostrar_login():
    st.title("⚖️ SGDA - Sistema de Gestión de Despacho")
    st.subheader("Acceso al Sistema")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            try:
                res = supabase.table("usuarios").select("*").eq("usuario", u).eq("password_hash", p).execute()
                if res.data:
                    st.session_state['auth'] = res.data[0]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- 2. PANEL DE CONTROL (ALARMAS Y HOY) ---
def mostrar_panel(user):
    st.title(f"📊 Panel de Control - {datetime.now().strftime('%d/%m/%Y')}")
    col1, col2 = st.columns(2)
    hoy = date.today()

    with col1:
        st.subheader("🔔 Alarmas Próximas")
        try:
            res_exp = supabase.table("expedientes").select("*, clientes(nombre_completo)").not_.is_("fecha_alarma", "null").execute()
            if res_exp.data:
                df_a = pd.DataFrame(res_exp.data)
                df_a['fecha_alarma'] = pd.to_datetime(df_a['fecha_alarma']).dt.date
                alertas = df_a[df_a['fecha_alarma'] >= hoy].sort_values("fecha_alarma")
                if not alertas.empty:
                    for _, r in alertas.head(5).iterrows():
                        st.warning(f"**{r['fecha_alarma']}** - {r['titulo_proceso']} (Cliente: {r['clientes']['nombre_completo']})")
                else: st.success("No hay alarmas pendientes.")
            else: st.info("Sin alarmas programadas.")
        except: st.error("Error al cargar alarmas.")

    with col2:
        st.subheader("📅 Citas para Hoy")
        try:
            res_cita = supabase.table("agenda").select("*").eq("fecha_cita", str(hoy)).execute()
            if res_cita.data:
                for c in res_cita.data:
                    st.info(f"⏰ {c['hora_cita'][:5]} - {c['titulo_cita']}")
            else: st.write("No tienes citas para hoy.")
        except: st.error("Error al cargar agenda.")

# --- 3. GESTIÓN DE AGENDA ---
def gestionar_agenda():
    st.title("🗓️ Agenda Judicial")
    t1, t2 = st.tabs(["📆 Calendario", "➕ Nueva Cita"])
    with t2:
        with st.form("form_agenda"):
            tit = st.text_input("Asunto")
            c1, c2 = st.columns(2)
            f = c1.date_input("Fecha", value=date.today())
            h = c2.time_input("Hora")
            desc = st.text_area("Detalles")
            if st.form_submit_button("Guardar en Agenda"):
                supabase.table("agenda").insert({
                    "abogado_id": st.session_state['auth']['id'],
                    "titulo_cita": tit, "fecha_cita": str(f), "hora_cita": str(h), "descripcion": desc
                }).execute()
                st.success("Evento agendado")
                st.rerun()
    with t1:
        f_ver = st.date_input("Consultar fecha", value=date.today())
        res = supabase.table("agenda").select("*").eq("fecha_cita", str(f_ver)).order("hora_cita").execute()
        if res.data:
            for r in res.data:
                with st.expander(f"🕒 {r['hora_cita'][:5]} - {r['titulo_cita']}"):
                    st.write(r['descripcion'])
                    if st.button("Eliminar", key=f"del_c_{r['id']}"):
                        supabase.table("agenda").delete().eq("id", r['id']).execute()
                        st.rerun()
        else: st.info("Día sin eventos.")

# --- 4. GESTIÓN DE CLIENTES ---
def gestionar_clientes():
    st.title("👤 Gestión de Clientes")
    t1, t2 = st.tabs(["Lista", "Registrar"])
    with t1:
        res = supabase.table("clientes").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            # Actualización de parámetro: width='stretch' reemplaza use_container_width=True
            st.dataframe(df, width='stretch')
            c_sel = st.selectbox("Ver expedientes de:", options=[c['id'] for c in res.data], 
                                format_func=lambda x: next(c['nombre_completo'] for c in res.data if c['id'] == x))
            e_res = supabase.table("expedientes").select("*").eq("cliente_id", c_sel).execute()
            if e_res.data: st.table(pd.DataFrame(e_res.data)[['titulo_proceso', 'finca']])
    with t2:
        with st.form("n_c"):
            nom = st.text_input("Nombre Completo")
            ident = st.text_input("Cedula / Pasaporte")
            es_ext = st.checkbox("¿Es Extranjero?")
            if st.form_submit_button("Guardar"):
                supabase.table("clientes").insert({"nombre_completo": nom, "cedula_ruc": ident, "es_extranjero": es_ext}).execute()
                st.success("Cliente registrado")
                st.rerun()

# --- 5. INVENTARIO DE EXPEDIENTES ---
def gestionar_inventario():
    st.title("📂 Inventario de Expedientes")
    t1, t2 = st.tabs(["🗂️ Fichas y Comentarios", "➕ Registrar Expediente"])
    
    with t2:
        c_res = supabase.table("clientes").select("id, nombre_completo").execute()
        if c_res.data:
            with st.form("n_e"):
                c_id = st.selectbox("Cliente", options=[c['id'] for c in c_res.data], format_func=lambda x: next(c['nombre_completo'] for c in c_res.data if c['id'] == x))
                tit = st.text_input("Título Proceso")
                col1, col2, col3 = st.columns(3)
                f, tm, fl = col1.text_input("Finca"), col2.text_input("Tomo"), col3.text_input("Folio")
                alm = st.date_input("Alarma / Vencimiento", value=None)
                if st.form_submit_button("Registrar Expediente"):
                    supabase.table("expedientes").insert({
                        "cliente_id": c_id, "titulo_proceso": tit, 
                        "finca": f, "tomo": tm, "folio": fl, 
                        "fecha_alarma": str(alm) if alm else None
                    }).execute()
                    st.success("Expediente guardado")
                    st.rerun()

    with t1:
        res = supabase.table("expedientes").select("*, clientes(nombre_completo)").execute()
        if res.data:
            for r in res.data:
                cliente_nom = r.get('clientes', {}).get('nombre_completo', 'N/A')
                with st.expander(f"📄 {r['titulo_proceso']} - Cliente: {cliente_nom}"):
                    st.write(f"**Ubicación:** F-{r['finca']} | T-{r['tomo']} | F-{r['folio']}")
                    st.write(f"**Alarma:** {r.get('fecha_alarma', 'No definida')}")
                    if st.button("Ver Historial / Actuaciones", key=f"hist_{r['id']}"):
                        st.session_state['exp_sel'] = r['id']
            
            if 'exp_sel' in st.session_state:
                e_id = st.session_state['exp_sel']
                st.divider()
                st.subheader(f"📜 Historial Expediente #{e_id}")
                try:
                    coms = supabase.table("procesos").select("*").eq("expediente_id", e_id).order("fecha", desc=True).execute()
                    for c in coms.data:
                        st.info(f"📅 {c['fecha'][:10]} - {c['comentario']}")
                except:
                    st.error("Error al cargar historial.")

                with st.form("n_com"):
                    txt = st.text_area("Nueva actuación judicial")
                    if st.form_submit_button("Añadir Registro"):
                        if txt:
                            supabase.table("procesos").insert({"expediente_id": e_id, "comentario": txt}).execute()
                            st.rerun()
        else:
            st.info("No hay expedientes registrados.")

# --- MAIN ---
def main():
    st.set_page_config(page_title="SGDA 2026", layout="wide", page_icon="⚖️")
    
    if 'auth' not in st.session_state:
        mostrar_login()
    else:
        user = st.session_state['auth']
        with st.sidebar:
            st.title("⚖️ SGDA Panamá")
            st.write(f"Abogado: **{user['nombre_abogado']}**")
            st.divider()
            menu = st.radio("Navegación", ["📊 Panel", "🗓️ Agenda", "👤 Clientes", "📂 Inventario"])
            st.divider()
            # Actualización de parámetro: width='stretch' reemplaza use_container_width=True
            if st.button("🔒 Cerrar Sesión", type="primary", width='stretch'):
                del st.session_state['auth']
                st.rerun()

        if menu == "📊 Panel": mostrar_panel(user)
        elif menu == "🗓️ Agenda": gestionar_agenda()
        elif menu == "👤 Clientes": gestionar_clientes()
        elif menu == "📂 Inventario": gestionar_inventario()

if __name__ == "__main__":
    main()