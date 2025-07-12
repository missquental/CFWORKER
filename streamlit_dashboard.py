def authenticate():
    """Authentication form"""
    st.markdown('<div class="main-header"><h1>🚀 Blog Management System</h1><p>Kelola blog Cloudflare Worker Anda dengan mudah</p></div>', unsafe_allow_html=True)
    
    with st.form("auth_form"):
        st.subheader("🔐 Konfigurasi Cloudflare")
        
        account_id = st.text_input(
            "Account ID Cloudflare:",
            placeholder="Masukkan Account ID dari dashboard Cloudflare",
            help="Bisa ditemukan di dashboard Cloudflare bagian kanan bawah"
        )
        
        api_token = st.text_input(
            "API Token:",
            type="password",
            placeholder="Masukkan API Token dengan permission Workers:Edit",
            help="Buat di https://dash.cloudflare.com/profile/api-tokens"
        )

        subdomain = st.text_input(
            "Subdomain:",
            placeholder="contoh: blog",
            help="Subdomain unik untuk worker"
        )
        
        submit = st.form_submit_button("🔗 Connect", use_container_width=True)
        
        if submit:
            if account_id and api_token and subdomain:
                account_name = get_account_name(account_id, api_token)
                if account_name:
                    full_subdomain = f"{subdomain}.{account_name.replace(' ', '').lower()}"
                    st.session_state.cf_account_id = account_id
                    st.session_state.cf_api_token = api_token
                    st.session_state.worker_subdomain = full_subdomain
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Gagal mengambil nama akun. Periksa API Token dan Account ID.")
            else:
                st.error("❌ Semua field harus diisi!")
