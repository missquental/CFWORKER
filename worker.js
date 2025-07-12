// Template Cloudflare Worker untuk Blog
// File ini akan di-generate otomatis oleh Streamlit dashboard

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// Sample posts - akan diganti dengan data dari Streamlit
const posts = [
  {
    id: "welcome",
    title: "Selamat Datang di Blog Saya",
    author: "Admin",
    date: "2024-01-15",
    excerpt: "Ini adalah post pertama di blog yang dibuat dengan Cloudflare Worker.",
    content: "Selamat datang di blog saya! <br><br>Blog ini dibuat menggunakan Cloudflare Worker dan dikelola melalui dashboard Streamlit. Anda dapat menambahkan, mengedit, dan menghapus postingan dengan mudah melalui interface yang user-friendly.<br><br>Fitur-fitur yang tersedia:<br>• 📝 Manajemen postingan yang mudah<br>• 🚀 Deploy otomatis ke Cloudflare Worker<br>• 📱 Responsive design<br>• ⚡ Loading yang cepat<br><br>Terima kasih telah mengunjungi blog saya!"
  },
  {
    id: "tutorial-cloudflare",
    title: "Tutorial Menggunakan Cloudflare Worker",
    author: "Admin", 
    date: "2024-01-16",
    excerpt: "Pelajari cara menggunakan Cloudflare Worker untuk membuat aplikasi web yang cepat dan scalable.",
    content: "Cloudflare Worker adalah platform serverless yang memungkinkan Anda menjalankan JavaScript di edge network Cloudflare.<br><br><strong>Keuntungan Cloudflare Worker:</strong><br>• ⚡ Latency rendah karena berjalan di edge<br>• 🌍 Global distribution<br>• 💰 Pricing yang terjangkau<br>• 🔧 Easy deployment<br><br><strong>Use Cases:</strong><br>• API endpoints<br>• Static site hosting<br>• Edge computing<br>• Request/response manipulation<br><br>Dengan kombinasi Cloudflare Worker dan Streamlit dashboard, Anda dapat membuat dan mengelola blog dengan mudah tanpa perlu server tradisional."
  }
];

const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <meta name="description" content="Blog pribadi yang dibuat dengan Cloudflare Worker">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        }
        header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="1" fill="white" opacity="0.1"/><circle cx="80" cy="40" r="1" fill="white" opacity="0.1"/><circle cx="40" cy="80" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
            opacity: 0.1;
        }
        .blog-title {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }
        .blog-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        .post-card {
            background: white;
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
            position: relative;
            overflow: hidden;
        }
        .post-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        .post-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 48px rgba(0,0,0,0.15);
        }
        .post-title {
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: #2d3748;
            line-height: 1.3;
        }
        .post-meta {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        .post-content {
            color: #4a5568;
            line-height: 1.8;
            font-size: 1rem;
        }
        .post-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            margin-top: 1.5rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .post-link:hover {
            background: rgba(102, 126, 234, 0.1);
            color: #764ba2;
            transform: translateX(4px);
        }
        .post-detail {
            max-width: 900px;
        }
        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 2rem;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .back-link:hover {
            background: rgba(102, 126, 234, 0.1);
            color: #764ba2;
            transform: translateX(-4px);
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #718096;
            border-top: 1px solid #e2e8f0;
            margin-top: 3rem;
            background: rgba(255,255,255,0.8);
            border-radius: 16px;
        }
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            .blog-title {
                font-size: 2.2rem;
            }
            .post-card {
                padding: 1.5rem;
            }
            .post-meta {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {{content}}
        <div class="footer">
            <p>💻 Powered by Cloudflare Worker | 🎨 Managed with Streamlit</p>
        </div>
    </div>
</body>
</html>
`;

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  // Handle CORS for API requests
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (path === '/') {
    return new Response(getHomePage(), {
      headers: { 
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=300'
      }
    });
  }

  if (path.startsWith('/post/')) {
    const postId = path.replace('/post/', '');
    return new Response(getPostPage(postId), {
      headers: { 
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=300'
      }
    });
  }

  // API endpoint untuk mendapatkan posts (untuk debugging)
  if (path === '/api/posts') {
    return new Response(JSON.stringify(posts), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }

  return new Response('404 Not Found', { 
    status: 404,
    headers: { 'Content-Type': 'text/html' }
  });
}

function getHomePage() {
  const postsHtml = posts.map(post => `
    <div class="post-card">
      <h2 class="post-title">${post.title}</h2>
      <div class="post-meta">
        <span>📅 ${post.date}</span>
        <span>✍️ ${post.author}</span>
      </div>
      <div class="post-content">${post.excerpt}</div>
      <a href="/post/${post.id}" class="post-link">
        Baca selengkapnya 
        <span>→</span>
      </a>
    </div>
  `).join('');

  const content = `
    <header>
      <h1 class="blog-title">📝 Blog Saya</h1>
      <p class="blog-subtitle">Berbagi pemikiran dan pengalaman melalui teknologi modern</p>
    </header>
    ${postsHtml}
  `;

  return HTML_TEMPLATE.replace('{{title}}', 'Blog Saya - Beranda').replace('{{content}}', content);
}

function getPostPage(postId) {
  const post = posts.find(p => p.id === postId);
  
  if (!post) {
    const content = `
      <header>
        <h1 class="blog-title">404</h1>
        <p class="blog-subtitle">Halaman tidak ditemukan</p>
      </header>
      <div class="post-card">
        <a href="/" class="back-link">
          <span>←</span> Kembali ke beranda
        </a>
        <h2>Oops! Postingan tidak ditemukan</h2>
        <p>Postingan yang Anda cari mungkin telah dipindahkan atau dihapus.</p>
      </div>
    `;
    
    return HTML_TEMPLATE.replace('{{title}}', '404 - Tidak Ditemukan').replace('{{content}}', content);
  }

  const content = `
    <div class="post-detail">
      <a href="/" class="back-link">
        <span>←</span> Kembali ke beranda
      </a>
      <div class="post-card">
        <h1 class="post-title">${post.title}</h1>
        <div class="post-meta">
          <span>📅 ${post.date}</span>
          <span>✍️ ${post.author}</span>
        </div>
        <div class="post-content">${post.content}</div>
      </div>
    </div>
  `;

  return HTML_TEMPLATE.replace('{{title}}', `${post.title} - Blog Saya`).replace('{{content}}', content);
}
