import streamlit as st
from st_supabase_connection import SupabaseConnection

class LegalDB:
    def __init__(self):
        # Conexión profesional usando Secrets de Streamlit
        self.conn = st.connection("supabase", type=SupabaseConnection)

    def table(self, tabla):
        return self.conn.table(tabla)

    def fetch(self, tabla):
        """Obtiene datos para Contabilidad y Configuración"""
        try:
            res = self.conn.table(tabla).select("*").execute()
            return res.data if res.data else []
        except Exception as e:
            st.error(f"Error en DB ({tabla}): {e}")
            return []

    def insert(self, tabla, datos):
        """Inserción con manejo de campos nulos para evitar errores"""
        return self.conn.table(tabla).insert(datos).execute()

    def update(self, tabla, datos, id_registro):
        """Actualización para el módulo de Configuración"""
        return self.conn.table(tabla).update(datos).eq("id", id_registro).execute()