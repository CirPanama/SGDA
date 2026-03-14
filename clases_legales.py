import streamlit as st
import re
from datetime import datetime, timedelta

class Cliente:
    def __init__(self, db):
        self.db = db

    def validar_id(self, doc, es_extranjero=False):
        if not es_extranjero:
            # Formato Cédula Panameña (Ej: 8-888-888)
            patron = r'^([1-9]|1[0-3]|[E|N|PE|PI])-\d{1,4}-\d{1,6}$'
            return bool(re.match(patron, doc))
        return len(doc) >= 5 # Pasaporte extranjero

    def registrar(self, datos):
        return self.db.table("clientes").insert(datos).execute()

class CasoLegal:
    def __init__(self, db):
        self.db = db

    def crear_expediente(self, datos):
        # Campos de Finca, Tomo, Folio incluidos en 'datos'
        return self.db.table("expedientes").insert(datos).execute()

    def programar_alarma(self, exp_id, titulo, fecha_vence, dias_aviso):
        fecha_aviso = fecha_vence - timedelta(days=dias_aviso)
        datos = {
            "expediente_id": exp_id,
            "titulo_alerta": titulo,
            "fecha_vencimiento": fecha_vence.isoformat(),
            "fecha_recordatorio": fecha_aviso.isoformat(),
            "revisado": False
        }
        return self.db.table("recordatorios").insert(datos).execute()

class AgendaSemaforo:
    def __init__(self, db):
        self.db = db

    def obtener_alertas(self):
        res = self.db.table("recordatorios").select("*, expedientes(titulo_proceso)").execute()
        if not res.data: return []
        
        hoy = datetime.now().date()
        resultados = []
        for a in res.data:
            vence = datetime.strptime(a['fecha_vencimiento'], '%Y-%m-%d').date()
            dias = (vence - hoy).days
            
            # Lógica de Semáforo
            if dias < 0: color = "🔴 VENCIDO"
            elif dias <= 3: color = "🟡 PRÓXIMO"
            else: color = "🟢 A TIEMPO"
            
            resultados.append({
                "Vencimiento": vence,
                "Estado": color,
                "Caso": a['expedientes']['titulo_proceso'],
                "Trámite": a['titulo_alerta'],
                "Días Restantes": dias
            })
        return sorted(resultados, key=lambda x: x['Vencimiento'])
    