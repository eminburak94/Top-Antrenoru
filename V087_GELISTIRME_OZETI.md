# v0.8.7 geliştirme özeti

Ayrı Windows çalışma kopyası. Yeni kariyerlerde Model 4, 2000/01 Türkiye ligi ve TR/EN. Eski Model 1–3, ekonomi modeli ve tarihsel katalog yerinde kaldı.

| Alan | Kaynak |
|---|---|
| Maç nesnesi, saha ve kurallar | mac.py, saha_motoru.py, futbol_kurallari.py, futbol_kalibrasyonu.py, konumsal.py |
| Taktik, duran top, 2D ve tema | arayuz.py, duran_top_ui.py, mac_gorunum.py, tema.py |
| Lig, fikstür, kariyer | yarisma.py, kariyer.py |
| Pazar, finans, iş piyasası | transfer.py, piyasa_ai.py, ekonomi.py, finans.py, is_piyasasi.py |
| Katalog, istatistik, kayıt | veritabani.py, istatistik.py, kayit.py |
| Windows başlatıcı ve paket | oyun.py, BASLAT.bat, PAKETLE.bat |

Kalibrasyon yeni alt sınıfta. Önceki saha motorunun kararları kullanılmaya devam ediyor. Yeni ofsayt ve kaleci kuralları sürüme bağlı. 2D çizim katmanındaki okunabilirlik değişiklikleri koordinat veya RNG yazmıyor.
