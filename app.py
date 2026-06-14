from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
app.secret_key = "perpustakaan123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    'static',
    'images',
    'books'
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Koneksi Database
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",  # sesuaikan password mysql Anda
    database="db_perpustakaan_al_irsyad"
)

@app.route('/')
def login():
    return render_template('auth/login.html')

@app.route('/proses_login', methods=['POST'])
def proses_login():

    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()

    sql = """
    SELECT * FROM users
    WHERE email=%s AND password=%s
    """

    cursor.execute(sql, (email, password))
    user = cursor.fetchone()

    if user:

        session['login'] = True

        session['id_user'] = user[0]
        session['nama'] = user[1]
        session['email'] = user[2]

        session['role'] = user[4]  # sesuaikan index role

        flash('Login Berhasil!', 'success')

        if session['role'] == 'admin':
            return redirect('/dashboard_admin')

        return redirect('/dashboard_user')

@app.route('/dashboard_admin')
def dashboard_admin():

    if 'login' not in session:
        return redirect('/')

    if session['role'] != 'admin':
        flash('Akses ditolak!')
        return redirect('/dashboard_user')

    return render_template(
        'admin/dashboard_admin.html',
        nama=session['nama']
    )

@app.route('/dashboard')
def dashboard():

    if 'login' not in session:
        return redirect('/')

    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Statistik
    cursor.execute("SELECT COUNT(*) FROM buku")
    total_buku = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(stok_tersedia) FROM buku")
    tersedia = cursor.fetchone()[0] or 0

    # Ambil buku terbaru
    cursor.execute("""
        SELECT *
        FROM buku
        ORDER BY id_buku DESC
        LIMIT 8
    """)

    buku = cursor.fetchall()

    return render_template(
        'dashboard.html',
        nama=session['nama'],
        total_buku=total_buku,
        tersedia=tersedia,
        buku=buku
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/kelola_buku')
def kelola_buku():

    if 'login' not in session:
        return redirect('/')

    cursor = db.cursor()

    cursor.execute("""
        SELECT *
        FROM buku
        ORDER BY id_buku DESC
    """)

    buku = cursor.fetchall()

    return render_template(
        'admin/kelola_buku.html',
        nama=session['nama'],
        buku=buku
    )

@app.route('/register')
def register():
    return render_template('auth/register.html')


@app.route('/riwayat')
def riwayat():

    if 'login' not in session:
        return redirect('/')

    return render_template(
        'member/riwayat.html',
        nama=session['nama']
    )

@app.route('/pengaturan')
def pengaturan():

    if 'login' not in session:
        return redirect('/')

    return render_template(
        'member/pengaturan.html',
        nama=session['nama']
    )

@app.route('/tambah_buku')
def tambah_buku():

    if 'login' not in session:
        return redirect('/')

    return render_template(
        'admin/tambah_buku.html',
        nama=session['nama']
    )

@app.route('/simpan_buku', methods=['POST'])
def simpan_buku():

    if 'login' not in session:
        return redirect('/')

    judul = request.form['judul_buku']
    penulis = request.form['penulis']
    penerbit = request.form['penerbit']
    tahun = request.form['tahun_terbit']
    isbn = request.form['isbn']
    bahasa = request.form['bahasa']
    kategori = request.form['kategori']
    genre = request.form['genre']
    deskripsi = request.form['deskripsi']

    jumlah = request.form['jumlah_eksemplar']
    stok = request.form['stok_tersedia']

    status = request.form['status_buku']
    rak = request.form['rak_lokasi']
    tags = request.form['tags']

    file = request.files['sampul']

    nama_file = ""

    if file and file.filename != "":
        nama_file = secure_filename(file.filename)

        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            nama_file
        )

        file.save(file_path)

        print("File disimpan:", file_path)

    cursor = db.cursor()

    sql = """
    INSERT INTO buku(
        judul_buku,
        penulis,
        penerbit,
        tahun_terbit,
        isbn,
        bahasa,
        kategori,
        genre,
        deskripsi,
        sampul,
        jumlah_eksemplar,
        stok_tersedia,
        status_buku,
        rak_lokasi,
        tags
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql,(
        judul,
        penulis,
        penerbit,
        tahun,
        isbn,
        bahasa,
        kategori,
        genre,
        deskripsi,
        nama_file,
        jumlah,
        stok,
        status,
        rak,
        tags
    ))

    db.commit()

    flash('Buku berhasil ditambahkan')

    return redirect('/kelola_buku')

@app.route('/detail_buku/<int:id>')
def detail_buku(id):

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM buku WHERE id_buku=%s",
        (id,)
    )

    buku = cursor.fetchone()

    return render_template(
        'member/detail_buku.html',
        buku=buku,
        nama=session['nama']
    )

@app.route('/hapus_buku/<int:id>')
def hapus_buku(id):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM buku WHERE id_buku=%s",
        (id,)
    )

    db.commit()

    flash('Buku berhasil dihapus')

    return redirect('/kelola_buku')

@app.route('/dashboard_user')
def dashboard_user():

    if 'login' not in session:
        return redirect('/')

    cursor = db.cursor()

    cursor.execute("""
        SELECT *
        FROM buku
        ORDER BY id_buku DESC
        LIMIT 10
    """)

    buku = cursor.fetchall()

    return render_template(
        'member/dashboard_user.html',
        nama=session['nama'],
        buku=buku
    )
    
if __name__ == '__main__':
    app.run(debug=True)