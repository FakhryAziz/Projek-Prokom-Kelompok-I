from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'spbu_rahasia_2024'

# ─── Database Sederhana (File JSON) ───────────────────────────────────────────
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        default = {
            "users": [
                {"id": 1, "username": "admin", "password": "admin123", "role": "admin", "nama": "Administrator"},
                {"id": 2, "username": "user1",  "password": "user123",  "role": "user",  "nama": "Budi Santoso"},
                {"id": 3, "username": "user2",  "password": "user456",  "role": "user",  "nama": "Siti Rahayu"}
            ],
            "spbu": [
                {
                    "id": 1,
                    "nama": "SPBU POM Bensin Gombel",
                    "alamat": "Jl. Setiabudi No. 65, Gombel, Semarang Selatan",
                    "maps_url": "https://maps.google.com/?q=SPBU+Gombel+Jl+Setiabudi+Semarang",
                    "lat": -7.0509,
                    "lng": 110.4116,
                    "bbm": {
                        "pertalite": {"tersedia": True,  "stok": "Penuh",   "updated": "07:00"},
                        "pertamax":  {"tersedia": True,  "stok": "Sedang",  "updated": "07:00"},
                        "solar":     {"tersedia": True,  "stok": "Penuh",   "updated": "07:00"}
                    }
                },
                {
                    "id": 2,
                    "nama": "SPBU Pertamina Sumurboto",
                    "alamat": "Jl. Ngesrep Timur V No. 18, Sumurboto, Banyumanik",
                    "maps_url": "https://maps.google.com/?q=SPBU+Pertamina+Sumurboto+Semarang",
                    "lat": -7.0561,
                    "lng": 110.4279,
                    "bbm": {
                        "pertalite": {"tersedia": True,  "stok": "Sedang",  "updated": "07:00"},
                        "pertamax":  {"tersedia": True,  "stok": "Penuh",   "updated": "07:00"},
                        "solar":     {"tersedia": False, "stok": "Habis",   "updated": "07:00"}
                    }
                },
                {
                    "id": 3,
                    "nama": "SPBU Pertamina Gas Station UNDIP",
                    "alamat": "Jl. Prof. Sudarto, Tembalang, Kec. Tembalang, Semarang",
                    "maps_url": "https://maps.google.com/?q=SPBU+Pertamina+UNDIP+Tembalang+Semarang",
                    "lat": -7.0498,
                    "lng": 110.4382,
                    "bbm": {
                        "pertalite": {"tersedia": True,  "stok": "Penuh",   "updated": "07:00"},
                        "pertamax":  {"tersedia": False, "stok": "Habis",   "updated": "07:00"},
                        "solar":     {"tersedia": True,  "stok": "Sedikit", "updated": "07:00"}
                    }
                },
                {
                    "id": 4,
                    "nama": "SPBU Pertamina Mulawarman",
                    "alamat": "Jl. Mulawarman Raya, Mangunharjo, Tembalang, Semarang",
                    "maps_url": "https://maps.google.com/?q=SPBU+Pertamina+Mulawarman+Tembalang+Semarang",
                    "lat": -7.0435,
                    "lng": 110.4450,
                    "bbm": {
                        "pertalite": {"tersedia": True,  "stok": "Penuh",   "updated": "07:00"},
                        "pertamax":  {"tersedia": True,  "stok": "Sedikit", "updated": "07:00"},
                        "solar":     {"tersedia": True,  "stok": "Sedang",  "updated": "07:00"}
                    }
                }
            ],
            "riwayat": []
        }
        save_data(default)
        return default
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_user(username, password):
    data = load_data()
    for u in data['users']:
        if u['username'] == username and u['password'] == password:
            return u
    return None

def login_required(role=None):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if role and session['user']['role'] != role:
                flash('Akses ditolak!', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = get_user(username, password)
        if user:
            session['user'] = user
            flash(f'Selamat datang, {user["nama"]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Username atau password salah!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('dashboard.html', spbu_list=data['spbu'], user=session['user'])

@app.route('/admin/update', methods=['GET', 'POST'])
def admin_update():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('dashboard'))
    
    data = load_data()
    
    if request.method == 'POST':
        spbu_id   = int(request.form.get('spbu_id'))
        jenis_bbm = request.form.get('jenis_bbm')
        tersedia  = request.form.get('tersedia') == 'true'
        stok      = request.form.get('stok')
        
        waktu_sekarang = datetime.now().strftime('%H:%M')
        
        for spbu in data['spbu']:
            if spbu['id'] == spbu_id:
                old_status = spbu['bbm'][jenis_bbm]['tersedia']
                spbu['bbm'][jenis_bbm]['tersedia'] = tersedia
                spbu['bbm'][jenis_bbm]['stok']     = stok
                spbu['bbm'][jenis_bbm]['updated']  = waktu_sekarang
                
                # Catat riwayat
                data['riwayat'].insert(0, {
                    "waktu":    datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "admin":    session['user']['nama'],
                    "spbu":     spbu['nama'],
                    "bbm":      jenis_bbm.capitalize(),
                    "dari":     "Tersedia" if old_status else "Tidak Tersedia",
                    "ke":       "Tersedia" if tersedia   else "Tidak Tersedia",
                    "stok":     stok
                })
                # Simpan hanya 50 riwayat terakhir
                data['riwayat'] = data['riwayat'][:50]
                break
        
        save_data(data)
        flash('Data BBM berhasil diperbarui!', 'success')
        return redirect(url_for('admin_update'))
    
    return render_template('admin.html', spbu_list=data['spbu'], user=session['user'], riwayat=data['riwayat'][:10])

@app.route('/api/status')
def api_status():
    data = load_data()
    return jsonify(data['spbu'])
    
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        nama = request.form.get('nama', '').strip()

        data = load_data()
        for user in data['users']:
            if user['username'] == username:
                flash('Username sudah digunakan!', 'error')
                return redirect(url_for('register'))

        new_user = {
            "id": max([u['id'] for u in data['users']], default=0) + 1,
            "username": username,
            "password": password,
            "role": "user",
            "nama": nama
        }

        data['users'].append(new_user)
        save_data(data)

        flash('Registrasi berhasil, silakan login!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/guest')
def guest_login():

    session['user'] = {
        'id': 0,
        'username': 'guest',
        'nama': 'Tamu',
        'role': 'guest'
    }

    flash('⚠️ Anda sedang masuk sebagai tamu', 'info')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
