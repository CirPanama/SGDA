class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def iniciar_sesion(self, email, password):
        try:
            # Intentamos autenticar con Supabase
            res = self.db.conn.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return res
        except Exception as e:
            st.error(f"Error de acceso: Credenciales incorrectas.")
            return None

    def cerrar_sesion(self):
        self.db.conn.auth.sign_out()
        st.rerun()

    def verificar_sesion(self):
        # Verifica si hay un usuario activo en la sesión de Streamlit
        return self.db.conn.auth.get_user()