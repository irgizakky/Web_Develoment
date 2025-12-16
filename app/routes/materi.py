from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
import MySQLdb.cursors
from datetime import datetime

materi_bp = Blueprint('materi', __name__)

@materi_bp.route('/materi')
def list_materi():
    if 'loggedin' not in session:
        return redirect(url_for('main.login'))
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    
    query = """
        SELECT materi.*, guru.nama as nama_guru 
        FROM materi 
        JOIN guru ON materi.id_guru = guru.id_guru 
        ORDER BY tanggal_upload DESC
    """
    cursor.execute(query)
    materi_list = cursor.fetchall()
    cursor.close()

    return render_template('materi_list.html', materi_list=materi_list, role=session['role'])

@materi_bp.route('/tambah_materi', methods=['GET', 'POST'])
def tambah_materi():
    if 'loggedin' not in session or session['role'] != 'guru':
        flash('Akses ditolak! Hanya Guru yang bisa upload materi.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        judul = request.form['judul']
        deskripsi = request.form['deskripsi']
        link_file = request.form['link_file'] 
        id_guru = session['id']

        cursor = db.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO materi (judul, deskripsi, link_file, id_guru)
                VALUES (%s, %s, %s, %s)
            """, (judul, deskripsi, link_file, id_guru))
            

            id_materi_baru = cursor.lastrowid
            db.connection.commit()
            
            flash('Materi berhasil diupload! Silakan buat kuisnya (opsional).', 'success')
            return redirect(url_for('materi.list_materi'))
            
        except Exception as e:
            db.connection.rollback()
            flash(f'Gagal upload: {str(e)}', 'danger')
        finally:
            cursor.close()

    return render_template('tambah_materi.html')


@materi_bp.route('/materi/<int:id_materi>')
def detail_materi(id_materi):
    if 'loggedin' not in session:
        return redirect(url_for('main.login'))
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM materi WHERE id_materi = %s", (id_materi,))
    materi = cursor.fetchone()
    
    cursor.execute("SELECT * FROM kuis WHERE id_materi = %s", (id_materi,))
    kuis = cursor.fetchone()

    cursor.close()
    return render_template('materi_detail.html', materi=materi, kuis=kuis, role=session['role'])


@materi_bp.route('/buat_kuis/<int:id_materi>', methods=['GET', 'POST'])
def buat_kuis(id_materi):
    if 'loggedin' not in session or session['role'] != 'guru':
        return redirect(url_for('main.dashboard'))
    
    cursor = db.connection.cursor()

    if request.method == 'POST':
        judul_kuis = request.form['judul_kuis']
        durasi = request.form['durasi'] 

        cursor.execute("INSERT INTO kuis (id_materi, judul_kuis, durasi_menit) VALUES (%s, %s, %s)", 
                       (id_materi, judul_kuis, durasi))
        db.connection.commit()
        
        id_kuis_baru = cursor.lastrowid
        flash('Kuis berhasil dibuat! Sekarang tambahkan soalnya.', 'success')
        return redirect(url_for('materi.tambah_soal', id_kuis=id_kuis_baru))
    
    cursor.execute("SELECT judul FROM materi WHERE id_materi = %s", (id_materi,))
    materi = cursor.fetchone()
    cursor.close()

    return render_template('kuis_buat.html', materi=materi, id_materi=id_materi)

@materi_bp.route('/tambah_soal/<int:id_kuis>', methods=['GET', 'POST'])
def tambah_soal(id_kuis):
    if 'loggedin' not in session or session['role'] != 'guru':
        return redirect(url_for('main.dashboard'))
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        pertanyaan = request.form['pertanyaan']
        opsi_a = request.form['opsi_a']
        opsi_b = request.form['opsi_b']
        opsi_c = request.form['opsi_c']
        opsi_d = request.form['opsi_d']
        jawaban_benar = request.form['jawaban_benar']

        cursor.execute("""
            INSERT INTO soal_kuis (id_kuis, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, jawaban_benar)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_kuis, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, jawaban_benar))
        db.connection.commit()
        flash('Soal berhasil ditambahkan!', 'success')
        return redirect(url_for('materi.tambah_soal', id_kuis=id_kuis))
    
    cursor.execute("SELECT * FROM kuis WHERE id_kuis = %s", (id_kuis,))
    kuis = cursor.fetchone()

    cursor.execute("SELECT * FROM soal_kuis WHERE id_kuis = %s ORDER BY id_soal ASC", (id_kuis,))
    soal_list = cursor.fetchall()
    
    cursor.close()
    return render_template('kuis_tambah_soal.html', kuis=kuis, soal_list=soal_list)



@materi_bp.route('/kuis/start/<int:id_kuis>')
def kerjakan_kuis(id_kuis):
    if 'loggedin' not in session or session['role'] != 'siswa':
        return redirect(url_for('main.dashboard'))
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM kuis WHERE id_kuis = %s", (id_kuis,))
    kuis = cursor.fetchone()
    

    cursor.execute("SELECT * FROM soal_kuis WHERE id_kuis = %s ORDER BY RAND()", (id_kuis,))
    soal_list = cursor.fetchall()
    
    cursor.close()
    return render_template('kuis_kerjakan.html', kuis=kuis, soal_list=soal_list)

@materi_bp.route('/kuis/submit/<int:id_kuis>', methods=['POST'])
def submit_kuis(id_kuis):
    if 'loggedin' not in session or session['role'] != 'siswa':
        return redirect(url_for('main.dashboard'))
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT id_soal, jawaban_benar FROM soal_kuis WHERE id_kuis = %s", (id_kuis,))
    kunci_jawaban = cursor.fetchall()
    
    jumlah_soal = len(kunci_jawaban)
    jawaban_benar = 0
    
    for soal in kunci_jawaban:
        id_soal = str(soal['id_soal'])
        kunci = soal['jawaban_benar']
        
        jawaban_siswa = request.form.get(f'q_{id_soal}')
        
        if jawaban_siswa == kunci:
            jawaban_benar += 1
            
    if jumlah_soal > 0:
        nilai_akhir = int((jawaban_benar / jumlah_soal) * 100)
    else:
        nilai_akhir = 0
        
 
    cursor.execute("""
        SELECT materi.judul, materi.id_materi 
        FROM kuis JOIN materi ON kuis.id_materi = materi.id_materi 
        WHERE kuis.id_kuis = %s
    """, (id_kuis,))
    info_materi = cursor.fetchone()
    judul_materi = info_materi['judul']
    id_materi = info_materi['id_materi']
    
    cursor.execute("""
        INSERT INTO nilai (id_siswa, mata_pelajaran, nilai)
        VALUES (%s, %s, %s)
    """, (session['id'], judul_materi, nilai_akhir))
    

    cursor.execute("SELECT * FROM progres_siswa WHERE id_siswa=%s AND id_materi=%s", (session['id'], id_materi))
    cek_progres = cursor.fetchone()
    
    if cek_progres:
        cursor.execute("UPDATE progres_siswa SET status='selesai' WHERE id_progres=%s", (cek_progres['id_progres'],))
    else:
        cursor.execute("INSERT INTO progres_siswa (id_siswa, id_materi, status) VALUES (%s, %s, 'selesai')", 
                       (session['id'], id_materi))

    db.connection.commit()
    cursor.close()
    
    
    return render_template('kuis_hasil.html', nilai=nilai_akhir, benar=jawaban_benar, total=jumlah_soal)
