class Expediente:
    def __init__(self, db_manager):
        self.db = db_manager
        self.tabla = "expedientes"

    def crear(self, cliente_id, titulo, radicado, finca=None, tomo=None, folio=None):
        datos = {
            "cliente_id": cliente_id,
            "titulo_proceso": titulo,
            "nro_radicado": radicado,
            "finca": finca,
            "tomo": tomo,
            "folio": folio,
            "estado": "Activo"
        }
        return self.db.insert(self.tabla, datos)

    def obtener_todos(self):
        # Join con clientes para ver nombres en lugar de IDs
        return self.db.conn.table(self.tabla).select("*, clientes(nombre_completo)").execute()