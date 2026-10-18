import os
from flask import Flask, request, redirect, session, render_template_string, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "henry-final-beautiful-vault-2026-xyz")

# === CONFIG FROM RENDER ENVIRONMENT ===
ADMIN_HASH = generate_password_hash(os.environ.get("VAULT_PASSWORD", "Henry@2026"))
CLIENT_HASH = generate_password_hash(os.environ.get("CLIENT_PASSWORD", "Client1000"))
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY", "") # pk_test_xxx or pk_live_xxx
PAYSTACK_LINK = os.environ.get("PAYSTACK_LINK", "https://paystack.com/pay/yourlink")
PRICE = os.environ.get("PRICE", "1000")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === BEAUTIFUL ULTRA MODERN TEMPLATE ===
STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://js.paystack.co/v1/inline.js"></script>
<style>
*{font-family:'Outfit',sans-serif;box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at 20% 30%, #3b82f6 0%, #1e1b4b 25%, #0f172a 60%);color:white;display:flex;justify-content:center;align-items:center;padding:20px}
.card{background:rgba(30,41,59,0.8);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.1);padding:35px;border-radius:24px;width:100%;max-width:520px;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
h1,h2{margin:0 0 10px}.small{color:#94a3b8;font-size:13px}
input{width:100%;padding:14px;margin:10px 0;border-radius:12px;border:1px solid #334155;background:#0f172a;color:white;font-size:15px}
.btn{width:100%;padding:14px;border-radius:12px;border:none;font-weight:700;cursor:pointer;font-size:15px;transition:0.2s}
.btn-primary{background:linear-gradient(90deg,#3b82f6,#8b5cf6);color:white}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(59,130,246,0.4)}
.btn-ghost{background:#1e293b;color:white;border:1px solid #334155;margin-top:10px}
.file{background:rgba(15,23,42,0.8);padding:12px 14px;border-radius:12px;margin:8px 0;display:flex;justify-content:space-between;align-items:center;border:1px solid rgba(255,255,255,0.05)}
.badge{padding:4px 10px;border-radius:20px;font-size:11px;background:#3b82f6}
.gradient-text{background:linear-gradient(90deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700}
a{color:#60a5fa;text-decoration:none}
</style>
"""

def page(content):
    return render_template_string(f"<!DOCTYPE html><html><head>{STYLE}</head><body><div class='card'>{content}</div></body></html>")

# === LANDING + LOGIN ===
@app.route("/", methods=["GET","POST"])
def home():
    if session.get("user"):
        return vault_page()
    
    error = ""
    if request.method == "POST":
        pwd = request.form.get("password","")
        if check_password_hash(ADMIN_HASH, pwd):
            session["user"]="admin"; return redirect("/")
        elif check_password_hash(CLIENT_HASH, pwd):
            session["user"]="client"; return redirect("/")
        else:
            error="<p style='color:#fb7185;margin-top:10px'>❌ Wrong password</p>"

    return page(f"""
    <div style="text-align:center">
      <div style="font-size:40px">🔐</div>
      <h1 class="gradient-text">Henry's Private Vault</h1>
      <p class="small">Military-grade • Encrypted • Paystack Secured</p>
    </div>
    <form method="post" style="margin-top:20px">
      <input type="password" name="password" placeholder="Enter vault password •••" required>
      <button class="btn btn-primary">Unlock Vault →</button>
    </form>
    {error}
    <div style="margin-top:25px;padding-top:20px;border-top:1px solid #334155;text-align:center">
      <p style="font-weight:600">Don't have password?</p>
      <p class="small">Pay ₦{PRICE} to get client access instantly</p>
      <button class="btn btn-primary" onclick="payWithPaystack()" style="margin-top:10px">💳 Pay ₦{PRICE} with Paystack</button>
      <p class="small" style="margin-top:10px">Or <a href="{PAYSTACK_LINK}" target="_blank">pay via link</a></p>
      <p style="margin-top:15px"><a href="/pricing">See pricing plans →</a></p>
    </div>

    <script>
    function payWithPaystack(){{
      var key = "{PAYSTACK_PUBLIC_KEY}";
      if(!key){{ window.open("{PAYSTACK_LINK}","_blank"); return; }}
      var handler = PaystackPop.setup({{
        key: key,
        email: "client@henryvault.com",
        amount: {PRICE} * 100,
        currency: "NGN",
        callback: function(response){{
          window.location.href = "/pay-success?ref="+response.reference;
        }},
        onClose: function(){{ alert("Payment cancelled"); }}
      }});
      handler.openIframe();
    }}
    </script>
    """)

@app.route("/pricing")
def pricing():
    return page(f"""
    <h2>💎 Vault Plans</h2>
    <div class="file"><span>👤 Client Access<br><span class="small">View & Download only</span></span><span>₦{PRICE}</span></div>
    <div class="file" style="border:1px solid #8b5cf6"><span>👑 Admin Access<br><span class="small">Upload, Delete, Full control</span></span><span>₦5000</span></div>
    <button class="btn btn-primary" onclick="window.location.href='/'">Get Access Now</button>
    <p style="margin-top:15px;text-align:center"><a href="/">← Back to login</a></p>
    """)

@app.route("/pay-success")
def pay_success():
    ref = request.args.get("ref","")
    return page(f"""
    <div style="text-align:center">
      <div style="font-size:50px">🎉</div>
      <h2>Payment Successful!</h2>
      <p class="small">Ref: {ref}</p>
      <div style="background:#0f172a;padding:15px;border-radius:12px;margin:20px 0">
        <p>Your Client Password:</p>
        <h2 style="letter-spacing:2px">{os.environ.get("CLIENT_PASSWORD","Client1000")}</h2>
        <p class="small">Copy and login now</p>
      </div>
      <button class="btn btn-primary" onclick="window.location.href='/'">Unlock Vault Now →</button>
      <p class="small" style="margin-top:15px">Screenshot this page!</p>
    </div>
    """)

def vault_page():
    user = session.get("user")
    files = os.listdir(UPLOAD_FOLDER)
    files_html = "".join([f"<div class=file><span>📁 {f}</span><span><a href='/download/{f}'>⬇️</a> {' <a href=/delete/'+f+' style=color:#fb7185>🗑️</a>' if user=='admin' else ''}</span></div>" for f in files]) or "<p class=small>No files yet. Upload your first file!</p>"
    upload = f"""<form method="post" enctype="multipart/form-data" action="/upload"><input type="file" name="file" required><button class="btn btn-primary">☁️ Upload to Cloud</button></form>""" if user=="admin" else "<p class=small>🔒 Client mode — view & download only. Upgrade to admin to upload.</p>"
    return page(f"""
    <div style="display:flex;justify-content:space-between;align-items:center"><h3>Welcome {user.upper()} <span class="badge">{user}</span></h3><a href="/logout">Logout</a></div>
    <p class="small">Secured by Paystack • {datetime.now().strftime('%d %b %Y')}</p>
    <hr style="border-color:#334155;margin:20px 0">
    {upload}
    <h4 style="margin:20px 0 10px">Your Files ({len(files)})</h4>
    {files_html}
    <button class="btn btn-ghost" onclick="window.location.href='/pricing'">💎 Upgrade Plan</button>
    """)

@app.route("/upload", methods=["POST"])
def upload():
    if session.get("user")!="admin": return redirect("/")
    f = request.files.get("file")
    if f: f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
    return redirect("/")

@app.route("/download/<path:name>")
def download(name):
    if not session.get("user"): return redirect("/")
    return send_from_directory(UPLOAD_FOLDER, name, as_attachment=True)

@app.route("/delete/<path:name>")
def delete(name):
    if session.get("user")!="admin": return redirect("/")
    try: os.remove(os.path.join(UPLOAD_FOLDER, name))
    except: pass
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
