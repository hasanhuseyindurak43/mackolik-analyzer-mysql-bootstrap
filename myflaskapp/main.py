from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=" ",
        database="mackolik"
    )
    return conn

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Tarih formatını düzenleme fonksiyonu
def format_date(day, month, year):
    day = f"{int(day):02d}"
    month = f"{int(month):02d}"
    return f"{day}.{month}.{year}"

# Maçları getirme endpoint'i
@app.route('/get_matches', methods=['POST'])
def get_matches():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
    else:
        return jsonify({'error': 'Geçersiz istek'}), 400

    matches = cursor.fetchall()
    conn.close()
    return jsonify(matches)

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
        details = {key: match[key] for key in list(match.keys())[6:26]}
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
