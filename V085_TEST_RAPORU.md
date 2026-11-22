# Test raporu

Nihai keşif 110 senaryo buldu. 104 geçti, altı isteğe bağlı test varsayılan koşuda atlandı. Bu altı senaryo ayrı çalıştırılıp geçti. Toplam 110 farklı otomatik test, sıfır açık başarısız, sıfır açık atlama. Sekiz yeni senaryo konum, pas zinciri, top kaybı, şut, gol, kurtarış, altı yeniden başlama, kaleci alanı, pres/kondisyon, değişiklik, RNG, eski kayıt tekrar üretimi ve üç uygulama akışını kapsar.

Geliştirme sırasında menajer kartında metin kaçış hatası, sol bek İngilizce etiket seçicisi ve dar personel araç çubuğu nedeniyle test başarısızlıkları görüldü. Kaçış ve seçici düzeltildi, arama eylemleri iki satıra bölündü ve testler yeniden geçti. İlk kalibrasyonda kaleci saha ortasına taşabildi. Top sürme sınırı sonrası kalibrasyon ve 17 kariyer matrisi yeniden çalıştırıldı. Önceki dönemin GUI testlerindeki pencere başlığı, serbest oyuncu filtresi ve kısa liste seçme adımları yeni tasarıma göre güncellendi. Davranış beklentileri korundu.

Tkinter oynanış akışları gerçek pencerelerde otomasyonla tamamlandı. Maç hazırlığı, otomatik ilk 11, başlat/duraklat, pres, oyuncu değişikliği ve maç analizi; sol bek/yaş/maaş filtresi, gözlem isteği ve kabul edilen gerçek transfer; masadan antrenman kararı ve hafta ilerletme ayrı test edildi. Bunlar insan tester oturumu değildir.

Yerel Windows x64 EXE açıldı, 18 kulüp ve iki arama ekranı yükledi, model 2 konumsal kare üretti, dokuz maç işledi, yalıtılmış kariyeri yazıp yeniden açtı. BASLAT.bat da görünür olarak açıldı. Ayrı temiz Windows, uzun insan oynanışı ve fiziksel DPI sınaması yapılmadı.
