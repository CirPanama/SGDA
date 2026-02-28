import streamlit as st
from st_supabase_connection import SupabaseConnection

class LegalDB:
    def __init__(self):
        self.conn = st.connection("supabase", type=SupabaseConnection)

    def insertar(self, tabla, datos):
        try:
            return self.conn.table(tabla).insert(datos).execute()
        except Exception as e:
            st.error(f"Error en DB ({tabla}): {e}")
            return None

    def listar(self, tabla, columnas="*"):
        return self.conn.table(tabla).select(columnas).execute()