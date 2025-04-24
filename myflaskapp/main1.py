from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="barron4335",
        password="1968Hram",
        database="mackolik"
    )
    return conn

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index_two')
def index_two():
    return render_template('index2.html')

@app.route('/index_three')
def index_three():
    return render_template('index3.html')

# Tarih formatını düzenleme fonksiyonu
def format_date(day, month, year):
    day = f"{int(day):02d}"
    month = f"{int(month):02d}"
    return f"{day}.{month}.{year}"

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
        if 'day' in data and 'month' in data and 'year' in data:
            day = data['day']
            month = data['month']
            year = data['year']
            date = format_date(day, month, year)
            cursor.execute("SELECT * FROM maclar WHERE tarih = %s", (date,))
        elif 'ev' in data and 'misafir' in data:
            ev = data['ev']
            misafir = data['misafir']
            cursor.execute("SELECT * FROM maclar WHERE ev = %s AND misafir = %s", (ev, misafir))
        elif 'iy1' in data and 'iy2' in data and 'ms1' in data and 'ms2' in data:
            iy1 = data['iy1']
            iy2 = data['iy2']
            ms1 = data['ms1']
            ms2 = data['ms2']
            iy_skor = f"{iy1} - {iy2}"
            ms_skor = f"{ms1} - {ms2}"
            cursor.execute("SELECT * FROM maclar WHERE iy = %s AND ms = %s", (iy_skor, ms_skor))
        elif 'oddsType' in data and 'oddsValue' in data:
            odds_type = data['oddsType']
            odds_value = data['oddsValue']

            # Eğer oddsValue bir string ise virgülü noktaya çevir
            if isinstance(odds_value, str):
                odds_value = odds_value.replace(',', '.')
            # Eğer oddsValue bir float ise doğrudan kullan
            elif isinstance(odds_value, float):
                pass
            else:
                return jsonify({'error': 'Geçersiz oddsValue değeri'}), 400

            # Debugging için sorgu ve parametreleri yazdır
            query = f"SELECT * FROM maclar WHERE REPLACE(TRIM({odds_type}), ',', '.') = %s"
            odds_value = str(odds_value).replace(',', '.')
            print(f"SQL Sorgusu: {query}")
            print(f"Parametreler: {odds_value}")

            cursor.execute(query, (odds_value,))
        else:
            return jsonify({'error': 'Geçersiz istek'}), 400

        matches = cursor.fetchall()
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
    app.run(host='0.0.0.0', port=5000, debug=True)