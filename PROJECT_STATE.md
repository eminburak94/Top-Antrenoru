# Top Antrenörü proje durumu

**Doğrulama tarihi:** 23 Kasım 2026 (Türkiye saati)  
**Sürüm:** v0.8.8, 8. tur Windows Beta adayı  
**Hedef:** Bağımsız Windows ve tester doğrulaması

| Alan | Doğrulanan durum |
|---|---|
| GitHub | [eminburak94/Top-Antrenoru](https://github.com/eminburak94/Top-Antrenoru) |
| Geliştirme dalı | develop/v088-match-balance |
| Temel HEAD | 6316fa332f46883f7dfae149c0e00f2a69c53595 |
| Ana çalışma klasörü | Bu deponun yerel kök dizini (.) |
| Main | 4317e9d567c281c11e7420d306e552f0d81313e1 |
| Çalışma ağacı | Aşama başında temiz, HEAD bilinen GitHub geliştirme ucu ile eşleşiyor. Bu manifest yeni izlenmeyen dosya. |
| Son Windows adayı | v0.8.8 TUR 8 TESTER BETA. EXE SHA-256 4A9885C71DE2E383BB159CB8B53CC0AFC01916BB333D24C982842F09055D3273. |

Aktif kod: başlatma ve arayüz oyun.py, arayuz.py, mac_gorunum.py, tema.py. Maç mac.py, saha_motoru.py, futbol_kurallari.py, futbol_kalibrasyonu.py. Kariyer ve kayıt kariyer.py, kayit.py, veritabani.py, yarisma.py. Transfer ve finans transfer.py, sozlesme.py, finans.py. test*.py ve testdata geliştirme doğrulamasına aittir. .build ve tester paketleri yerel çıktılardır. Eski sürümler, yedek_v dizinleri ve FM/CM tarihsel veri arşiv kökü korunur.

Son doğrulanmış sonuç: 13 hedefli ve 152 genel test geçti, dört koşullu uzun test atlandı. Fenerbahçe denemesi 34 hafta ve 306 maç tamamladı. Kaleci değişikliği, ihraç sonrası diziliş ve yeni sezon kaydı doğrulandı. Bu aşamada oyun testleri yeniden çalıştırılmadı. [Gerçek oynanış denetimi](V088_GERCEK_OYNANIS_DENETIMI.md) · [Windows aday raporu](V088_WINDOWS_BETA_ADAYI.md) · [Beta hazırlığı](V088_BETA_HAZIRLIK_RAPORU.md) · [Kayıt güvenliği](V088_KAYIT_GUVENLIGI.md) · [Uzun kariyer](V088_UZUN_KARIYER_TESTLERI.md) · [2D oynanabilirlik](V088_2D_OYNANABILIRLIK_RAPORU.md) · [Atlas devri](V088_ATLAS_DEVIR_RAPORU.md)

Açık riskler: bağımsız temiz Windows, fiziksel DPI ve insan tester sınaması bekliyor. Taç/faul sıklığı ve disiplin dengesi açık. Yeni geliştirme öncelikleri: ilk 30 dakika tester senaryosu, kış transferi ve sözleşme uzatma için farklı takım güçlerinde kısa kariyerler, ardından kaleci ve disiplin kalibrasyonu. [İlk 30 dakika](V088_BETA_ILK_30_DAKIKA.md)

## Korunan ikinci çalışma

Tarihsel arşiv kökü altındaki v088-work, HEAD 39f8e2788bdf7217af931b784e2a77e1be28a8e1. Git hazırlık alanında 20 düzenleme ve 2 ekleme bulunuyor. İzlenen dosya 197. Hazırlık alanı dışında değişiklik, silinmiş, izlenmeyen veya yok sayılan dosya bulunmadı.

Tam yedek Top-Antrenoru-v088-work-yedek_2026-11-23_162013 kapsayıcısındaki v088-work. Git dizini dahil 259 dosya ve 50 alt dizin. Dosya boyutu ve SHA-256 kaynak öncesi, kaynak sonrası ve yedek envanterinde eşleşti. Yedek HEAD, Git durumu ve hazırlık farkı da kaynakla aynı. Envanter, yedek kapsayıcısındaki SHA256_MANIFEST.json dosyasında.

### Dosya karşılaştırması

Tür, ikinci çalışmanın hazırlık alanındaki işlemdir. Ana sütunu, ana HEAD ile metin düzeyindeki ilişkiyi gösterir. Bu tablo karşılaştırmadır, aktarım yapılmadı.

| Dosya | Tür | Ana | Fark ve olası çakışma | Aktif oyun için gerekli | Sonraki işlem |
|---|---|---|---|---|---|
| BASLAT.bat | M | Var, farklı | Veri ve Tk denetimi, UTF-8, Python 3.12 tercihi. Ana genel Python başlatıcısını kullanıyor. | Kaynaktan başlatma | Veri/Tk denetimini bağımsız değerlendir. Python sürüm kısıtını test et. |
| PAKETLE.bat | M | Var, farklı | İkinci kopya v0.8.8 hedefi ekliyor. Ana ayrıca ayrı dağıtım ve çalışma yolu seçebiliyor. | EXE derleme | Ana sürümü koru. |
| arayuz.py | M | Var, farklı | v0.8.8 etiketi ve eski kayıt klasörü zaten ana kaynakta. Ana ayrıca yerleşim ve oyuncu değişikliği düzeltmelerini içeriyor. | Evet | Dosyayı değiştirme. |
| kayit.py | M | Var, aynı | v0.8.8 kayıt dizini ana kaynakta aynı. | Evet | Aktarım gerekmez. |
| tarihsel_test_kaynagi.py | A | Yok | TOP_ANTRENORU_TEST_ARCHIVE ile mutlak test arşivi yolu. Ana test_fixtures.py ile yakındaki arşivleri keşfediyor. | Hayır | Açık arşiv klasörü seçeneğinin faydasını mevcut yardımcı üzerinde değerlendir. |
| test_v060.py | M | Var, farklı | v0.5.5 katalog ve kayıt kontrolünü yardımcıya bağlar. Ana aynı katalog ayrımını başka yardımcıyla yapıyor. | Hayır | Ana kapsamı koru. |
| test_v070.py | M | Var, farklı | v0.6.0 kayıt ve katalog yolunu değiştirir. Ana güncel katalog testini arşivden ayırır. | Hayır | Yalnız ortak arşiv yolu seçeneği kabul edilirse uyarla. |
| test_v075.py | M | Var, farklı | v0.7.0 kaydı için farklı arşiv çözümleyici. | Hayır | Ana yardımcıyı koru. |
| test_v076.py | M | Var, farklı | v0.7.5 kariyer ve katalog testlerinde farklı yardımcı ve test adı. | Hayır | Kapsam örtüşüyor, ayrı aktarım gerekmez. |
| test_v078.py | M | Var, farklı | v0.7.7 kariyer kaydı için farklı dizin çözümü. | Hayır | Ana yardımcıyı koru. |
| test_v079.py | M | Var, farklı | v0.7.8 kaydı ve antrenman testinin arşiv yolu farklı. | Hayır | Ana yardımcıyı koru. |
| test_v0791.py | M | Var, farklı | v0.7.9 özellik referansının arşiv yolu farklı. | Hayır | Ana yardımcıyı koru. |
| test_v0792.py | M | Var, farklı | v0.7.9.1 motor karşılaştırmasının arşiv yolu farklı. | Hayır | Ana yardımcıyı koru. |
| test_v0793.py | M | Var, farklı | v0.7.9.1/.2 karşılaştırması ve güncel RNG ayrılmış. Ana benzer ayrımı farklı yardımcıyla yapıyor. | Hayır | Ana kapsamı koru. |
| test_v080.py | M | Var, farklı | v0.7.9.3 referans yolu farklı, ikinci kopyada güncel personel eşdeğerliği aynı yöntemde. | Hayır | Ana kaynakta ayrı güncel personel testini koru. |
| test_v081.py | M | Var, farklı | Dört tarihsel sürüm için farklı klasör keşfi. | Hayır | Ortak yardımcı kararı verilirse dört alt senaryoyu koru. |
| test_v082.py | M | Var, farklı | v0.8.1 ekonomi karşılaştırmasına açık arşiv yolu seçimi. | Hayır | Ana yardımcıyı koru. |
| test_v084.py | M | Var, farklı | v0.8.3 kayıt referansı için farklı dizin keşfi. | Hayır | Ana yardımcıyı koru. |
| test_v085.py | M | Var, farklı | v0.8.4 maç tekrarının arşiv yolu farklı. Ana test ayrıca Tk olay döngüsünü bekliyor. | Hayır | Ana oynatma kontrolünü koru. |
| test_v086.py | M | Var, farklı | v0.8.5 Model 1/2 tekrarının arşiv yolu farklı. | Hayır | Ana yardımcıyı koru. |
| test_v087.py | M | Var, farklı | Model 4 hızlı/2D testi ile v0.8.6 uyumluluğu ayrılmış. Ana da ayırıyor. | Hayır | Ana uyumluluk ve sentetik kayıt kapsamını koru. |
| test_v088_beta.py | A | Yok | Sentetik migrasyon, serbest transfer, otomatik kayıt, hasarlı kayıtta yedeğe dönüş ve eski klasör seçimi. Ana Beta ve kayıt testleriyle kısmen örtüşüyor. | Hayır | Yalnız özgün senaryoları daha sonra izole kopyada çalıştırıp gerekirse aktar. |

## Bağımsız denetim düzeni

Mevcut Top-Antrenoru-Denetim kopyasında 81 dosya var. Tamamı başlangıçtaki ana çalışma dosyalarıyla bayt düzeyinde eşleşir. 204 izlenen dosyanın 123'ü yoktur. Üç temel JSON, başlatıcılar, fixture ve raporlar dahil. Üretim commit’i belgelenmemiştir. Bu aşamada kopya yenilenmedi.

Onaylanacak sonraki aşamada her denetim, açık bir Git commit'inden yeni bir dizine çıkarılmalı. Meta veri depo URL'si, dal etiketi, tam commit, Türkiye saatli ISO 8601 oluşturulma tarihi, kapsam listesi, hariç tutulan alanlar ve her dosyanın SHA-256 özetini içermeli. Kapsam kaynak inceleme veya çalıştırılabilir test kopyası olarak belirtilmeli. Yeni kopya doğrulanmadan denetim referansı değiştirilmemeli. Önceki kopya ve arşivler korunmalı.

Claude, Qwen3 ve Atlas rapor başlığı: sürüm, amaç, depo, dal, tam commit, denetim kapsamı ve doğrulama tarihi. Hazırlık alanındaki değişikliklerden söz ediliyorsa bunların ayrı HEAD'i ve yedek manifesti belirtilmeli.