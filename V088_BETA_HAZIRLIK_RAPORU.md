# v0.8.8 Beta hazırlığı · Altıncı tur

## Temiz GitHub klonunda yeniden doğrulama

Bu ek doğrulama, GitHub'daki `701886a` geliştirme ucunu temel aldı. Dalda bulunan arayüz, kayıt ve oynanış düzeltmeleri korundu. Arşiv bağımlılığının nedeni, testlerin Git dışında tutulan `yedek_v*` dizinlerini ve geliştiriciye özgü komşu sürüm klasörlerini varsaymasıydı. 22 başlangıç hatasının dördü aynı testin sürüm alt senaryolarıydı.

Arşivsiz çalışmada tarihsel karşılaştırmalar sürüm adıyla açıkça raporlanıyor. Depodaki yedi sentetik v0.8.6/v0.8.7 kayıt örneği ve arşivsiz veri kontrolleri çalışmaya devam ediyor. Ayrı bir test, çalışma anında üretilen sürümsüz kayıt, şema 1 ve şema 2 örneklerini şema 3'e yükseltiyor ve bir hafta oynatıyor. Tam karşılaştırma için `TOP_ANTRENORU_TEST_ARCHIVE` mutlak yolu kullanılabiliyor. Açıkça yapılandırılmış fakat eksik bir arşivin test hatası verdiği doğrulandı. Beklenen dizinler [testdata/README.md](testdata/README.md) içinde. Yalnızca oyun kaynakları ve gerekli oyun JSON dosyaları kullanıldı.

### Windows kurulumu

