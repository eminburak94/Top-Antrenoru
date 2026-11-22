# v0.8.3 test raporu

Normal keşifte 96 senaryodan 90 geçti ve altı isteğe bağlı senaryo ayrı çalıştırıldı. İsteğe bağlı iki Tkinter testi, 10/25/50 sezon testleri ve v0.7.6'nın iki 50 ile bir 100 sezonluk defter regresyonu geçti. Birleştirilmiş sonuç 96 farklı otomatik test, sıfır başarısız, sıfır atlandı. Yeni v0.8.3 testleri dokuz senaryo.

Yeni testler üç maç modunun sonucu, aynı müdahalelerle kare eşitliği, RNG, saha sınırları, taktik etkisi, oyuncu değiştirme dakikası, sınırlı gündem, kayıt sonrasında eşdeğerlik, yaşa göre gelişim ve pazarlığı kapsar. Tkinter testinde 960×600 ana pencere ve 600 pikseli aşmayan maç penceresi iki dilde ölçüldü. Pres, hız seçimi, duraklatma ve bitirme denendi. Mevcut kadro, taktik, iş piyasası, transfer ve kayıt testleri korundu.

Ayrı ekonomi koşuları 345 sezon ve 105.570 lig maçı içerdi. Windows x64 PyInstaller testinde ayrı geçici kullanıcı dizini ve Python bulunmayan PATH kullanıldı. EXE 18 kulübü yükledi, bir 2D maç çekirdeğinde kare üretti, dokuz lig maçını işledi, kaydetti ve yeniden yükledi. Yerel geliştirme Windows'u kullanıldı. Bu sonuçlar insan tester veya temiz fiziksel Windows kurulumunu temsil etmez.

Nihai EXE SHA-256 1bc9a21d57f8d7cbd4c92c5a14ad3d94552bfad5f2638f370c1709feb9664aad
