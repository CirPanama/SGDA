import streamlit as st
from datetime import datetime

class AlarmaLegal:
    def __init__(self, db_manager):
        self.db = db_manager

    def programar(self, expediente_id, mensaje, fecha_hora, tipo_aviso):
        datos = {
            "expediente_id": expediente_id,
            "titulo_alerta": mensaje,
            "fecha_recordatorio": fecha_hora.isoformat(),
            "tipo_aviso": tipo_aviso
        }
        return self.db.insert("recordatorios", datos)

    def verificar_pendientes(self):
        # Lógica para mostrar notificaciones críticas
        res = self.db.conn.table("recordatorios").select("*, expedientes(titulo_proceso)")\
            .eq("revisado", False).execute()
        return res.data
    