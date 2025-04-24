from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import secrets
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import random

app = Flask(__name__)

# Güvenli bir secret key oluştur
app.secret_key = secrets.token_hex(16)

# Flask-Mail konfigürasyonu
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'barronsoftwares92@gmail.com'
app.config['MAIL_PASSWORD'] = 'zbot ubsr ktbv xdwy'
mail = Mail(app)

# Veritabanı bağlantısı
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="barron4335",
        password="1968Hram",
        database="mackolik"
    )
    return conn

# Kullanıcı modeli
class User:
    @staticmethod
    def create_user(username, password, email):
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
        print(type(username), repr(username))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

# OTP saklamak için geçici bir sözlük
otp_storage = {}

# Yanlış giriş denemelerini takip etmek için sözlük
failed_attempts = {}

# Aktif kullanıcıları takip etmek için küme
active_users = set()

# Ana sayfa
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()

    active_users_count = len(active_users)
    daily_visits = 50  # Örnek değer, gerçek veri için loglama yapılmalı
    weekly_visits = 350
    monthly_visits = 1500

    return render_template('index8.html', active_users_count=active_users_count, total_users=total_users, daily_visits=daily_visits, weekly_visits=weekly_visits, monthly_visits=monthly_visits)


# Kayıt ol sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        email = request.form['email']
        session['email'] = email  # E-posta bilgisini de sakla

        # OTP oluştur ve gönder
        otp = random.randint(100000, 999999)
        otp_storage[email] = otp

        msg = Message('Has Analiz OTP', sender='your_email@gmail.com', recipients=[email])
        msg.body = f'Kayıt işlemi için OTP kodunuz: {otp}'
        mail.send(msg)

        flash('OTP kodunuz e-posta adresinize gönderildi.')
        return redirect(url_for('verify_otp', email=email))

    return render_template('register.html')

