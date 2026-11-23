# Top Antrenörü v0.8.8 Windows Beta adayı

Paket yolu: C:\Users\pc\Desktop\top ant v0.8.7\v0.8.8 TESTER BETA\Top Antrenoru. Açılacak dosya Top Antrenoru.exe. Klasör, _internal ve BENI_OKU.txt birlikte dağıtılır.

- Paket: 31.310.886 bayt, 1.001 dosya.
- EXE: 3.121.727 bayt. SHA-256 389E34FEE7B3ED0287D49CA0C3F80EE94B8857FC5027BE9FDC964EA462FF1750.
- Gerekli data.json, tarihsel_girisler.json ve tarihsel_skorlar.json dosyalarının paket ve kaynak SHA-256 özetleri eşleşti. Uygulama 18 kulüp ve 619 oyuncu yükledi. Harici DAT arşivi yok.

## Windows doğrulaması

PyInstaller onedir paketinin gerçek EXE'si yerel Windows'ta sistem PATH'iyle, harici Python ve Tcl ortam değişkenleri kaldırılarak çalıştı. Ayrı açılışta v0.8.8 Tkinter ana penceresi görüldü ve normal Windows kapatma mesajıyla çıktı kodu 0 alındı.

Paket içindeki denetim geçici profilde gerçek Tkinter kontrolleriyle Fenerbahçe kariyeri açtı. Kadro ve duran toplar açıldı, diziliş 4-3-3 oldu, 27547 numaralı oyuncunun transferi tamamlandı. 2D Canvas 73 öğe çizdi. Hafta 2 ve dokuz maç sonucu doğrulandı. Yeni Tk oturumunda kaydedilen kariyer tekrar açıldı ve tam durum eşleşti. Dosya ve onay diyalogları otomasyon yanıtı aldı. Uygulama işlemleri gerçek kodla yapıldı. Ham kanıt .build/v088-package-probe.json.

v0.8.7 başlığı, varsayılan kayıt dizini ve paketleme hedefi yeni sürüme ayrıldı. v0.8.7 kayıt klasörü yükleme seçeneğinde korunuyor. Eski EXE özeti değişmedi. Paket ve geçici test profili Git'e gönderilmedi.

## Testler ve kalanlar

- Hedefli paket senaryosu, 2D ve kayıt grubu: 10 başarılı.
- Genel keşif, Tkinter koşulları etkin: 153 testten 149 başarılı, 4 koşullu uzun test atlandı, 0 hata.
- Yerel Beta adayı oluşturuldu ve doğrulandı. Bağımsız temiz Windows makinesi ve insan tester henüz sınanmadı. Genel Beta onayı verilmedi.
- Çoklu monitör ve gerçek sistem DPI doğrulaması açık. Taç ve faul sıklığına ilişkin önceki model sınırlamaları sürüyor.

Tester akışı V088_BETA_ILK_30_DAKIKA.md ve paket içindeki BENI_OKU.txt dosyasında.
