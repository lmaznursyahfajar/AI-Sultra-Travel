"""
Autentikasi sederhana untuk Panel Admin SultraTravel.
Kredensial default HARUS diganti melalui st.secrets sebelum aplikasi di-deploy publik.
"""
import hashlib
import streamlit as st

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD_HASH = hashlib.sha256("sultra2026".encode()).hexdigest()


def _get_credentials():
    try:
        username = st.secrets.get("admin_username", DEFAULT_USERNAME)
        password_hash = st.secrets.get("admin_password_hash", DEFAULT_PASSWORD_HASH)
    except Exception:
        username, password_hash = DEFAULT_USERNAME, DEFAULT_PASSWORD_HASH
    return username, password_hash


def check_login(username: str, password: str) -> bool:
    valid_user, valid_hash = _get_credentials()
    return username == valid_user and hashlib.sha256(password.encode()).hexdigest() == valid_hash


def require_login():
    """Menampilkan form login. Mengembalikan True jika sudah terautentikasi."""
    if st.session_state.get("is_admin_logged_in"):
        return True

    st.markdown("### 🔐 Login Admin")
    st.caption("Khusus pengelola data pariwisata. Kredensial default: **admin / sultra2026** "
               "(harap diganti melalui st.secrets sebelum deployment publik).")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Masuk", type="primary")
        if submitted:
            if check_login(username, password):
                st.session_state["is_admin_logged_in"] = True
                st.rerun()
            else:
                st.error("❌ Username atau password salah.")
    return False


def logout_button():
    if st.sidebar.button("🚪 Keluar dari Admin"):
        st.session_state["is_admin_logged_in"] = False
        st.rerun()
