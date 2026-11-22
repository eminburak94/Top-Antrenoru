# v0.8.2 test raporu

Normal keşifte 87 senaryo bulundu. 81 geçti, 6 isteğe bağlı senaryo varsayılan koşuda atlandı. Başarısız kalan kısa test yok. Sekiz yeni senaryo dönem endeksleri, defter ve transfer dengesi, kaleci ihtiyacı, v0.8.1 haftasının birebir yeniden üretilmesi, kesintili dosya değişimi ve 960×600 iki dilde ekran ile kayıt akışını ölçer.

İlk kısa koşuda ayrı kopyada skor doğrulama CSV'si eksikti. Üç defter testi yeni ticari geliri hesaba katmadığı için mutabakat eşitliği başarısız oldu. Kaynak CSV yalıtılmış kopyaya alındı ve defter eşitliklerine ticari gelir kalemi eklendi. Eski açılış testi beklenen başlığını v0.8.2 olarak kullanır. Geçmiş sürüm dosyaları değişmedi. İlk Windows derlemesi data yolunda durdu. Mutlak girdi yolu ile paket üretildi.

Arayüz testleri otomatik Tkinter testidir. Yerel paket testi gerçek süreci başlattı ve pencereyi doğruladı. Temiz Windows makinesi, fiziksel güç kesintisi ve insan tester oturumu kapsam dışında kaldı.

Kaynak BASLAT.bat açılışları salt okunur v0.8.1 ve geliştirme v0.8.2 kopyalarında ayrı ayrı doğrulandı. v0.8.1 kopyasının 57 dosyası orijinalle yeniden SHA-256 eşleşti.

## İsteğe bağlı testlerin sonucu

- v0.6.0 Tkinter ve 10 sezon regresyonu geçti.
- v0.7.0 iş akışı ve 25 sezon regresyonu geçti.
- v0.7.5 üç 50 sezonluk kariyer testi geçti.
- v0.7.6 iki 50 ve bir 100 sezonluk kariyer, defter mutabakatı ve kayıt boyutu kontrolü geçti. CSV çıktıları geçici dizinde tutuldu.

Birleştirilmiş son sonuç 87 farklı otomatik test geçti, 0 başarısız, 0 atlandı. Ek ekonomi matrisi ve EXE kontrolleri bu test sayısına dahil değildir.
