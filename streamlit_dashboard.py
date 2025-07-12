import streamlit as st
import requests
import json
import os
from datetime import datetime
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="Blog Management Dashboard",
    page_icon="📝",
    layout="wide"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .blog-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    .success-msg {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-msg {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'posts' not in st.session_state:
        st.session_state.posts = []
    if 'cf_account_id' not in st.session_state:
        st.session_state.cf_account_id = ""
    if 'cf_api_token' not in st.session_state:
        st.session_state.cf_api_token = ""
    if 'worker_subdomain' not in st.session_state:
        st.session_state.worker_name = ""
    if 'worker_url' not in st.session_state:
        st.session_state.worker_url = ""

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
            "Nama Worker:",
            placeholder="testaja",
            help="Worker akan di-deploy ke [nama].[account-id].workers.dev"
        )
        
        submit = st.form_submit_button("🔗 Connect", use_container_width=True)
        
        if submit:
            if account_id and api_token and subdomain:
                # Test koneksi ke Cloudflare
                if test_cloudflare_connection(account_id, api_token):
                    st.session_state.cf_account_id = account_id
                    st.session_state.cf_api_token = api_token
                    st.session_state.worker_name = subdomain
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Koneksi gagal! Periksa kembali Account ID dan API Token.")
            else:
                st.error("❌ Semua field harus diisi!")

def test_cloudflare_connection(account_id, api_token):
    """Test connection to Cloudflare API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"https://api.cloudflare.com/client/v4/accounts/{account_id}", headers=headers)
        return response.status_code == 200
    except:
        return False

def deploy_worker(script_content):
    """Deploy worker to Cloudflare"""
    try:
        # Dapatkan account info untuk subdomain
        account_info = get_account_info()
        if not account_info:
            st.error("❌ Gagal mendapatkan informasi account!")
            return False
            
        account_subdomain = account_info.get('subdomain', st.session_state.cf_account_id[:8])
        worker_url = f"https://{st.session_state.worker_name}.{account_subdomain}.workers.dev"
        st.session_state.worker_url = worker_url
        
        headers = {
            "Authorization": f"Bearer {st.session_state.cf_api_token}",
            "Content-Type": "application/javascript"
        }
        
        # Deploy script
        url = f"https://api.cloudflare.com/client/v4/accounts/{st.session_state.cf_account_id}/workers/scripts/{st.session_state.worker_name}"
        
        response = requests.put(url, headers=headers, data=script_content)
        
        if response.status_code == 200:
            # Setup custom domain/route jika diperlukan
            setup_worker_route()
            return True
        else:
            st.error(f"❌ Deploy gagal: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error deploying worker: {str(e)}")
        return False

def get_account_info():
    """Dapatkan informasi account Cloudflare"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.cf_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"https://api.cloudflare.com/client/v4/accounts/{st.session_state.cf_account_id}", headers=headers)
        if response.status_code == 200:
            return response.json().get('result', {})
        return None
    except:
        return None

def setup_worker_route():
    """Setup routing untuk worker"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.cf_api_token}",
            "Content-Type": "application/json"
        }
        
        # Enable subdomain untuk worker
        subdomain_url = f"https://api.cloudflare.com/client/v4/accounts/{st.session_state.cf_account_id}/workers/scripts/{st.session_state.worker_name}/subdomain"
        subdomain_data = {"enabled": True}
        
        requests.post(subdomain_url, headers=headers, json=subdomain_data)
        
        # Setup custom domain jika ada
        setup_custom_domain()
        
    except Exception as e:
        # Tidak masalah jika custom domain gagal
        pass

def setup_custom_domain():
    """Setup custom domain untuk worker (opsional)"""
    try:
        # Cek apakah ada domain yang bisa digunakan
        headers = {
            "Authorization": f"Bearer {st.session_state.cf_api_token}",
            "Content-Type": "application/json"
        }
        
        # List zones/domains
        zones_response = requests.get(f"https://api.cloudflare.com/client/v4/zones", headers=headers)
        if zones_response.status_code == 200:
            zones = zones_response.json().get('result', [])
            if zones:
                # Gunakan domain pertama yang tersedia
                zone = zones[0]
                zone_id = zone['id']
                domain = zone['name']
                
                # Setup worker route
                route_data = {
                    "pattern": f"blog.{domain}/*",
                    "script": st.session_state.worker_name
                }
                
                route_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/workers/routes"
                route_response = requests.post(route_url, headers=headers, json=route_data)
                
                if route_response.status_code == 200:
                    custom_url = f"https://blog.{domain}"
                    st.session_state.worker_url = custom_url
                    st.success(f"✅ Custom domain setup: {custom_url}")
            
    except Exception as e:
        # Tidak masalah jika custom domain gagal
        pass
def generate_worker_script():
    """Generate worker script dengan posts dari session state"""
    posts_json = json.dumps(st.session_state.posts, indent=2)
    
    worker_script = f"""// Blog Worker untuk Cloudflare
addEventListener('fetch', event => {{
  event.respondWith(handleRequest(event.request))
}})

const posts = {posts_json};

const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 3rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .blog-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .blog-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .post-card {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .post-card:hover {{
            transform: translateY(-2px);
        }}
        .post-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #2d3748;
        }}
        .post-meta {{
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        .post-content {{
            color: #4a5568;
            line-height: 1.7;
        }}
        .post-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            margin-top: 1rem;
        }}
        .post-link:hover {{
            color: #764ba2;
        }}
        .post-detail {{
            max-width: 900px;
        }}
        .back-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 2rem;
            font-weight: 500;
        }}
        .back-link:hover {{
            color: #764ba2;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            .blog-title {{
                font-size: 2rem;
            }}
            .post-card {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {{content}}
    </div>
</body>
</html>
`;

async function handleRequest(request) {{
  const url = new URL(request.url);
  const path = url.pathname;

  if (path === '/') {{
    return new Response(getHomePage(), {{
      headers: {{ 'Content-Type': 'text/html' }}
    }});
  }}

  if (path.startsWith('/post/')) {{
    const postId = path.replace('/post/', '');
    return new Response(getPostPage(postId), {{
      headers: {{ 'Content-Type': 'text/html' }}
    }});
  }}

  return new Response('404 Not Found', {{ status: 404 }});
}}

function getHomePage() {{
  const postsHtml = posts.map(post => `
    <div class="post-card">
      <h2 class="post-title">${{post.title}}</h2>
      <div class="post-meta">📅 ${{post.date}} | ✍️ ${{post.author}}</div>
      <div class="post-content">${{post.excerpt}}</div>
      <a href="/post/${{post.id}}" class="post-link">Baca selengkapnya →</a>
    </div>
  `).join('');

  const content = `
    <header>
      <h1 class="blog-title">📝 Blog Saya</h1>
      <p class="blog-subtitle">Berbagi pemikiran dan pengalaman</p>
    </header>
    ${{postsHtml}}
  `;

  return HTML_TEMPLATE.replace('{{title}}', 'Blog Saya').replace('{{content}}', content);
}}

function getPostPage(postId) {{
  const post = posts.find(p => p.id === postId);
  
  if (!post) {{
    return HTML_TEMPLATE.replace('{{title}}', '404 Not Found').replace('{{content}}', `
      <header>
        <h1 class="blog-title">404</h1>
        <p class="blog-subtitle">Post tidak ditemukan</p>
      </header>
      <div class="post-card">
        <a href="/" class="back-link">← Kembali ke beranda</a>
      </div>
    `);
  }}

  const content = `
    <div class="post-detail">
      <a href="/" class="back-link">← Kembali ke beranda</a>
      <div class="post-card">
        <h1 class="post-title">${{post.title}}</h1>
        <div class="post-meta">📅 ${{post.date}} | ✍️ ${{post.author}}</div>
        <div class="post-content">${{post.content}}</div>
      </div>
    </div>
  `;

  return HTML_TEMPLATE.replace('{{title}}', post.title).replace('{{content}}', content);
}}
"""
    
    return worker_script

def main_dashboard():
    """Main dashboard interface"""
    st.markdown('<div class="main-header"><h1>📝 Blog Management</h1></div>', unsafe_allow_html=True)
    
    # Sidebar untuk navigasi
    with st.sidebar:
        st.header("🎛️ Menu")
        page = st.selectbox("Pilih Halaman:", ["📋 Kelola Post", "🚀 Deploy", "⚙️ Settings"])
        
        st.markdown("---")
        if st.session_state.worker_url:
            st.markdown(f"**Worker URL:**  \n{st.session_state.worker_url}")
        else:
            account_info = get_account_info()
            if account_info:
                subdomain = account_info.get('subdomain', st.session_state.cf_account_id[:8])
                estimated_url = f"{st.session_state.worker_name}.{subdomain}.workers.dev"
                st.markdown(f"**Estimated URL:**  \n`{estimated_url}`")
        
        if st.button("🔓 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    if page == "📋 Kelola Post":
        manage_posts()
    elif page == "🚀 Deploy":
        deploy_page()
    elif page == "⚙️ Settings":
        settings_page()

def manage_posts():
    """Interface untuk mengelola posts"""
    st.header("📋 Kelola Postingan")
    
    # Form untuk post baru
    with st.expander("➕ Tambah Post Baru", expanded=True):
        with st.form("new_post"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Judul Post:")
                author = st.text_input("Penulis:", value="Admin")
            
            with col2:
                post_id = st.text_input("ID Post:", placeholder="contoh: post-1")
                date = st.date_input("Tanggal:", value=datetime.now())
            
            excerpt = st.text_area("Excerpt/Ringkasan:", height=100)
            content = st.text_area("Konten Post:", height=300)
            
            if st.form_submit_button("💾 Simpan Post", use_container_width=True):
                if title and post_id and content:
                    new_post = {
                        "id": post_id,
                        "title": title,
                        "author": author,
                        "date": date.strftime("%Y-%m-%d"),
                        "excerpt": excerpt,
                        "content": content.replace("\n", "<br>")
                    }
                    st.session_state.posts.append(new_post)
                    st.success("✅ Post berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("❌ Judul, ID, dan Konten wajib diisi!")
    
    # Daftar posts yang ada
    st.subheader("📚 Daftar Postingan")
    
    if st.session_state.posts:
        for i, post in enumerate(st.session_state.posts):
            with st.container():
                st.markdown(f"""
                <div class="blog-card">
                    <h3>{post['title']}</h3>
                    <p><strong>ID:</strong> {post['id']} | <strong>Tanggal:</strong> {post['date']} | <strong>Penulis:</strong> {post['author']}</p>
                    <p>{post['excerpt'][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"🗑️ Hapus", key=f"delete_{i}"):
                        st.session_state.posts.pop(i)
                        st.rerun()
    else:
        st.info("📝 Belum ada postingan. Tambahkan post pertama Anda!")

def deploy_page():
    """Halaman untuk deploy worker"""
    st.header("🚀 Deploy Blog")
    
    # Tampilkan URL target
    if st.session_state.worker_url:
        st.info(f"Worker akan di-deploy ke: **{st.session_state.worker_url}**")
    else:
        account_info = get_account_info()
        if account_info:
            subdomain = account_info.get('subdomain', st.session_state.cf_account_id[:8])
            estimated_url = f"{st.session_state.worker_name}.{subdomain}.workers.dev"
            st.info(f"Worker akan di-deploy ke: **{estimated_url}**")
    
    # Preview posts
    if st.session_state.posts:
        st.subheader("📋 Preview Posts")
        for post in st.session_state.posts:
            st.markdown(f"• **{post['title']}** (ID: {post['id']})")
        
        st.markdown("---")
        
        if st.button("🚀 Deploy Sekarang", type="primary", use_container_width=True):
            with st.spinner("⏳ Deploying worker..."):
                worker_script = generate_worker_script()
                
                if deploy_worker(worker_script):
                    st.success("✅ Worker berhasil di-deploy!")
                    st.balloons()
                    if st.session_state.worker_url:
                        st.markdown(f"🌍 Blog Anda live di: {st.session_state.worker_url}")
                    else:
                        account_info = get_account_info()
                        if account_info:
                            subdomain = account_info.get('subdomain', st.session_state.cf_account_id[:8])
                            worker_url = f"https://{st.session_state.worker_name}.{subdomain}.workers.dev"
                            st.markdown(f"🌍 Blog Anda live di: {worker_url}")
                else:
                    st.error("❌ Deploy gagal! Periksa konfigurasi Cloudflare.")
    else:
        st.warning("⚠️ Tidak ada postingan untuk di-deploy. Tambahkan post terlebih dahulu.")

def settings_page():
    """Halaman pengaturan"""
    st.header("⚙️ Pengaturan")
    
    with st.form("settings_form"):
        st.subheader("🔧 Konfigurasi Cloudflare")
        
        new_account_id = st.text_input("Account ID:", value=st.session_state.cf_account_id)
        new_api_token = st.text_input("API Token:", value=st.session_state.cf_api_token, type="password")
        new_worker_name = st.text_input("Nama Worker:", value=st.session_state.worker_name)
        
        if st.form_submit_button("💾 Update Konfigurasi"):
            st.session_state.cf_account_id = new_account_id
            st.session_state.cf_api_token = new_api_token
            st.session_state.worker_name = new_worker_name
            st.success("✅ Konfigurasi berhasil diupdate!")
    
    st.markdown("---")
    
    # Export/Import data
    st.subheader("📤 Export/Import Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Posts"):
            if st.session_state.posts:
                posts_json = json.dumps(st.session_state.posts, indent=2)
                st.download_button(
                    label="💾 Download posts.json",
                    data=posts_json,
                    file_name="posts.json",
                    mime="application/json"
                )
            else:
                st.warning("Tidak ada posts untuk di-export")
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import Posts", type="json")
        if uploaded_file:
            try:
                imported_posts = json.load(uploaded_file)
                st.session_state.posts = imported_posts
                st.success("✅ Posts berhasil di-import!")
                st.rerun()
            except:
                st.error("❌ File JSON tidak valid!")

# Main app logic
def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        authenticate()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
