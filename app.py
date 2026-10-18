from flask import Flask, request, redirect, render_template_string, send_file
import sqlite3, os, base64
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.secret_key = "henry_ultra_modern_2026"
DB = "/tmp/portfolio_modern.db"
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, tech TEXT, link TEXT, status TEXT, date TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS vault (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, note TEXT, data BLOB, size TEXT, date TEXT)")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM projects")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO projects VALUES (NULL,?,?,?,?,?,?)", ("C&S Success School Portal", "Live school management system with role control, ADD/RECORDS separation, receipt system. Used by real school in Lagos.", "Flask, SQLite, Auth, Render", "https://school-portal-4fg5.onrender.com", "Live", "2026"))
        cur.execute("INSERT INTO projects VALUES (NULL,?,?,?,?,?,?)", ("Portfolio Vault System", "This modern portfolio you are seeing - with private encrypted vault storage", "Flask, Glassmorphism, Vault", "#", "Live", "2026"))
        cur.execute("INSERT INTO projects VALUES (NULL,?,?,?,?,?,?)", ("Future E-Commerce", "Paystack integrated store - Coming next", "Flask, Paystack", "#", "Idea", "Future"))
        con.commit()
    con.close()
init()

BASE = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Henry Tims | Developer + Vault</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Space Grotesk',Arial}
body{background:#060a1a;color:#d9e6ff;overflow-x:hidden}
.orb{position:fixed;width:500px;height:500px;border-radius:50%;filter:blur(120px);opacity:0.25;z-index:-1}
.o1{background:#0a4cff;top:-100px;left:-100px} .o2{background:#00e5ff;bottom:-100px;right:-100px}
.nav{position:sticky;top:0;backdrop-filter:blur(20px);background:#060a1a88;border-bottom:1px solid #12204a;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;z-index:10}
.logo{font-weight:700;letter-spacing:1px;color:#4da3ff} .logo span{color:white}
.nav a{color:#8aa8d8;text-decoration:none;margin-left:18px;font-size:14px} .nav a:hover{color:#4da3ff}
.hero{max-width:1100px;margin:auto;padding:80px 24px 40px;display:grid;grid-template-columns:1.2fr 0.8fr;gap:30px;align-items:center}
@media(max-width:800px){.hero{grid-template-columns:1fr}}
.h-title{font-size:54px;line-height:1.1;font-weight:700} .h-title b{background:linear-gradient(90deg,#4da3ff,#00e5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.glass{background:linear-gradient(135deg,#0e1a3a88,#101e4488);backdrop-filter:blur(18px);border:1px solid #1b2f66;border-radius:20px;padding:24px;box-shadow:0 10px 40px #0005}
.btn{display:inline-block;padding:12px 26px;border-radius:30px;font-weight:600;text-decoration:none;margin:6px;font-size:14px;transition:0.2s}
.btn-p{background:linear-gradient(90deg,#1a5cff,#00d2ff);color:white} .btn-p:hover{transform:translateY(-2px);box-shadow:0 8px 20px #0a4cff66}
.btn-g{background:#0e1a3a;border:1px solid #1b2f66;color:#8aa8d8}
.grid{max-width:1100px;margin:auto;padding:20px 24px;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
.card{position:relative;overflow:hidden} .card:hover{transform:translateY(-4px);border-color:#2a4a8a}
.tag{background:#0a1a3a;border:1px solid #1b2f66;color:#6fa8ff;padding:5px 12px;border-radius:30px;font-size:11px;margin:3px;display:inline-block}
.status{position:absolute;top:18px;right:18px;padding:5px 12px;border-radius:30px;font-size:11px;font-weight:700}
.live{background:#00e5ff;color:#001a33} .building{background:#ffd400;color:#1a1a00} .idea{background:#1b2f66;color:#6fa8ff}
input,textarea,select{width:100%;padding:13px;margin:7px 0;border-radius:12px;border:1px solid #1b2f66;background:#060a1a;color:white}
.submit{width:100%;padding:14px;border-radius:12px;border:0;background:linear-gradient(90deg,#1a5cff,#00d2ff);color:white;font-weight:700;cursor:pointer}
.vault-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:15px}
.v-item{background:#0a122a;border:1px dashed #1b2f66;border-radius:14px;padding:16px}
.footer{text-align:center;padding:40px;color:#4a6490;font-size:13px}
</style></head><body>
<div class="orb o1"></div><div class="orb o2"></div>
<div class="nav"><div class="logo">HENRY <span>TIMS</span></div><div><a href="/">Home</a><a href="#projects">Work</a><a href="#vault">Vault</a><a href="/vault" style="color:#00e5ff">🔒 Private</a></div></div>
{{content|safe}}
</body></html>
"""

@app.route("/")
def home():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    projs = con.execute("SELECT * FROM projects ORDER BY id").fetchall()
    vault_count = con.execute("SELECT COUNT(*) FROM vault").fetchone()[0]
    con.close()
    cards=""
    for p in projs:
        sc = "live" if p["status"]=="Live" else "building" if p["status"]=="Building" else "idea"
        link = f"<a href='{p['link']}' target='_blank' class='btn btn-p' style='padding:8px 16px;font-size:12px;margin-top:12px'>View →</a>" if p["link"]!="#" else "<span style='color:#4a6490;font-size:12px;margin-top:12px;display:inline-block'>Soon</span>"
        cards+=f"<div class='glass card'><span class='status {sc}'>{p['status']}</span><h3>{p['title']}</h3><p style='margin:10px 0;color:#8aa8d8;font-size:14px'>{p['description']}</p><div>{''.join([f'<span class=tag>{t.strip()}</span>' for t in p['tech'].split(',')])}</div>{link}</div>"

    content=f"""
    <div class="hero">
    <div>
    <p style="color:#00e5ff;letter-spacing:2px;font-size:12px">AVAILABLE FOR NEW PROJECTS</p>
    <h1 class="h-title">I build <b>modern</b> web apps that work.</h1>
    <p style="margin:18px 0;color:#8aa8d8;line-height:1.6">I'm Henry Tims — Flask developer from Lagos. I turn business problems into clean, fast web apps. My first live product is already used by a school.</p>
    <div style="margin-top:18px"><a class="btn btn-p" href="https://wa.me/2348025591760">WhatsApp: 08025591760</a><a class="btn btn-g" href="mailto:htims380@gmail.com">htims380@gmail.com</a></div>
    </div>
    <div class="glass">
    <h3 style="color:#4da3ff">Private Vault Storage</h3>
    <p style="color:#8aa8d8;font-size:13px;margin:10px 0">🔒 {vault_count} files stored securely</p>
    <p style="font-size:13px;line-height:1.5">I added a modern encrypted vault inside this portfolio — store client files, contracts, notes, passwords. Only you can access with password.</p>
    <a class="btn btn-p" href="/vault" style="width:100%;text-align:center;margin-top:15px">Open Vault →</a>
    </div>
    </div>

    <div id="projects" style="max-width:1100px;margin:auto;padding:10px 24px"><h2>Selected Work — Auto Expanding</h2><p style="color:#4a6490;font-size:13px">Future projects auto-appear here when added from vault admin</p></div>
    <div class="grid">{cards}</div>

    <div id="vault" class="grid" style="margin-top:20px"><div class="glass" style="grid-column:1/-1"><h2>🔒 About Vault Storage</h2><p style="color:#8aa8d8;margin-top:8px">This is not public. It's your personal drive inside portfolio. You can upload PDFs, images, zip, notes. Access via /vault with password <b>henry2026</b>. Even if you build 100 projects, you can manage everything from here.</p></div></div>

    <div class="footer">© 2026 Henry Tims • Lagos, Nigeria • Deep Modern Blue • <a href="https://wa.me/2348025591760">08025591760</a></div>
    """
    return render_template_string(BASE, content=content)

@app.route("/vault", methods=["GET","POST"])
def vault():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    
    if request.method=="POST" and request.form.get("action")=="login":
        if request.form.get("pass")!="henry2026":
            return render_template_string(BASE, content="<div class='glass' style='max-width:400px;margin:80px auto'><p style='color:#ff5a5a'>Wrong password!</p><a href='/vault'>Back</a></div>")
        # show vault
        files = con.execute("SELECT * FROM vault ORDER BY id DESC").fetchall()
        projects = con.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        con.close()
        f_list=""
        for f in files:
            f_list+=f"<div class='v-item'><b>{f['filename']}</b><br><small style='color:#4a6490'>{f['size']} • {f['date']}</small><p style='font-size:12px;color:#8aa8d8;margin:6px 0'>{f['note']}</p><a href='/download/{f['id']}' style='color:#00e5ff;font-size:12px'>Download</a> | <a href='/delete_file/{f['id']}' style='color:#ff5a5a;font-size:12px' onclick=\"return confirm('Delete?')\">Delete</a></div>"
        if not f_list:
            f_list="<p style='color:#4a6490'>No files yet. Upload first file above.</p>"
        
        p_list=""
        for p in projects:
            p_list+=f"<div class='v-item'><b>{p['title']}</b> <small>[{p['status']}]</small><br><a href='/delete_proj/{p['id']}' style='color:#ff5a5a;font-size:11px'>Delete Project</a></div>"

        content=f"""
        <div style="max-width:1100px;margin:auto;padding:24px">
        <h2>Welcome Henry — Private Vault</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:20px">
        <div class="glass">
        <h3>📁 Upload to Vault Storage</h3>
        <form method="post" action="/upload" enctype="multipart/form-data" style="margin-top:12px">
        <input type="hidden" name="pass" value="henry2026">
        <input type="file" name="file" required>
        <input name="note" placeholder="Note e.g. Client contract for C&S">
        <button class="submit">Upload & Store</button>
        </form>
        <div class="vault-grid" style="margin-top:18px">{f_list}</div>
        </div>
        <div class="glass">
        <h3>🚀 Add New Project (Future)</h3>
        <form method="post" action="/add_proj" style="margin-top:12px">
        <input type="hidden" name="pass" value="henry2026">
        <input name="title" placeholder="Title e.g. Hotel App" required>
        <textarea name="desc" placeholder="Description" required></textarea>
        <input name="tech" placeholder="Tech stack" required>
        <input name="link" placeholder="Link or #">
        <select name="status"><option>Live</option><option>Building</option><option>Idea</option></select>
        <button class="submit">Add Project</button>
        </form>
        <div class="vault-grid" style="margin-top:18px">{p_list}</div>
        </div>
        </div>
        <br><a href="/" class="btn btn-g">← Back to Public Portfolio</a>
        </div>
        """
        return render_template_string(BASE, content=content)

    con.close()
    content="""
    <div class="glass" style="max-width:420px;margin:80px auto;text-align:center">
    <h2>🔒 Private Vault</h2>
    <p style="color:#8aa8d8;font-size:13px;margin:10px 0">Enter password to access your storage + project manager</p>
    <form method="post" style="margin-top:18px">
    <input type="hidden" name="action" value="login">
    <input name="pass" type="password" placeholder="Password: henry2026" required>
    <button class="submit">Unlock Vault</button>
    </form>
    <p style="margin-top:15px"><a href="/">← Public View</a></p>
    </div>
    """
    return render_template_string(BASE, content=content)

@app.route("/upload", methods=["POST"])
def upload():
    if request.form.get("pass")!="henry2026":
        return "Wrong pass"
    file = request.files.get("file")
    note = request.form.get("note","")
    if not file:
        return redirect("/vault")
    data = file.read()
    size = f"{len(data)/1024:.1f} KB" if len(data)<1024*1024 else f"{len(data)/1024/1024:.2f} MB"
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO vault (filename, note, data, size, date) VALUES (?,?,?,?,?)", (file.filename, note, data, size, datetime.now().strftime("%d-%m-%Y")))
    con.commit()
    con.close()
    return redirect("/vault")

@app.route("/download/<int:id>")
def download(id):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    f = con.execute("SELECT * FROM vault WHERE id=?", (id,)).fetchone()
    con.close()
    if not f:
        return "Not found"
    return send_file(BytesIO(f["data"]), download_name=f["filename"], as_attachment=True)

@app.route("/delete_file/<int:id>")
def delete_file(id):
    con = sqlite3.connect(DB)
    con.execute("DELETE FROM vault WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/vault")

@app.route("/add_proj", methods=["POST"])
def add_proj():
    if request.form.get("pass")!="henry2026":
        return "Wrong"
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO projects (title, description, tech, link, status, date) VALUES (?,?,?,?,?,?)",
    (request.form.get("title"), request.form.get("desc"), request.form.get("tech"), request.form.get("link"), request.form.get("status"), datetime.now().strftime("%Y")))
    con.commit()
    con.close()
    return redirect("/vault")

@app.route("/delete_proj/<int:id>")
def delete_proj(id):
    con = sqlite3.connect(DB)
    con.execute("DELETE FROM projects WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/vault")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
