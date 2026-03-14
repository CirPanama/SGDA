import streamlit as st  # <--- ESTO CORRIGE EL ERROR DE "st"
import sys
import os

# Asegurar que reconozca clases_legales.py en la misma carpeta
ruta_actual = os.path.dirname(os.path.abspath(__file__))
if ruta_actual not in sys.path:
    sys.path.append(ruta_actual)

try:
    from clases_legales import Cliente, CasoLegal
except ImportError:
    st.error("No se pudo importar la clase Cliente de clases_legales.py")

def modulo_clientes(db):
    st.header("👤 Registro de Clientes (Panamá & Extranjeros)")
    
    # Instanciamos la clase POO
    gestor_cliente = Cliente(db)

    with st.form("registro_pro"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            # Mejoramos el radio para que sea booleano internamente
            tipo_id = st.radio("Tipo de Documento", ["Nacional (Cédula)", "Extranjero (Pasaporte)"])
            doc_id = st.text_input("Número de Documento")
        
        with col2:
            st.info("💡 Datos de Contacto de Apoyo")
            cont_nom = st.text_input("Nombre del contacto")
            cont_tel = st.text_input("Teléfono del contacto")

        if st.form_submit_button("💾 Guardar Cliente"):
            # Lógica para determinar si es extranjero según tu instrucción del 2026-02-28
            es_extranjero = True if "Extranjero" in tipo_id else False
            
            # Validamos antes de enviar a la DB usando el método de la clase
            if not gestor_cliente.validar_id(doc_id, es_extranjero):
                if not es_extranjero:
                    st.error("❌ La cédula no cumple con la estructura panameña (Ej: 8-777-1234)")
                else:
                    st.warning("⚠️ El pasaporte no requiere cumplir la estructura de cédula nacional.")
            
            # Intentamos el registro
            datos = {
                "nombre_completo": nombre,
                "cedula_ruc": doc_id,
                "es_extranjero": es_extranjero,
                "contacto_emergencia_nombre": cont_nom,
                "contacto_emergencia_tel": cont_tel
            }
            
            exito = gestor_cliente.registrar(datos)
            
            if exito:
                st.success(f"✅ Cliente {nombre} registrado correctamente.")
            else:
                st.error("❌ Error al guardar en la base de datos.")

def modulo_registro(db):
    """Función principal que agrupa los submódulos"""
    tab1, tab2 = st.tabs(["Clientes", "Expedientes"])
    with tab1:
        modulo_clientes(db)
    with tab2:
        st.write("Módulo de expedientes en construcción...")