import streamlit as st
from clases_legales import Cliente, CasoLegal

def modulo_registro(db):
    st.header("📝 Registro de Clientes y Expedientes")
    
    cl = Cliente(db)
    ca = CasoLegal(db)

    tab1, tab2 = st.tabs(["👤 Nuevo Cliente", "📂 Nuevo Expediente"])

    with tab1:
        with st.form("f_cliente"):
            nombre = st.text_input("Nombre Completo")
            es_ext = st.checkbox("¿Es Extranjero? (Pasaporte)")
            doc = st.text_input("Identificación (Cédula o Pasaporte)")
            c_nom = st.text_input("Contacto Adicional (Nombre)")
            c_tel = st.text_input("Contacto Adicional (Teléfono)")
            
            if st.form_submit_button("Guardar Cliente"):
                if cl.validar_id(doc, es_ext):
                    cl.registrar({"nombre_completo": nombre, "cedula_ruc": doc, 
                                 "contacto_emergencia_nombre": c_nom, "contacto_emergencia_tel": c_tel})
                    st.success("Cliente guardado.")
                else:
                    st.error("Identificación no válida para Panamá.")

    with tab2:
        res_c = db.table("clientes").select("id, nombre_completo").execute()
        dict_c = {c['nombre_completo']: c['id'] for c in res_c.data}
        
        with st.form("f_caso"):
            c_sel = st.selectbox("Seleccione Cliente", dict_c.keys())
            tit = st.text_input("Título del Caso")
            f, t, fo = st.columns(3)
            finca = f.text_input("Finca")
            tomo = t.text_input("Tomo")
            folio = fo.text_input("Folio")
            
            st.subheader("🔔 Alarma de Seguimiento")
            f_vence = st.date_input("Fecha de Vencimiento Judicial")
            aviso = st.selectbox("Avisar con anticipación de:", [0, 1, 3, 7, 15], format_func=lambda x: f"{x} días antes")

            if st.form_submit_button("Crear Caso y Alarma"):
                exp = ca.crear_expediente({"cliente_id": dict_c[c_sel], "titulo_proceso": tit, 
                                           "finca": finca, "tomo": tomo, "folio": folio})
                if exp.data:
                    ca.programar_alarma(exp.data[0]['id'], f"Término: {tit}", f_vence, aviso)
                    st.success("Expediente y Alarma creados con éxito.")