- Windows 11 x64 build 26200, CPython 3.12.10 ve Tcl/Tk 8.6.15 ile doğrulandı. Kaynak oyunu ve regresyonu çalıştırmak için ek pip bağımlılığı gerekmiyor. Python kurulumunda Tcl/Tk bileşeni bulunmalı. [Python Windows kurulum belgeleri](https://docs.python.org/3.12/using/windows.html)
- Klondaki `data.json`, `tarihsel_girisler.json` ve `tarihsel_skorlar.json` dosyaları `oyun.py` yanında bulunmalı. `BASLAT.bat` bu dosyaları ve Tkinter'ı kontrol ediyor. Windows `py` başlatıcısı ve PATH üzerindeki `python` yolu ayrı ayrı çalıştırıldı. Eksik veri senaryosunda başlatıcı dosya adını bildirdi ve 1 koduyla çıktı.
- `python -m venv --without-pip <geçici-ortam>` ile kurulan, sıfır ek paketli ortamda `python -B -X utf8 oyun.py --check-package <geçici-sonuç.json>` geçti. Aynı kontrol `BASLAT.bat --check-package <geçici-sonuç.json>` ile de geçti.
- PyInstaller 6.22.3 ile `PAKETLE.bat` üzerinden yerel ve ayrı bir onedir EXE üretildi. EXE ve `_internal` birlikte tutulmalı. EXE, Python içermeyen PATH ve geçici kullanıcı profiliyle çalıştı. Paket içindeki üç JSON'un SHA-256 değerleri kaynak dosyalarla eşleşti. EXE SHA-256 değeri `0f4aee9c389bf12b5d046ee9f14791074d11a203f22cdbe5f8bd2dc2587e94d1`. Paket yerel test çıktısı olarak kaldı.

### Beta işlem zinciri

- Kaynak ve EXE kontrolleri İngilizce arayüzde Fenerbahçe Model 4 kariyeri açtı, 4-3-3'ü uyguladı, transferi tamamladı ve 2D maçı adımlayıp bitirdi. 73 Canvas öğesi, hafta 2, dokuz maç sonucu ve kapatıp açtıktan sonra aynı kayıt durumu doğrulandı.
- Genel regresyondaki tam sezon senaryosu 34 hafta ve 306 maç sonrası 2001 sezonuna geçti. Kaleci değişikliği, ihraç sonrası diziliş, kayıt/yeniden açma, yedek ve kesintili yazma, 2D oynatma ve TR/EN yerleşim kontrolleri de koşuldu. Dosya seçimi ve onay diyalogları otomasyonda sabitlendi. Oyun işlemleri gerçek kodla çalıştı.
- Test süreçleri için `LOCALAPPDATA` ve `USERPROFILE` geçici dizinlere yönlendirildi. Bellek içi veya geçici diskte üretilen kariyerler kullanıldı.

### Güncel regresyon ve Beta kararı

İki koşu aynı GitHub klonunda, Tkinter testleri açık ve kullanıcı profili yalıtılmış olarak yapıldı.

| Koşu | Keşfedilen | Geçen | Atlanan test / kayıt | Hata veya başarısızlık |
|---|---:|---:|---:|---:|
| Temiz klon, arşivsiz | 157 | 134 | 23 / 26 | 0 |
| Temiz klon, tam yerel kaynak arşiviyle | 157 | 153 | 4 / 4 | 0 |

Arşivsiz koşudaki 22 tarihsel atlama kaydı 19 test yöntemine karşılık geliyor. `test_v081.test_legacy_saves_continue_with_legacy_models` dört alt senaryo bildiriyor. Tam arşiv koşusunda aşağıdaki tarihsel kontrollerin tümü geçti.

- `test_v060` katalog karşılaştırması ve v0.5.5 kayıt açma, `test_v070` katalog karşılaştırması ve v0.6.0 kayıt açma, `test_v075` eski kayıt bonusu, `test_v076` katalog karşılaştırması ve v0.7.5 kariyer kaydı.
- `test_v078` eski kayıt ve simülasyon, `test_v079` aylık rapor ve canlı maç eşdeğerliği, `test_v0791` özellik değerleri, `test_v0792` eski motor, `test_v0793` iki eski maç modu ve `test_v080` personel öncesi eşdeğerlik.
- `test_v081` dört sürüm alt senaryosu, `test_v082` v0.8.1 ekonomi, `test_v084` v0.8.3 kayıt tercihleri, `test_v085` v0.8.4 tekrar, `test_v086` v0.8.5 Model 1/2 tekrar ve `test_v087` v0.8.6 eski model tekrarları.

Her iki koşuda `--long` gerektiren dört test atlandı. Bunlar `test_v060.test_ten_seasons`, `test_v070.test_twenty_five_seasons`, `test_v075.test_fifty_seasons` ve `test_v076.test_careers`. Model 4 tam sezon, 2D ve Beta arayüzü, sentetik ve güncel kayıt güvenliği, transfer ve menajerlik testleri iki koşuda da geçti.

Depo kökünden PowerShell ile aynı koşuyu yeniden üretmek için aşağıdaki komut kullanılabilir. Tam arşiv koşusundan önce `TOP_ANTRENORU_TEST_ARCHIVE` ayarlanır.

```powershell
@'
import os, sys, tempfile, unittest
with tempfile.TemporaryDirectory() as profile:
    os.environ.update(LOCALAPPDATA=profile, USERPROFILE=profile)
    sys.argv.append('--gui')
    suite = unittest.defaultTestLoader.discover('.')
    sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
'@ | python -B -X utf8 -
```

Otomatik testlerde kaynak veya yerel EXE için engelleyici hata görülmedi. Bağımsız, yeni kurulmuş bir Windows makinesinde kurulum ve insan tester oturumu dağıtım öncesi açık kalan kapılar. Bu denetim mevcut Windows makinesinde yeni, paketsiz Python ortamı ve yalıtılmış kullanıcı profiliyle yapıldı. Fiziksel DPI, çoklu monitör ve başka Windows sürümleri ayrıca doğrulanmadı. Önceki maç kalibrasyonu ve uzun kariyer dengesi riskleri bu turun kapsamı dışındaydı.

---

## Önceki doğrulama kayıtları

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

## GitHub'daki menajerlik güncellemesiyle son doğrulama

İlk gönderimde uzak geliştirme dalı 39f8e27 ile ilerlemişti. Bu commit geliştirme dalına birleştirildi. Birleşik kaynakta 11 hedefli test geçti. --gui ile 153 test keşfedildi. Temiz Git kaynak arşivinde 130 geçti, 26 atlama kaydı ve 0 hata. Tam tarihsel klasörlere sahip yerel kaynakta 149 geçti, 4 uzun test atlandı ve 0 hata. Atlamalar arasında ayrı sayılan tarihsel alt senaryolar bulunur. Son günlükler .build/v088-beta-merged-clean.log ve .build/v088-beta-merged-local.log. Main aynı commit'te tutuldu.
