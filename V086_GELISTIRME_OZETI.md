# v0.8.6 geliştirme özeti

v0.8.5 tabanından ayrı çalışma kopyasında Model 3 geliştirildi. 2000/01 başlangıcı, 18 kulüp, tarihsel katalog, alternatif kariyer, eski motorlar ve ekonomi modeli korundu.

- Kurallar çekirdeği: futbol_kurallari.py, saha_motoru.py, mac.py.
- Kariyer ve arayüz: kayit.py, arayuz.py, duran_top_ui.py, mac_gorunum.py.
- Windows girişleri: oyun.py, BASLAT.bat, PAKETLE.bat.
- Doğrulama: test_v086.py, test_v060.py başlık beklentisi, mac_kalibrasyonu_v086.py, kalibrasyon_v086.py ve gorsel_kontrol_v086.py.

Yeni kariyerlerde Model 3 varsayılan. Grafik, maç olaylarını ve motor koordinatlarını okur. Hızlı maç ve 2D kayıt aynı maç nesnesini kullanır. Ayarların ekonomiye veya tarihsel kataloglara veri aktarımı yoktur.
