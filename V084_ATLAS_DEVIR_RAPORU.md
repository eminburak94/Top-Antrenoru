# Atlas devir raporu · Top Antrenörü v0.8.4

## Tamamlananlar

- Ayrı v0.8.4 proje ve paket dizini. 95 kaynak dosyanın başlangıç SHA-256 manifesti işlem sonunda tekrar eşleşti. v0.8.3 EXE özeti doğrulandı.
- Gruplu menü, işlevsel ana panel, içeriğe göre genişleyen kadro ve arama sütunları.
- Futbolcu ve personel arama merkezleri. Birleşik filtreler, kısa liste, ham değerlere göre sıralama, sayfalama, profil ve uygun teklif işlemleri.
- Kendi oyuncusunda kariyer, gelişim ve sözleşme akışları. Rakip oyuncuda yalnız kamuya açık alanlar ve gözlem aralıkları.
- Geniş 2D saha, olay/istatistik sekmeleri, kontrast top, pasör veya şutörün motorda top konumuyla eşleştiği karede ismi ve konturu, hız ve müdahale kontrolleri.

## Motor ve veri

mac.py, konumsal.py ve kariyer.py simülasyon akışı değiştirilmedi. Interpolasyon arayüzde çalışır ve RNG tüketmez. Maç ve ekonomi bayrakları korunur. 17 kariyer, 345 sezon ve 105.570 maçta 25 kontrol noktası v0.8.3 ile süre dışındaki bütün kaydedilen alanlarda eşleşti. Gözlem raporları yeni nitelik aralıkları ekler. Kısa listeler ve filtreler isteğe bağlı kayıt alanında saklanır. Önceki kariyerler kendi modelleriyle açılır.

## Dosya değişiklikleri

arayuz.py, arama_bilesenleri.py, ise_alim_ui.py, mac_gorunum.py, tema.py, personel.py, personel_ui.py, kayit.py, oyun.py, BASLAT.bat, PAKETLE.bat, gorsel_kontrol_v084.py, test_v060.py ve test_v084.py.

## Test ve görseller

102 otomatik senaryo geçti. İlk eski GUI testi 200/60 sayfalama beklentisinde, yeni filtre testi giriş seçicisinde başarısız oldu. İkisi de düzeltilip yeniden geçti. Açık başarısız veya atlanan test yok. 960×600, 1280×720 ve 1920×1080 geometrilerinde TR/EN test edildi.

V084_EKRANLAR altındaki 01_menajer, 02_kadro, 03_futbolcu_arama, 04_personel_arama, 05_futbolcu_profili, 06_personel_profili, 07_mac_merkezi ve 08_mac_sonrasi PNG dosyaları gerçek Tkinter pencerelerinden alındı. İlk sütun ve maç ekranı kırpılmaları görsel kontrolle düzeltildi.

## Windows

v0.8.4 TESTER BETA/Top Antrenoru dizininde Top Antrenoru.exe, eşlik eden _internal klasörü ve BENI_OKU.txt hazır. Yerel EXE açılış, arama, 2D ve kayıt testi tamamlandı. Genel Tester Beta onayı bekliyor.

## Açık işler ve v0.8.5

- Gerçek Windows DPI, farklı ekran ölçekleri, ayrı temiz Windows ve insan tester denemesi.
- 2D’de kesintisiz zaman çözümü, gerçek pas zinciri ve motor kaynaklı tam top sahipliği. Mevcut hareket beş dakikalık dönemlerin görsel açılımıdır.
- Dar pencere, çok uzun metin ve yüksek DPI için ek tablo görünümü. Süreli bellek testi.
- Eksik eski gözlem aralıkları geriye dönük tahminle doldurulmadı.

## Kullanıcı kararı

Genel beta dağıtımından önce bir temiz Windows ve insan tester oturumu belirlenmeli. Sonraki geliştirme önceliği için 2D oynatma ile transfer/personel iş akışının gerçek kullanım geri bildirimi karşılaştırılmalı.
