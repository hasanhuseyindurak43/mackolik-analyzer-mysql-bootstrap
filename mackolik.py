from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from openpyxl import Workbook
import sqlite3
import pymysql
import time
import os

class mysql_veri_kaydet():
    def __init__(self):

        # SQLite bağlantısı
        sqlite_conn = sqlite3.connect("mackolik.db")
        sqlite_cursor = sqlite_conn.cursor()

        # MySQL bağlantısı
        mysql_conn = pymysql.connect(
            host="localhost",
            user="root",  # MySQL kullanıcı adınızı buraya yazın
            password=" ",  # MySQL şifrenizi buraya yazın
            database="mackolik"  # MySQL'de kullanacağınız veritabanı adı
        )
        mysql_cursor = mysql_conn.cursor()

        # MySQL'de tabloyu oluştur
        create_table_query = """
        CREATE TABLE IF NOT EXISTS maclar (
            tarih TEXT,
            saat TEXT,
            ev TEXT,
            misafir TEXT,
            iy TEXT,
            ms TEXT,
            ms1 TEXT,
            msx TEXT,
            ms2 TEXT,
            iys1 TEXT,
            iysx TEXT,
            iys2 TEXT,
            kgvar TEXT,
            kgyok TEXT,
            iybirbucukalt TEXT,
            iybirbucukust TEXT,
            tgbirbucukalt TEXT,
            tgbirbucukust TEXT,
            tgikibucukalt TEXT,
            tgikibucukust TEXT,
            tgucbucukalt TEXT,
            tgucbucukust TEXT,
            tgsifrbir TEXT,
            tgikiuc TEXT,
            tgdortalti TEXT,
            tgyedi TEXT
        )
        """
        mysql_cursor.execute(create_table_query)
        mysql_conn.commit()

        # SQLite'dan verileri oku
        sqlite_cursor.execute("SELECT * FROM maclar")
        rows = sqlite_cursor.fetchall()

        sorgu = """SELECT COUNT(*) FROM maclar WHERE tarih = %s AND saat = %s AND ev = %s AND misafir = %s"""

        update_query = """
        UPDATE maclar 
        SET iy = %s, ms = %s, ms1 = %s, msx = %s, ms2 = %s, iys1 = %s, iysx = %s, iys2 = %s, 
            kgvar = %s, kgyok = %s, iybirbucukalt = %s, iybirbucukust = %s, 
            tgbirbucukalt = %s, tgbirbucukust = %s, tgikibucukalt = %s, tgikibucukust = %s, 
            tgucbucukalt = %s, tgucbucukust = %s, tgsifrbir = %s, tgikiuc = %s, 
            tgdortalti = %s, tgyedi = %s 
        WHERE tarih = %s AND saat = %s AND ev = %s AND misafir = %s
        """

        # Verileri MySQL'e ekle
        insert_query = """
        INSERT INTO maclar (
            tarih, saat, ev, misafir, iy, ms, ms1, msx, ms2, iys1, iysx, iys2,
            kgvar, kgyok, iybirbucukalt, iybirbucukust, tgbirbucukalt, tgbirbucukust,
            tgikibucukalt, tgikibucukust, tgucbucukalt, tgucbucukust, tgsifrbir,
            tgikiuc, tgdortalti, tgyedi
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        for row in rows:
            mysql_cursor.execute(sorgu, (row[0], row[1], row[2], row[3],))
            sonuc = mysql_cursor.fetchone()
            if sonuc[0] > 0:
                mysql_cursor.execute(update_query, (
                row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[0],
                row[1], row[2], row[3],))
                mysql_conn.commit()
            else:
                mysql_cursor.execute(insert_query, row)
                mysql_conn.commit()

        # Bağlantıları kapat
        sqlite_conn.close()
        mysql_cursor.close()
        mysql_conn.close()

        print("Veriler başarıyla MySQL'e aktarıldı.")

for i in range(0, 10000):
    # Chrome WebDriver'ı başlat
    driver = webdriver.Chrome()

    # URL'ye git
    driver.get("https://arsiv.mackolik.com/Genis-Iddaa-Programi")

    time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekle

    # XPath ile input öğesini bul
    checkbox = driver.find_element(By.XPATH, '//*[@id="justNotPlayed"]')

    # Öğeye tıklamak
    checkbox.click()

    time.sleep(3)

    # Explicit Wait kullanarak öğeyi bekleyin
    wait = WebDriverWait(driver, 10)
    select_element = wait.until(EC.presence_of_element_located((By.ID, "dayId")))

    # Select sınıfı ile seçenek seç
    select = Select(select_element)
    select.select_by_visible_text("Hepsi")

    time.sleep(5)

    # SQLite veritabanını bağla veya oluştur
    conn = sqlite3.connect("mackolik.db")
    cursor = conn.cursor()

    # Tabloyu oluştur (varsa mevcut tabloyu yeniden oluşturmaz)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maclar (
        tarih TEXT,
        saat TEXT,
        ev TEXT,
        misafir TEXT,
        iy TEXT,
        ms TEXT,
        ms1 TEXT,
        msx TEXT,
        ms2 TEXT,
        iys1 TEXT,
        iysx TEXT,
        iys2 TEXT,
        kgvar TEXT,
        kgyok TEXT,
        iybirbucukalt TEXT,
        iybirbucukust TEXT,
        tgbirbucukalt TEXT,
        tgbirbucukust TEXT,
        tgikibucukalt TEXT,
        tgikibucukust TEXT,
        tgucbucukalt TEXT,
        tgucbucukust TEXT,
        tgsifrbir TEXT,
        tgikiuc TEXT,
        tgdortalti TEXT,
        tgyedi TEXT
    )
    """)
    conn.commit()

    # İlk tarih ve saat değişkenlerini tanımlayın
    current_date = None

    # İlk üç tr hariç tüm satırları seçmek için XPath düzenle
    rows = driver.find_elements(By.XPATH, "//table[@id='resultsList']/tbody/tr[position()>3]")

    # Seçilen satırları işleyin
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        data = [cell.text for cell in cells]

        # Listenin boş olmadığını ve yeterli uzunlukta olduğunu kontrol et
        if len(data) > 0:

            saat = data[0]

            # Eğer 5. eleman mevcut değilse varsayılan olarak boş bir değer ata
            ev = data[5] if len(data) > 5 else "Veri Eksik"

            # Eğer 6. eleman mevcut değilse varsayılan olarak boş bir değer ata
            misafir = data[6] if len(data) > 6 else "Veri Eksik"

            # Eğer 7. eleman mevcut değilse varsayılan olarak boş bir değer ata
            iy = data[7] if len(data) > 7 else "Veri Eksik"

            # Eğer 8. eleman mevcut değilse varsayılan olarak boş bir değer ata
            ms = data[8] if len(data) > 8 else "Veri Eksik"

            # Eğer 9. eleman mevcut değilse varsayılan olarak boş bir değer ata
            ms1 = data[9] if len(data) > 9 else "Veri Eksik"

            # Eğer 10. eleman mevcut değilse varsayılan olarak boş bir değer ata
            msx = data[10] if len(data) > 10 else "Veri Eksik"

            # Eğer 11. eleman mevcut değilse varsayılan olarak boş bir değer ata
            ms2 = data[11] if len(data) > 11 else "Veri Eksik"

            # Eğer 12. eleman mevcut değilse varsayılan olarak boş bir değer ata
            iys1 = data[12] if len(data) > 12 else "Veri Eksik"

            # Eğer 12. eleman mevcut değilse varsayılan olarak boş bir değer ata
            iysx = data[13] if len(data) > 13 else "Veri Eksik"

            # Eğer 14. eleman mevcut değilse varsayılan olarak boş bir değer ata
            iys2 = data[14] if len(data) > 14 else "Veri Eksik"

            # Eğer 20. eleman mevcut değilse varsayılan olarak boş bir değer ata
            kgvar = data[20] if len(data) > 18 else "Veri Eksik"

            # Eğer 21. eleman mevcut değilse varsayılan olarak boş bir değer ata
            kgyok = data[21] if len(data) > 19 else "Veri Eksik"

            # Eğer 25. eleman mevcut değilse varsayılan olarak boş bir değer ata
            iybirbucukalt = data[25] if len(data) > 25 else "Veri Eksik"

            # Eğer 26. eleman mevcut değilse varsayılan olarak boş bir değer ata
            iybirbucuküst = data[26] if len(data) > 26 else "Veri Eksik"

            # Eğer 27. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgbirbucukalt = data[27] if len(data) > 27 else "Veri Eksik"

            # Eğer 28. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgbirbucukust = data[28] if len(data) > 28 else "Veri Eksik"

            # Eğer 29. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgikibucukalt = data[29] if len(data) > 29 else "Veri Eksik"

            # Eğer 30. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgikibucukust = data[30] if len(data) > 30 else "Veri Eksik"

            # Eğer 31. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgucbucukalt = data[31] if len(data) > 31 else "Veri Eksik"

            # Eğer 32. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgucbucukust = data[32] if len(data) > 32 else "Veri Eksik"

            # Eğer 33. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgsifrbir = data[33] if len(data) > 33 else "Veri Eksik"

            # Eğer 34. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgikiuc = data[34] if len(data) > 34 else "Veri Eksik"

            # Eğer 35. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgdortalti = data[35] if len(data) > 35 else "Veri Eksik"

            # Eğer 36. eleman mevcut değilse varsayılan olarak boş bir değer ata
            tgyedi = data[36] if len(data) > 36 else "Veri Eksik"

            # Tarih kontrolü (örneğin, '02.12.2024' formatında)
            try:
                # Eğer veri tarih formatında ise
                date_obj = datetime.strptime(saat, "%d.%m.%Y")

                # Eğer tarih değiştiyse
                if current_date != date_obj:
                    current_date = date_obj
                    print(f"Tarih değişti: {current_date.strftime('%d.%m.%Y')} - Kayıt işlemi başlatıldı.")

            except ValueError:
                # Eğer tarih değilse, saat olduğunu varsayalım (örneğin, '14:30' formatında)
                try:
                    time_obj = datetime.strptime(saat, "%H:%M")
                    if current_date:
                        # "Ev Sahibi" kontrolü
                        if "Ev Sahibi" in ev:
                            continue  # "Ev Sahibi" yazısını boş geç
                        if "Misafir" in misafir:
                            continue
                        if "IY" in iy:
                            continue
                        if "MS" in ms:
                            continue
                        if "VAR" in kgvar:
                            continue
                        if "YOK" in kgyok:
                            continue
                        if "ALT" in iybirbucukalt:
                            continue
                        if "ÜST" in iybirbucuküst:
                            continue
                        if "ALT" in tgbirbucukalt:
                            continue
                        if "ÜST" in tgbirbucukust:
                            continue
                        if "ALT" in tgikibucukalt:
                            continue
                        if "ÜST" in tgikibucukust:
                            continue
                        if "ALT" in tgucbucukalt:
                            continue
                        if "ÜST" in tgucbucukust:
                            continue
                        if "0-1" in tgsifrbir:
                            continue
                        if "2-3" in tgikiuc:
                            continue
                        if "4-6" in tgdortalti:
                            continue
                        if "7+" in tgyedi:
                            continue

                        # Sorgu: Verilerin var olup olmadığını kontrol et
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM maclar 
                            WHERE tarih = ? AND saat = ? AND ev = ? AND misafir = ?
                        """, (current_date.strftime('%d.%m.%Y'), time_obj.strftime('%H:%M'), ev, misafir))
                        # Sonuç al ve kontrol et
                        sonuc = cursor.fetchone()
                        if sonuc[0] > 0:
                            cursor.execute("""
                                UPDATE maclar 
                                SET iy = ?, ms = ?, ms1 = ?, msx = ?, ms2 = ?, iys1 = ?, iysx = ?, iys2 = ?, kgvar = ?, kgyok = ?, 
                                    iybirbucukalt = ?, iybirbucukust = ?, tgbirbucukalt = ?, tgbirbucukust = ?, tgikibucukalt = ?, 
                                    tgikibucukust = ?, tgucbucukalt = ?, tgucbucukust = ?, tgsifrbir = ?, tgikiuc = ?, 
                                    tgdortalti = ?, tgyedi = ? 
                                WHERE tarih = ? AND saat = ? AND ev = ? AND misafir = ?
                            """, (iy, ms, ms1, msx, ms2, iys1, iysx, iys2, kgvar, kgyok, iybirbucukalt, iybirbucuküst,
                                  tgbirbucukalt,
                                  tgbirbucukust, tgikibucukalt, tgikibucukust, tgucbucukalt, tgucbucukust, tgsifrbir,
                                  tgikiuc,
                                  tgdortalti, tgyedi, current_date.strftime('%d.%m.%Y'), time_obj.strftime('%H:%M'), ev,
                                  misafir))

                            conn.commit()

                        else:
                            cursor.execute("""
                                                            INSERT INTO maclar (tarih, saat, ev, misafir, iy, ms, ms1, msx,ms2, iys1, iysx, iys2, kgvar, kgyok, iybirbucukalt, iybirbucukust, tgbirbucukalt, tgbirbucukust, tgikibucukalt, tgikibucukust, tgucbucukalt, tgucbucukust, tgsifrbir, tgikiuc, tgdortalti, tgyedi)
                                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                                            """, (
                            current_date.strftime('%d.%m.%Y'), time_obj.strftime('%H:%M'), ev, misafir, iy, ms, ms1, msx,
                            ms2, iys1, iysx, iys2, kgvar, kgyok, iybirbucukalt, iybirbucuküst, tgbirbucukalt, tgbirbucukust,
                            tgikibucukalt, tgikibucukust, tgucbucukalt, tgucbucukust, tgsifrbir, tgikiuc, tgdortalti,
                            tgyedi))
                            conn.commit()

                        print(f"{current_date.strftime('%d.%m.%Y')} - Saat: {time_obj.strftime('%H:%M')} - Ev: {ev} - Misafir: {misafir} - IY: {iy} - MS: {ms} - MS-1: {ms1} / MS-X: {msx} / MS-2: {ms2} - İY-1: {iys1} / İY-X: {iysx} / İY-2: {iys2} - KG-VAR: {kgvar} / KG-YOK: {kgyok} - İY 1,5 ALT: {iybirbucukalt} / İY 1,5 ÜST: {iybirbucuküst} - TG 1,5 ALT: {tgbirbucukalt} / TG 1,5 ÜST: {tgbirbucukust} - TG 2,5 ALT: {tgikibucukalt} / TG 2,5 ÜST: {tgikibucukust} - TG 3,5 ALT: {tgucbucukalt} / TG 3,5 ÜST: {tgucbucukust} - 0-1: {tgsifrbir} / 2-3: {tgikiuc} / 4-6: {tgdortalti} / 7+: {tgyedi} - Kayıt işlemi yapılacak.")

                    else:
                        print("Tarih henüz belirlenmedi.")
                except ValueError:
                    pass  # Eğer ne tarih ne de saat formatı değilse, hata vermemek için geç
        else:
            print("Boş veya eksik veri bulundu:", data)

    driver.quit()

    mysql_veri_kaydet()

    
    file_name = "mackolik_verileri.xlsx"

    # Dosyayı sil
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"{file_name} başarıyla silindi.")
    else:
        print(f"{file_name} bulunamadı.")


    # MySQL bağlantısı
    mysql_conn = pymysql.connect(
        host="localhost",
        user="barron4335",  # MySQL kullanıcı adınızı buraya yazın
        password="1968Hram",  # MySQL şifrenizi buraya yazın
        database="mackolik"  # MySQL'de kullanacağınız veritabanı adı
    )
    mysql_cursor = mysql_conn.cursor()

    # Verileri çekmek için sorgu
    row_data = []
    mysql_cursor.execute("SELECT * FROM maclar")
    sonuc = mysql_cursor.fetchall()
    if sonuc:
        for row in sonuc:
            row_data.append(list(row))  # Tuple'ları listeye çeviriyoruz

    # Excel dosyasını oluştur
    wb = Workbook()
    ws = wb.active
    ws.title = "Maç Verileri"

    # Başlıklar
    headers = [
        "Tarih", "Saat", "Ev Sahibi", "Misafir", "IY", "MS", "MS-1", "MS-X", "MS-2",
        "İY-1", "İY-X", "İY-2", "KG-Var", "KG-Yok",
        "İY 1,5 A", "İY 1,5 Ü", "TG 1,5 A", "TG 1,5 Ü", "TG 2,5 A", "TG 2,5 Ü",
        "TG 3,5 A", "TG 3,5 Ü", "0-1", "2-3", "4-6", "7+"
    ]
    ws.append(headers)

    # Satır verilerini ekle
    for row in row_data:
        ws.append(row)

    # Excel dosyasını kaydet
    wb.save(file_name)
    print(f"{file_name} Veriler Excel'e kaydedildi.")

    # Veritabanı bağlantısını kapat
    mysql_conn.close()

    time.sleep(2700)