# OTP doğrulama sayfası
@app.route('/verify_otp/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    if request.method == 'POST':
        user_otp = request.form['otp']
        if otp_storage.get(email) == int(user_otp):
            # Kullanıcı bilgilerini session'dan al
            username = session.get('username')
            password = session.get('password')

            if username and password:
                # Kullanıcıyı veritabanına kaydet
                User.create_user(username, password, email)
                flash('Kayıt başarılı! Giriş yapabilirsiniz.')
                return redirect(url_for('login'))
            else:
                flash('Kullanıcı bilgileri bulunamadı. Lütfen tekrar kayıt olun.')
                return redirect(url_for('register'))
        else:
            flash('Geçersiz OTP kodu.')

    return render_template('verify_otp.html', email=email)

# Giriş yap sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in failed_attempts and failed_attempts[username]['count'] >= 3:
            last_attempt = failed_attempts[username]['last_attempt']
            if datetime.now() < last_attempt + timedelta(minutes=5):
                flash('5 dakika boyunca giriş yapamazsınız.')
                return redirect(url_for('login'))

        user = User.get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            # Kullanıcı giriş yaparsa, session'a bilgileri ekleyelim
            session['user_id'] = user['id']
            session['username'] = user['username']  # Kullanıcı adını ekliyoruz
            active_users.add(user['id'])
            flash('Başarıyla giriş yapıldı!')
            return redirect(url_for('index'))  # Kullanıcıyı `index` sayfasına yönlendiriyoruz
        else:
            if username in failed_attempts:
                failed_attempts[username]['count'] += 1
                failed_attempts[username]['last_attempt'] = datetime.now()
            else:
                failed_attempts[username] = {'count': 1, 'last_attempt': datetime.now()}
            flash('Geçersiz kullanıcı adı veya şifre.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id')  # Kullanıcının ID'sini al

    if user_id in active_users:
        active_users.remove(user_id)  # Kullanıcıyı aktif listeden çıkar

    session.clear()  # Oturumu temizle
    flash('Başarıyla çıkış yapıldı.')
    return redirect(url_for('index'))  # Ana sayfaya yönlendir


# Maçları getirme endpoint'i
@app.route('/get_matches', methods=['POST'])
def get_matches():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Geçersiz JSON verisi'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM maclar WHERE 1=1"
        params = []

        # Tarih filtresi
        if 'day' in data and 'month' in data and 'year' in data:
            day = data['day']
            month = data['month']
            year = data['year']
            date = f"{int(day):02d}.{int(month):02d}.{year}"
            query += " AND tarih = %s"
            params.append(date)

        # Ev ve misafir takım filtresi
        elif 'ev' in data and 'misafir' in data:
            ev = data['ev']
            misafir = data['misafir']
            query += " AND ev = %s AND misafir = %s"
            params.extend([ev, misafir])

        # Skor filtresi (birden fazla skor seti için)
        elif 'customScores' in data:
            custom_scores = data['customScores']
            if not isinstance(custom_scores, list):
                return jsonify({'error': 'Geçersiz skor verisi'}), 400

            # Her bir skor seti için OR koşulu oluştur
            score_conditions = []
            for score_set in custom_scores:
                iy1 = score_set.get('iy1')
                iy2 = score_set.get('iy2')
                ms1 = score_set.get('ms1')
                ms2 = score_set.get('ms2')

                # Skorların geçerli olup olmadığını kontrol et
                if iy1 is None or iy2 is None or ms1 is None or ms2 is None:
                    continue

                # İlk yarı ve maç sonu skorlarını formatla
                iy_skor = f"{iy1} - {iy2}"
                ms_skor = f"{ms1} - {ms2}"

                # Skor koşulunu ekle
                score_conditions.append("(iy = %s AND ms = %s)")
                params.extend([iy_skor, ms_skor])

            # Eğer en az bir skor seti varsa, OR ile birleştir
            if score_conditions:
                query += " AND (" + " OR ".join(score_conditions) + ")"

        # Oran analizi filtresi (güncellenmiş versiyon)
        elif 'oddsAnalysis' in data:
            odds_conditions = data['oddsAnalysis']

            # Tarih filtresi (oran analizi için özel)
            if odds_conditions and isinstance(odds_conditions, list) and len(odds_conditions) > 0:
                first_condition = odds_conditions[0]
                if 'day' in first_condition and 'month' in first_condition and 'year' in first_condition:
                    day = first_condition['day']
                    month = first_condition['month']
                    year = first_condition['year']
                    if day and month and year:
                        date = f"{int(day):02d}.{int(month):02d}.{year}"
                        query += " AND tarih = %s"
                        params.append(date)

            # Oran tiplerini grupla
            odds_groups = {}
            for odds in odds_conditions:
                odds_type = odds.get('oddsType')
                odds_value = odds.get('oddsValue')

                if not odds_type or not odds_value:
                    continue

                # Oran değerini formatla
                try:
                    if isinstance(odds_value, str):
                        odds_value = odds_value.replace(',', '.')
                    odds_value = "{:.2f}".format(float(odds_value))
                except ValueError:
                    continue

                # Oran tipine göre grupla
                if odds_type not in odds_groups:
                    odds_groups[odds_type] = []
                odds_groups[odds_type].append(odds_value)

            # Oran koşullarını sorguya ekle
            for odds_type, values in odds_groups.items():
                # Oran tipinin geçerli bir sütun olup olmadığını kontrol et
                # (Burada veritabanı sütunlarını kontrol edebilirsiniz)

                # Aynı oran tipi için birden fazla değer varsa OR kullan
                if len(values) > 1:
                    or_conditions = " OR ".join([f"REPLACE(TRIM({odds_type}), ',', '.') <= %s" for _ in values])
                    query += f" AND ({or_conditions})"
                else:
                    # Tek değer varsa direkt AND kullan
                    query += f" AND REPLACE(TRIM({odds_type}), ',', '.') <= %s"

                params.extend(values)

        # Sorguyu çalıştır
        cursor.execute(query, params)
        matches = cursor.fetchall()
        print(f"Sonuç: {matches}")
        print(f"Sorgu : {query, params}")
        return jsonify(matches)
    except mysql.connector.Error as err:
        print(f"SQL sorgusu hatası: {err}")
        return jsonify({'error': 'SQL sorgusu hatası'}), 500
    finally:
        conn.close()

# Maç detaylarını getirme endpoint'i
@app.route('/get_match_details', methods=['POST'])
def get_match_details():
    data = request.get_json()
    ev = data['ev']
    misafir = data['misafir']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM maclar WHERE ev = %s AND misafir = %s", (ev, misafir))
    match = cursor.fetchone()
    conn.close()

    if match:
        # Detayları JSON olarak döndür
        details = {key: match[key] for key in list(match.keys())[6:26]}  # İlgili sütunları seç
        return jsonify({'details': details})
    else:
        return jsonify({'error': 'Maç bulunamadı'}), 404

# Takımları getirme endpoint'i
@app.route('/get_teams', methods=['GET'])
def get_teams():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT ev FROM maclar")
    ev_teams = [row['ev'] for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT misafir FROM maclar")
    misafir_teams = [row['misafir'] for row in cursor.fetchall()]
    conn.close()
    return jsonify({'ev': ev_teams, 'misafir': misafir_teams})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)