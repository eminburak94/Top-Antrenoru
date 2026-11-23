# v0.8.8 Beta hazırlığı · Altıncı tur

## Temiz kopyadaki 22 hata

Tur başındaki 2c4c608 Git ağacından arşivsiz temiz kopya çıkarıldı. 138 test keşfedildi, 22 hata ve 6 koşullu atlama çıktı. Dört hata tek bir testin farklı sürüm alt senaryolarıydı. Hatalı çağrılar Git'te bulunmayan yedek_v dizinleri ve komşu eski sürüm klasörleri üzerinden veri okuyor veya Python çalıştırıyordu.

Yalnızca gerçekten bulunmayan arşiv dizinleri açıklayıcı biçimde atlanıyor. Dizin mevcutsa bozuk dosya, yanlış yol türü, subprocess hatası ve iddia hataları başarısızlık olarak kalır. Katalog, güncel maç eşdeğerliği ve personel kontrollerinin arşivsiz sınanabilen bölümleri ayrıca çalışır. Yerel tam arşiv kontrolleri korunur.

Depoya v0.8.6 (Model 1–3) ve v0.8.7 (Model 1–4) ile üretilen yedi sentetik şema 3 kaydı eklendi. Boyut 192.981 bayt. Fixture, depodaki oyun kataloğuyla oluşturulmuş kurgusal kariyerleri içerir. Eski EXE, harici CM/FM arşivi veya kişisel kariyer içermez. Her kayıt salt okunur açıldı, başka dosyaya yazıldı ve RNG'siyle paralel ilerletildi. Model ve kayıt şeması korundu. Fixture kökeni testdata/README.md içinde.

## Windows ve gerçek işlem zinciri

Kaynak oyun Windows'ta gerçek Tkinter ana penceresini açtı ve WM_CLOSE ile süreç kodu 0 döndü. Pencere mevcut v0.8.7 başlık metnini taşıyor. İngilizce ana menüde Fenerbahçe seçilerek Model 4 kariyeri açıldı. Kadro satır sayısı kulüp kadrosuyla eşleşti. Diziliş seçimi gerçek 4-3-3 durumunu güncelledi. Arama tablosundan oyuncu seçilip teklif penceresinin Gönder düğmesine basıldı ve oyuncunun kulüp kaydı değişti. 2D maç adımlandı ve tamamlandı. Hafta 2, dokuz lig sonucu ve kullanıcının karşılaşması doğrulandı. Kayıt diske yazıldı, pencere kapatıldı, yeni Tk oturumundan menü ile açıldı ve serileştirilmiş durum eşleşti. Dosya seçici ve onay iletişimleri otomasyon için sabit yanıt aldı. Maç, transfer ve kayıt işlemleri gerçek kodla tamamlandı.

960×600 TR/EN büyütülmüş Tk ölçeğinde Devam ve Haberler düğmelerinin kesildiği ölçüldü. Araç çubukları gerekli olduğunda birden fazla satıra açılıyor. Düzeltilmiş kontroller 960×600, 1280×720 ve 1920×1080 boyutlarında sınandı. Tk ölçek değişkeni üzerinden %125 ve %150 büyütme denendi. Windows sistem DPI'sı, çoklu monitör ve monitör arası geçiş ayrı doğrulanmadı.

## Beta kararı

- Düzelen engeller: Temiz kopyadaki arşiv kaynaklı genel test hataları ve dar/büyütülmüş arayüzde kritik kontrollerin kesilmesi.
- Kalan dağıtım kapısı: Bağımsız temiz Windows makinesi ve insan tester. Bu tur yerel kaynak doğrulamasıyla sınırlı kaldığından ayrı Windows EXE paketi üretilmedi. Önceki v0.8.7 paketi korundu.
- Sonraya bırakılabilir: Tam tarihsel kaynak olmadan birebir motor karşılaştırmaları, sistem DPI ve çoklu ekran, maç modelinde önceki turlardan kalan taç ve disiplin kalibrasyonu.

## Son testler

Hedefli kayıt ve arayüz koşusunda 10 test geçti. Son yerleşim düzeltmesi sonrası 7 Tkinter ve 2D testi de geçti. Son genel koşular Windows'ta --gui ile yürütüldü. Yerel kaynakta 147 test keşfedildi, 143 geçti, 4 koşullu uzun test atlandı. Yalnızca Git'te izlenen dosyalardan çıkarılan temiz kaynakta 147 test keşfedildi, 124 geçti, 0 hata çıktı. unittest 26 atlama kaydı bildirdi. Bu sayı, aynı testin dört ayrı sürüm alt senaryosunu ayrı sayar. Uzun kariyer bu turun konusu olmadığından son koşularda yeniden çalıştırılmadı.

İlk yerleşim denemesinden sonra dar pencere senaryosu genişletildi. Test ayrıştırmasında yanlış teste taşınan --long kapısı da düzeltilerek ölçümler nihai kaynakla tekrarlandı. Son günlükler .build/v088-beta-final-clean.log ve .build/v088-beta-final-local.log.
