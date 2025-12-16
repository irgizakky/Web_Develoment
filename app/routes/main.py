from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensions import db
import MySQLdb.cursors

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return render_template('home.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        nama = request.form.get('nama')
        kelas = request.form.get('kelas')
        nomor_induk = request.form.get('nomor_induk')

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        
        
        if role == 'siswa':
            cursor.execute('SELECT * FROM siswa WHERE nis = %s', (nomor_induk,))
            account = cursor.fetchone()

            if not account:
                cursor.execute('INSERT INTO siswa (nama, kelas, nis) VALUES (%s, %s, %s)', (nama, kelas, nomor_induk))
                db.connection.commit()
                cursor.execute('SELECT * FROM siswa WHERE nis = %s', (nomor_induk,))
                account = cursor.fetchone()
                flash(f'Selamat datang, {nama}. Akun berhasil dibuat.', 'success')
            else:
                if account['nama'].lower() != nama.lower():
                    flash('NIS terdaftar dengan nama berbeda!', 'danger')
                    return redirect(url_for('main.login'))
                flash(f'Selamat datang kembali, {nama}!', 'success')

            session['loggedin'] = True
            session['id'] = account['id_siswa']
            session['nama'] = account['nama']
            session['kelas'] = account['kelas']
            session['role'] = 'siswa'
            return redirect(url_for('main.dashboard'))
        
        
        elif role == 'guru':
            cursor.execute('SELECT * FROM guru WHERE nip = %s', (nomor_induk,))
            account = cursor.fetchone()

            if not account:
            
                cursor.execute('INSERT INTO guru (nama, kelas, nip) VALUES (%s, %s, %s)', (nama, kelas, nomor_induk))
                db.connection.commit()
                cursor.execute('SELECT * FROM guru WHERE nip = %s', (nomor_induk,))
                account = cursor.fetchone()
                flash(f'Selamat datang, Pak/Bu {nama}.', 'success')
            else:
                if account['nama'].lower() != nama.lower():
                    flash('NIP terdaftar dengan nama berbeda!', 'danger')
                    return redirect(url_for('main.login'))
                flash(f'Selamat datang kembali, Pak/Bu {nama}!', 'success')

            session['loggedin'] = True
            session['id'] = account['id_guru']
            session['nama'] = account['nama']
            session['kelas'] = account['kelas']
            session['role'] = 'guru'
            return redirect(url_for('main.dashboard'))
        
        cursor.close()

    return render_template('login.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Harap login terlebih dahulu', 'warning')
        return redirect(url_for('main.login'))
    
    role = session['role']
    user_id = session['id']
    nama = session['nama']

    
    materi_selesai = 0
    tugas_pending = 0
    rata_rata_nilai = 0
    total_materi = 0
    total_siswa = 0
    total_kelas = 0
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

    
    if role == 'siswa':
        
        cursor.execute("SELECT COUNT(*) as total FROM progres_siswa WHERE id_siswa = %s AND status = 'selesai'", (user_id,))
        res = cursor.fetchone()
        materi_selesai = res['total'] if res else 0

        
        cursor.execute("SELECT AVG(nilai) as rata FROM nilai WHERE id_siswa = %s", (user_id,))
        res_nilai = cursor.fetchone()
        if res_nilai and res_nilai['rata']:
            rata_rata_nilai = round(res_nilai['rata'], 1)

        
        cursor.execute("SELECT COUNT(*) as total FROM materi")
        res_materi = cursor.fetchone()
        total_materi_semua = res_materi['total'] if res_materi else 0
        tugas_pending = total_materi_semua - materi_selesai
        if tugas_pending < 0: tugas_pending = 0

    
    elif role == 'guru':
        cursor.execute("SELECT COUNT(*) as total FROM materi WHERE id_guru = %s", (user_id,))
        res = cursor.fetchone()
        total_materi = res['total'] if res else 0

        cursor.execute("SELECT COUNT(*) as total FROM siswa")
        res = cursor.fetchone()
        total_siswa = res['total'] if res else 0

        cursor.execute("SELECT COUNT(DISTINCT kelas) as total FROM siswa")
        res = cursor.fetchone()
        total_kelas = res['total'] if res else 0

    
    query_aktivitas = """
        SELECT materi.judul, materi.tanggal_upload, guru.nama as nama_guru, 'materi' as tipe
        FROM materi
        JOIN guru ON materi.id_guru = guru.id_guru
        ORDER BY materi.tanggal_upload DESC
        LIMIT 5
    """
    cursor.execute(query_aktivitas)
    aktivitas_list = cursor.fetchall()

    cursor.close()

    return render_template('dashboard.html', 
                           nama=nama, 
                           role=role,
                           materi_selesai=materi_selesai,
                           tugas_pending=tugas_pending,
                           rata_rata_nilai=rata_rata_nilai,
                           total_materi=total_materi,
                           total_siswa=total_siswa,
                           total_kelas=total_kelas,
                           aktivitas_list=aktivitas_list)


@main_bp.route('/data_nilai')
def data_nilai():
    if 'loggedin' not in session:
        return redirect(url_for('main.login'))
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    role = session['role']
    user_id = session['id']

    if role == 'guru':
        query = """
            SELECT nilai.*, siswa.nama as nama_siswa, siswa.kelas 
            FROM nilai 
            JOIN siswa ON nilai.id_siswa = siswa.id_siswa 
            ORDER BY siswa.kelas ASC, siswa.nama ASC
        """
        cursor.execute(query)
    
    elif role == 'siswa':
        query = """
            SELECT nilai.*, siswa.nama as nama_siswa, siswa.kelas 
            FROM nilai 
            JOIN siswa ON nilai.id_siswa = siswa.id_siswa 
            WHERE nilai.id_siswa = %s
            ORDER BY nilai.id_nilai DESC
        """
        cursor.execute(query, (user_id,))
        
    data_nilai = cursor.fetchall()
    cursor.close()

    return render_template('guru_nilai.html', data_nilai=data_nilai)


@main_bp.route('/logout')
def logout():
    session.clear() 
    flash('Anda telah logout', 'info')
    return redirect(url_for('main.login'))
