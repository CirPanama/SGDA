import streamlit as st

class CasoLegal:
    def __init__(self, db_manager):
        self.db = db_manager
        self.tabla = "expedientes"

    def registrar_nuevo_caso(self, datos):
        """
        Recibe un diccionario con la info del formulario.
        Incluye validación básica de campos obligatorios.
        """
        if not datos.get("titulo_proceso") or not datos.get("cliente_id"):
            st.error("❌ El título del proceso y el cliente son obligatorios.")
            return False
            
        return self.db.insert(self.tabla, datos)

    def obtener_lista_casos(self):
        # Hacemos un JOIN con la tabla clientes para mostrar el nombre en lugar del ID
        return self.db.conn.table(self.tabla).select("*, clientes(nombre_completo)").execute()