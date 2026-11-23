# v0.8.8 gerçek oynanış denetimi · Sekizinci tur

## İncelenen kariyer

Fenerbahçe, tohum 888, Model 4. Yeni kariyer ve takım seçimi gerçek Tkinter ekranından yapıldı. Kadro satırları kulüp kadrosuyla eşleşti. Diziliş 4-3-3 olarak kaydedildi ve 11 oyunculuk elle seçilen kadro onaylandı. Teklif formundan 676.676 oyun baz birimli bedelli transfer tamamlandı. Alıcının kasa ve bütçesi bonservis ve imza ücretini yansıttı. Satıcının bonservis kaydı ve oyuncunun yeni sözleşmesi doğrulandı. Finans sayfasındaki kasa ve ödenen bonservis değerleri defterle eşleşti. Oyuncu sahipliği ile kadro indeksi her kontrol noktasında birebir eşleşti.

İzole sakatlık koşulunda kadro ekranı doğru sayıyı gösterdi ve oyuncu 2D maçta süre almadı. Maç hazırlığı doğru rakibi gösterdi. Oyuncu değişikliği gerçek maç olayına yazıldı. Bilet geliri ve maaş gideri maç haftasında güncellendi. Sonraki haftalar hızlı motorla oynandı. 34 haftanın 306 maçından bağımsız toplanan puan ve averaj, oyun kayıtları ve ekranla eşleşti. İzole bir sözleşme sonu koşulu gerçek sezon geçişinde işlendi. 2001/02 açılışı ve aktif sözleşmeler doğrulandı. Geçici kariyer diske kaydedildi, pencere kapatıldı ve yeni oturumda durum eşitliği doğrulandı.

## Doğrulanmış hatalar ve düzeltmeler

- Model 4'te kaleci varken saha oyuncusu kaleci yuvasına ve yedek kaleci saha yuvasına alınabiliyordu. Motor uygunsuz değişiklikleri reddediyor. Arayüz uygun yedekleri listeliyor.
- İhraç sonrası yedek kaleci, çıkan saha oyuncusunun rolünde kalıyordu. Yedek kaleci artık kaleyi devralıyor. Çıkan saha oyuncusunun yuvası kaybediliyor ve takım 10 kişi kalıyor.
- İhraç sonrası genel diziliş noktaları sıra tabanlı yerleşime dönebiliyordu. Model 4'te kalan oyuncuların diziliş noktaları korunuyor. İki kaleci hatası düzeltmeden önce testlerde yeniden üretildi.

## Testler ve paket

13 hedefli test geçti. Tkinter koşulları etkin genel keşifte 156 testten 152 geçti, 4 koşullu uzun kariyer testi atlandı, 0 hata. Önceki kayıt fixture'ları da çalıştı. Bir otomatik sezon yapıldı. Sakatlık ve sözleşme bitişi test girdileriydi. Kullanıcı kayıtlarına dokunulmadı.

Yeni ayrı paket C:\Users\pc\Desktop\top ant v0.8.7\v0.8.8 TUR 8 TESTER BETA\Top Antrenoru. 31.311.909 bayt, EXE SHA-256 4A9885C71DE2E383BB159CB8B53CC0AFC01916BB333D24C982842F09055D3273. İlk denemede PyInstaller spec dizinine göre çözülen veri yolları başarısız oldu. Ayrı hedef seçebilen mevcut toplu başlatıcı ve mutlak veri yollarıyla paket oluşturuldu. EXE yerel Windows'ta açıldı, kapandı, dokuz maçlık hafta, transfer ve kayıt/yükleme sınamasını geçti. Üç veri dosyasının özetleri ve eski iki paketin EXE özetleri doğrulandı. Ham kanıt .build/v088-turn8-proof.json. Paket Git dışında tutuldu.

Kalan riskler: Tek sezon ve bir tohum oyuncu davranışlarının tamamını kapsamaz. Taç/faul sıklığı ve disiplin dengesi önceki bulgularıyla açık. Bağımsız temiz Windows, fiziksel DPI ve insan tester doğrulaması yapılmadı.

## Sonraki geliştirme için üç öncelik

1. Bağımsız tester ile temiz Windows'ta ilk 30 dakikalık senaryoyu izlemek.
2. Farklı takım güçlerinde kış transferi ve sözleşme uzatma akışını ek kontrollü kariyerlerle sınamak.
3. Kalecisiz kalan takımlarda oyun kalitesi, taç/faul hacmi ve ikinci sarı oranını eşleştirilmiş maçlarla ölçmek.
