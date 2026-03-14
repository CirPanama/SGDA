import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

class ModuloConfiguracion:
    def __init__(self, db):
        self.db = db
        self.tabla_perfiles = "perfiles"
        self.tabla_inventario = "productos"  # Ajustado a tu JSON
        self.tabla_logs = "logs_sistema"
        self.roles_disponibles = ["usuario", "supervisor", "administrador", "master_it"]

    def registrar_log(self, accion, modulo, detalle):
        """Guarda movimientos en la base de datos"""
        usuario_actual = st.session_state.get('usuario', 'Desconocido')
        rol_actual = st.session_state.get('rol', 'N/A')
        log_data = {
            "usuario": usuario_actual,
            "rol": rol_actual,
            "accion": accion,
            "modulo": modulo,
            "detalle": detalle
        }
        try:
            self.db.insert(self.tabla_logs, log_data)
        except:
            pass

    def render(self):
        st.markdown("<h2 style='color: #707070; font-weight: bold;'>⚙️ Panel de Control Maestro</h2>", unsafe_allow_html=True)
        
        # Creamos pestañas para organizar todo y que no sea una pared de texto
        tab_usuarios, tab_datos, tab_logs, tab_mantenimiento = st.tabs([
            "👥 Usuarios", "📊 Importar/Exportar", "📜 Auditoría (Logs)", "🛡️ Mantenimiento"
        ])

        # --- PESTAÑA 1: GESTIÓN DE USUARIOS ---
        with tab_usuarios:
            st.subheader("Control de Acceso")
            with st.expander("➕ Registrar Nuevo Usuario"):
                with st.form("form_nuevo_usuario"):
                    c1, c2, c3 = st.columns(3)
                    with c1: u = st.text_input("Nombre de Usuario")
                    with c2: p = st.text_input("Contraseña", type="password")
                    with c3: r = st.selectbox("Rol", self.roles_disponibles)
                    
                    if st.form_submit_button("✅ Guardar Usuario"):
                        if u and p:
                            self.db.insert(self.tabla_perfiles, {"usuario": u.lower().strip(), "clave": p, "rol": r})
                            self.registrar_log("Creación", "Configuración", f"Nuevo usuario: {u}")
                            st.success(f"Usuario {u} creado.")
                            st.rerun()

            st.markdown("---")
            st.markdown("### Usuarios Activos")
            usuarios = self.db.fetch(self.tabla_perfiles)
            for user in usuarios:
                with st.container(border=True):
                    col_info, col_rol, col_acc = st.columns([2, 2, 1])
                    with col_info:
                        st.write(f"**{user['usuario']}**")
                        st.caption(f"Rol actual: {user['rol']}")
                    with col_rol:
                        nuevo_rol = st.selectbox("Cambiar Rol", self.roles_disponibles, 
                                               index=self.roles_disponibles.index(user['rol']) if user['rol'] in self.roles_disponibles else 0,
                                               key=f"edit_rol_{user['id']}")
                    with col_acc:
                        if st.button("💾", key=f"btn_save_{user['id']}"):
                            self.db.update(self.tabla_perfiles, {"rol": nuevo_rol}, user['id'])
                            st.toast("Rol actualizado")
                            st.rerun()

        # --- PESTAÑA 2: IMPORTACIÓN Y EXPORTACIÓN ---
        with tab_datos:
            st.subheader("Centro de Datos")
            col_up, col_down = st.columns(2)
            
            with col_up:
                st.info("Subir Inventario desde Excel")
                archivo = st.file_uploader("Archivo .xlsx", type=["xlsx"])
                if archivo:
                    df = pd.read_excel(archivo)
                    if st.button("🚀 Procesar Importación"):
                        registros = df.to_dict(orient='records')
                        for reg in registros:
                            self.db.insert(self.tabla_inventario, reg)
                        self.registrar_log("Importación", "Datos", f"Carga masiva: {len(registros)} items")
                        st.success("¡Importación exitosa!")

            with col_down:
                st.info("Descargar Plantilla")
                columnas = ["barcode", "nombre", "referencia", "stock", "precio_costo", "p5", "p10"]
                df_template = pd.DataFrame(columns=columnas)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_template.to_excel(writer, index=False)
                st.download_button("📥 Bajar Formato Excel", data=output.getvalue(), 
                                 file_name="plantilla_inventario.xlsx", use_container_width=True)

        # --- PESTAÑA 3: LOGS (AUDITORÍA) ---
        with tab_logs:
            st.subheader("Historial de Actividad 24/7")
            try:
                logs_data = self.db.fetch(self.tabla_logs)
                if logs_data:
                    df_logs = pd.DataFrame(logs_data)
                    df_logs['fecha'] = pd.to_datetime(df_logs['fecha']).dt.strftime('%d/%m/%Y %H:%M')
                    st.dataframe(df_logs.sort_values('fecha', ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.warning("No hay registros de actividad.")
            except:
                st.error("Tabla de logs no encontrada en la base de datos.")

        # --- PESTAÑA 4: MANTENIMIENTO Y BACKUP (TU GANANCIA) ---
        with tab_mantenimiento:
            st.subheader("Seguridad y Respaldo")
            st.write("Esta sección permite asegurar la integridad de la información para el plan de mantenimiento.")
            
            with st.container(border=True):
                st.markdown("#### 💾 Generar Backup del Sistema")
                st.write("Descarga un archivo maestro con toda la información de la base de datos.")
                
                if st.button("🛠️ Preparar Respaldo Completo", use_container_width=True):
                    # Recolección de datos
                    data_prod = self.db.fetch("productos")
                    data_ventas = self.db.fetch("ventas")
                    data_perfiles = self.db.fetch("perfiles")
                    
                    output_bak = BytesIO()
                    with pd.ExcelWriter(output_bak, engine='xlsxwriter') as writer:
                        pd.DataFrame(data_prod).to_excel(writer, sheet_name='Inventario', index=False)
                        pd.DataFrame(data_ventas).to_excel(writer, sheet_name='Ventas', index=False)
                        pd.DataFrame(data_perfiles).to_excel(writer, sheet_name='Usuarios', index=False)
                    
                    st.download_button(
                        label="⬇️ Descargar Backup (.xlsx)",
                        data=output_bak.getvalue(),
                        file_name=f"BACKUP_SGE_CIR_{datetime.date.today()}.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )
            
            with st.expander("🚨 Zona de Peligro"):
                st.warning("Estas acciones son irreversibles.")
                if st.button("Borrar Logs Antiguos"):
                    # Aquí iría la lógica de limpieza
                    st.error("Función protegida por seguridad.")