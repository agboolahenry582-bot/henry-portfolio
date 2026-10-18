import os, json
from flask import Flask, request, redirect, session, render_template_string, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "henry-ultimate-vault-final-2026")

# === CONFIG - Set in Render Environment ===
ADMIN_PASS_RAW = os.environ.get("VAULT_PASSWORD", "HenryAdmin@2026")
CLIENT_PASS_RAW = os.environ.get("CLIENT_PASSWORD", "Client1000")
ADMIN_HASH = generate_password_hash(ADMIN_PASS_RAW)
CLIENT_HASH = generate_password_hash(CLIENT_PASS_RAW)
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY", "")
PAYSTACK_LINK = os.environ.get("PAYSTACK_LINK", "https://paystack.com/pay/henryvault")
PRICE = os.environ.get("PRICE", "1000")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATA_FILE = "transactions.json"

def load_tx():
    try:
        with open(DATA_FILE, "r") as f: return json.load(f)
    except: return []

def save_tx(data):
    try:
        with open(DATA_FILE, "w") as f: json.dump(data, f)
    except: pass

# === BEAUTIFUL UI ===
STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://js.paystack.co/v1/inline.js"></script>
<style>
*{font-family:'Outfit',sans-serif;box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(circle at 20% 30%, #3b82f6 0%, #1e1b4b 25%, #0f172a 60%);color:white;display:flex;justify-content:center;align-items:center;padding:20px}
.card{background:rgba(30,41,59,0.85);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.1);padding:32px;border-radius:24px;width:100%;max-width:540px;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
h1,h2,h3{margin:0 0 8px}.small{color:#94a3b8;font-size:13px}
input{width:100%;padding:14px;margin:10px 0;border-radius:12px;border:1px solid #334155;background:#0f172a;color:white;font-size:15px}
.btn{width:100%;padding:14px;border-radius:12px;border:none;font-weight:700;cursor:pointer;font-size:15px;transition:0.2s}
.btn-primary{background:linear-gradient(90deg,#3b82f6,#8b5cf6);color:white}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 10px 25px rgba(59,130,246,0.5)}
.btn-ghost{background:#1e293b;color:white;border:1px solid #334155;margin-top:10px}
.file{background:rgba(15,23,42,0.9);padding:12px 14px;border-radius:12px;margin:8px 0;display:flex;justify-content:space-between;align-items:center;border:1px solid rgba(255,255,255,0.05)}
.badge{padding:4px 10px;border-radius:20px;font-size:11px;background:#3b82f6}
.gradient-text{background:linear-gradient(90deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700}
a{color:#60a5fa;text-decoration:none}
</style>
"""
def page(content):
    return render_template_string(f"<!DOCTYPE html><html><head>{STYLE}</head><body><div class='card'>{content}</div></body></html>")

@app.route("/", methods=["GET","POST"])
def home():
    if session.get("user"): return vault_page()
    error=""
    if request.method=="POST":
        pwd=request.form.get("password","")
        if check_password_hash(ADMIN_HASH,pwd):
            session["user"]="admin"; session["time"]=datetime.now().strftime("%d %b %H:%M"); return redirect("/")
        elif check_password_hash(CLIENT_HASH,pwd):
            session["user"]="client"; session["time"]=datetime.now().strftime("%d %b %H:%M"); return redirect("/")
        else: error="<p style='color:#fb7185;margin-top:10px'>❌ Wrong password — try again</p>"
    return page(f"""
    <div style="text-align:center"><div style="font-size:42px">🔐</div>
    <h1 class="gradient-text">Henry's Private Vault</h1><p class="small">Encrypted • Beautiful • Paystack Secured</p></div>
    <form method="post" style="margin-top:20px"><input type="password" name="password" placeholder="Password ••• hidden" required><button class="btn btn-primary">Unlock Vault →</button></form>
    {error}
    <div style="margin-top:25px;padding-top:20px;border-top:1px solid #334155;text-align:center">
      <p style="font-weight:600">No password?</p><p class="small">Pay ₦{PRICE} to get instant client access</p>
      <button class="btn btn-primary" onclick="payWithPaystack()" style="margin-top:12px">💳 Pay ₦{PRICE} with Paystack</button>
      <p class="small" style="margin-top:10px"><a href="{PAYSTACK_LINK}" target="_blank">Or pay via link</a> • <a href="/pricing">Pricing</a></p>
    </div>
    <script>
    function payWithPaystack(){{
      var key="{PAYSTACK_PUBLIC_KEY}";
      if(!key){{ window.open("{PAYSTACK_LINK}","_blank"); return; }}
      var handler=PaystackPop.setup({{key:key,email:"client@henryvault.com",amount:{PRICE}*100,currency:"NGN",
        callback:function(r){{ window.location.href="/pay-success?ref="+r.reference; }},
        onClose:function(){{ alert("Payment cancelled"); }}
      }}); handler.openIframe();
    }}
    </script>
    """)

@app.route("/pricing")
def pricing():
    return page(f"""
    <h2>💎 Vault Pricing</h2>
    <div class="file"><span>👤 Client<br><span class="small">View & Download</span></span><b>₦{PRICE}</b></div>
    <div class="file" style="border:1px solid #8b5cf6"><span>👑 Admin (You)<br><span class="small">Upload, Delete, Wallet, Full Control</span></span><b>₦5000</b></div>
    <button class="btn btn-primary" onclick="window.location.href='/'">Pay & Get Access</button>
    <p style="text-align:center;margin-top:15px"><a href="/">← Back</a></p>
    """)

@app.route("/pay-success")
def pay_success():
    ref=request.args.get("ref","PAY-"+datetime.now().strftime("%H%M%S"))
    tx=load_tx(); tx.append({"ref":ref,"time":datetime.now().strftime("%d %b %H:%M"),"amount":PRICE}); save_tx(tx)
    return page(f"""
    <div style="text-align:center"><div style="font-size:50px">🎉</div><h2>Payment Successful!</h2><p class="small">Ref: {ref} • ₦{PRICE} paid</p>
    <div style="background:#0f172a;padding:18px;border-radius:14px;margin:20px 0;border:1px dashed #3b82f6">
      <p class="small">Your Client Password (copy now)</p><h2 style="letter-spacing:2px">{CLIENT_PASS_RAW}</h2><p class="small">Use it to login</p>
    </div>
    <button class="btn btn-primary" onclick="window.location.href='/'">Unlock Vault Now →</button>
    <p class="small" style="margin-top:12px">Money sent to your Paystack bank account!</p></div>
    """)

def vault_page():
    user=session.get("user"); files=os.listdir(UPLOAD_FOLDER)
    files_html="".join([f"<div class=file><span>📁 {f}</span><span><a href='/download/{f}'>⬇️</a> {' <a href=/delete/'+f+' style=color:#fb7185;margin-left:8px>🗑️</a>' if user=='admin' else ''}</span></div>" for f in files]) or "<p class=small>No files yet — upload first file</p>"
    upload_form=f"""<form method="post" enctype="multipart/form-data" action="/upload"><input type="file" name="file" required><button class="btn btn-primary">☁️ Upload to Cloud</button></form>""" if user=="admin" else "<p class=small>🔒 Client mode — view & download only</p>"
    wallet_btn=f"""<button class="btn btn-ghost" onclick="window.location.href='/wallet'">💰 Wallet — See Money Earned</button>""" if user=="admin" else ""
    return page(f"""
    <div style="display:flex;justify-content:space-between"><h3>Welcome {user.upper()} <span class="badge">{user}</span></h3><a href="/logout">Logout</a></div>
    <p class="small">Logged: {session.get("time")} • Secured by Paystack</p><hr style="border-color:#334155;margin:18px 0">
    {upload_form}<h4 style="margin:18px 0 10px">Files ({len(files)})</h4>{files_html}
    {wallet_btn}<button class="btn btn-ghost" onclick="window.location.href='/pricing'">💎 Upgrade</button>
    """)

@app.route("/wallet")
def wallet():
    if session.get("user")!="admin": return redirect("/")
    tx=load_tx(); total=len(tx)*int(PRICE)
    tx_html="".join([f"<div class=file><span>💳 {t['ref']}<br><span class=small>{t['time']}</span></span><span>₦{t['amount']}</span></div>" for t in reversed(tx)]) or "<p class=small>No payments yet — share your vault link!</p>"
    return page(f"""
    <h2>💰 My Wallet</h2>
    <div style="background:linear-gradient(90deg,#3b82f6,#8b5cf6);padding:22px;border-radius:18px;text-align:center;margin:15px 0">
      <p class="small" style="color:white">Total Earned (in vault record)</p><h1 style="font-size:38px;margin:8px 0">₦{total:,}</h1><p class="small" style="color:white">{len(tx)} payments • Real money in your bank via Paystack</p>
    </div><h4>Payments</h4>{tx_html}
    <button class="btn btn-ghost" onclick="window.location.href='/'">← Back to Vault</button>
    """)

@app.route("/upload", methods=["POST"])
def upload():
    if session.get("user")!="admin": return redirect("/")
    f=request.files.get("file")
    if f: f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
    return redirect("/")

@app.route("/download/<path:name>")
def download(name):
    if not session.get("user"): return redirect("/")
    return send_from_directory(UPLOAD_FOLDER, name, as_attachment=True)

@app.route("/delete/<path:name>")
def delete_file(name):
    if session.get("user")!="admin": return redirect("/")
    try: os.remove(os.path.join(UPLOAD_FOLDER, name))
    except: pass
    return redirect("/")

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
