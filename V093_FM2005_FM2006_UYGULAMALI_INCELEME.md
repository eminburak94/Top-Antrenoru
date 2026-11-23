# FM 2005 ve FM 2006 — Uygulamalı inceleme ve Top Antrenörü v0.9.3 karşılaştırması

**Dayanak** [V093_CM_FM_KAPSAMLI_INCELEME.md](V093_CM_FM_KAPSAMLI_INCELEME.md), Top Antrenörü `develop/v093-match-engine`, yerel kalite düzeltmesi `4c8c4fa`.

## Oyunların açılışı ve teknik sorunlar

| Oyun | Çalıştırılan dosya | Sonuç ve kanıt |
|---|---|---|
| FM 2005 | `C:/Users/pc/Desktop/Football Manager 2005/Football Manager 2005/fm2005.exe` | **Doğrudan gözlemlendi** — İlk sırada, kendi kurulum klasörü çalışma dizini olarak verilerek başlatıldı. Windows, çalışan sürece ait `Football Manager 2005` başlıklı bir ana pencere bildirdi. FM 2006 denemesi sırasında da süreç yanıt veriyordu. Açılış görseli, ana menü ve kariyer hazır durumu **incelenemedi**. |
| FM 2006 | `C:/Program Files (x86)/Sports Interactive/Football Manager 2006/fm.exe` | **Doğrudan gözlemlendi** — İkinci sırada, kendi kurulum klasöründen başlatıldı. Sürecin ilk ana pencere başlığı `Access Denied` idi. İletinin gövdesi ve kaynağı **incelenemedi**. Bu başlık tek başına Windows sürümü, uyumluluk, disk erişimi veya kopya koruması hakkında teşhis koymaya yetmez. Oynanabilir açılış doğrulanamadı. |

Windows pencere denetimi, ilk denemelerden ve yeniden başlatmadan sonra `CreateProcessSecurityEnvironment failed (HRESULT = 0x8007000F)` hatasıyla durdu. Bu, denetim aracının hatası. FM 2006'nın pencere başlığı ise oyun sürecine ait ayrı bir gözlem. Windows işlem bilgileriyle başlatma sonucu belgelendi; ekran içeriği, düğmeler veya oynanış bu yolla doğrulanamadı.

İki oyunda da yeni kariyer oluşturulmadı, kayıt açılmadı ve maç oynatılmadı. Güvenlik veya uyumluluk ayarı değiştirilmedi, ek yazılım yüklenmedi. Kurulum dosyalarına, Top Antrenörü kaynaklarına ve mevcut kayıtlara yazma işlemi yapılmadı.

## FM 2005 oynanış bulguları

- **Belgelerden doğrulandı** — Sports Interactive, tarayıcı tipi geri ve ileri gezinmeyi ve ekran bilgilerinin yeniden gruplanmasını FM 2005 özelliği olarak listeliyor. Top Antrenörü için tasarım karşılığı, haberden oyuncuya veya kulübe geçip filtreleri ve seçili satırı koruyarak dönmek. Yerel menünün düzeni ve gezinme hızı **incelenemedi**. [Sports Interactive FM 2005 arşivi](https://www.sports-interactive.com/games/football-manager-2005)
- **Belgelerden doğrulandı** — Stüdyo 51 lig ülkesinde 158 seviyeden ve 5.300'den fazla oynanabilir takımdan söz ediyor. Bu sayılar yayına ait stüdyo açıklaması. Yerel kurulumdaki lig seçim ekranı, veritabanı seçenekleri ve kurulum süresi **incelenemedi**. Top Antrenörü'nün tarihsel 2000 başlangıcı için yakın vadede daha değerli hedef, ilk kulüp seçiminde bütçe, hedef ve kadro gücünü erişilebilir kılmak. [Sports Interactive FM 2005 arşivi](https://www.sports-interactive.com/games/football-manager-2005)
- **Belgelerden doğrulandı** — Takım yaratıcılığına tanınan serbestlik, genişlik ve tempo için dereceli kontroller belgeleniyor. Yerel kadro yerleşimi, bireysel talimatların listesi ve taktik seçimin maçtaki etkisi **incelenemedi**. Top Antrenörü'nde genişlik ve tempo gibi seçimler Model 4 ile bağlantılı. Önce mevcut ayarın sahadaki sonucu açıklanmalı; yaratıcılık ayrı bir kontrol olacaksa pas riski ve serbest koşuyla ölçülebilir ilişkisi olmalı. [Sports Interactive FM 2005 arşivi](https://www.sports-interactive.com/games/football-manager-2005)
- **Belgelerden doğrulandı** — Stüdyo, menajerin basın üzerinden rakiplerine yönelik açıklama yapabildiğini ve bazı işlemlerin kullanıcı ilerlet komutu vermeden işlendiğini belirtiyor. Haber filtreleme, bekleme süresi ve basın yanıtlarının yerel sonuçları **incelenemedi**. [Sports Interactive FM 2005 arşivi](https://www.sports-interactive.com/games/football-manager-2005)

## FM 2006 oynanış bulguları

- **Belgelerden doğrulandı** — Sports Interactive, her sayfadan F1 ile bağlama uygun yardım ve daha kapsamlı oyun içi öğretici sunduğunu bildiriyor. Top Antrenörü için uygulanabilir karşılık, taktik ve transfer ekranında seçili kontrole ait kısa açıklama. FM 2006 yerel yardım penceresi **incelenemedi**. [Sports Interactive FM 2006 arşivi](https://www.sports-interactive.com/games/football-manager-2006)
- **Belgelerden doğrulandı** — Devre arası ve maç sonu takım konuşmaları ile maç hazırlığında başvurulabilen hakem profilleri belgeleniyor. Top Antrenörü canlı taktik, skor ve kondisyonu zaten işliyor. Takım konuşması eklenecekse etkisi kısa süreli ve duruma bağlı olmalı. Belirli bir yanıtın başarı garantisi verdiği ya da niteliklerini kalıcı değiştirdiği sonucuna varılamaz. [Sports Interactive FM 2006 arşivi](https://www.sports-interactive.com/games/football-manager-2006)
- **Belgelerden doğrulandı** — Bireysel antrenman programı, antrenör görevlendirmesi ve sağlık personeli raporu açıklanıyor. Top Antrenörü'nde antrenman, gelişim, kondisyon ve sakatlık kayıtları var. Bunları aynı kararda birleştirmek için oyuncu ekranında mevcut yük, dönüş durumu ve bir sonraki maçın zamanını birlikte göstermek yeterli bir başlangıç. [Sports Interactive FM 2006 arşivi](https://www.sports-interactive.com/games/football-manager-2006)
- **Belgelerden doğrulandı** — Yönetimden takım veya tesis yatırımı istemek ve artan beklentileri üstlenmek oyunun belgelenen kararlarından biri. Top Antrenörü'nde yönetim görüşmesi ve beklenti değerlendirmesi zaten var. Bir talebin karşılığında hedef veya maliyet değişiyorsa görüşme ekranında bunun nedeni görünmeli. Yerel FM 2006 yönetim ve taraftar ekranları **incelenemedi**. [Sports Interactive FM 2006 arşivi](https://www.sports-interactive.com/games/football-manager-2006)

## İki oyun arasındaki farklar ve inceleme kapsamı

Belgelerde FM 2005'in öne çıkan katkısı geniş kariyer seçimini ve taktik ayarlarını daha rahat gezinilen bir arayüzle sunması. FM 2006'nın katkısı maç, antrenman ve yönetim arasında daha fazla menajer kararı kurması. İki EXE'nin yerel ekran akışları, tıklama sayıları ve tepkileri kıyaslanamadı.

| İnceleme konusu | FM 2005 | FM 2006 |
|---|---|---|
| 1. Menü, yeni kariyer, menajer profili | **İncelenemedi** | **İncelenemedi** |
| 2. Kulüp, lig ve veritabanı | Ölçek **belgelerden doğrulandı**; seçim ekranı **incelenemedi** | Yerel seçim akışı ve katalog **incelenemedi** |
| 3. Kadro, diziliş ve roller | **İncelenemedi** | **İncelenemedi** |
| 4. Takım ve bireysel talimat | Üç takım ayarı **belgelerden doğrulandı**; bireysel kapsam **incelenemedi** | Talimat listesi ve etki **incelenemedi** |
| 5. Maç motoru, canlı 2D, müdahale | Maç oturumu **incelenemedi** | Takım konuşması **belgelerden doğrulandı**; oynatma ve müdahaleler **incelenemedi** |
| 6. Transfer, sözleşme, değer | Uçtan uca teklif **incelenemedi** | Uçtan uca teklif **incelenemedi** |
| 7. Antrenman, gelişim, sakatlık | Yerel akış ve etkiler **incelenemedi** | Program ve sağlık raporu **belgelerden doğrulandı**; uygulama **incelenemedi** |
| 8. Gözlemcilik ve personel | Yerel görev ataması **incelenemedi** | Teknik ekibe antrenman görevi **belgelerden doğrulandı**; gözlem görevi **incelenemedi** |
| 9. Yönetim, finans, taraftar | **İncelenemedi** | Yönetimle yatırım görüşmesi **belgelerden doğrulandı**; bütçe ve taraftar ekranı **incelenemedi** |
| 10. Haber, fikstür, istatistik, kariyer akışı | Geri/ileri ve basın etkileşimi **belgelerden doğrulandı**; maç ve hafta akışı **incelenemedi** | Bağlamsal yardım **belgelerden doğrulandı**; maç ve hafta akışı **incelenemedi** |

## Top Antrenörü v0.9.3'te mevcut sistemler

Önceki kaynak denetimi bu karşılaştırmanın Top Antrenörü tarafını sağlıyor. `arayuz.dashboard/tactics/live/report` ve `mac.LiveMatch` kadrodan canlı maça ve sonuca geçiyor. `mac.instruction/assign_role` ile takım talimatı ve oyuncu rolü maçta değişiyor, `saha_motoru` bunları simülasyonda kullanıyor, `mac_gorunum` Model 4 karelerini sunuyor. Rol uyumsuzluğu geri dönüşü ve maç içi planın sezonluk plandan ayrılması `4c8c4fa` denetim tabanına dahil.

`transfer`, `sozlesme` ve `finans` teklif, ücret, taahhüt ve sözleşme kararlarını işliyor. `antrenman`, `oyuncu` ve `kariyer` gelişim, yük ve sakatlığı birbirine bağlıyor. `personel.start_scout/finish_scouting` gözlem süresi ve belirsizlik sunuyor. `yasayan_kulup` yönetim güveni, taraftar, basın yanıtı ve görüşmeleri kapsıyor. Haber, fikstür ve sezon geçişi mevcut. Bu incelemede Top Antrenörü'nün yeni bir UI veya maç testi çalıştırılmadı. [Önceki v0.9.3 kaynak denetimi](V093_CM_FM_KAPSAMLI_INCELEME.md)

## Eksik veya geliştirilmesi gereken sistemler

- **Bağlamı koruyan gezinme.** Bir transfer haberinden oyuncu profiline geçildiğinde geri dönüşün önceki filtre, sıralama ve seçimi geri yüklemesi ölçülmeli. Ekran sayısını büyütmeden kariyer akışını iyileştirir.
- **Taktik kararının görünür sonucu.** Rapor, müdahale zamanı ile ilgili saha olayını birlikte göstermeli. Pres sonrası kazanılan top veya bek bindirmesi gibi bir olayın zamanını ve konumunu vermek, ek talimat katmanından önce gelir.
- **Antrenman ve sağlık kararının görünürlüğü.** `oyuncu.prepare_player`, `antrenman` ve `kariyer.apply_match` arasındaki mevcut bilgileri kadroya taşımak, maçtan önce yük ve rotasyon kararı almayı kolaylaştırır. Sakatlık durumunun tanısal kesinliğini aşan ifadeler kullanılmamalı.
- **Yönetim talebinin bedeli.** `yasayan_kulup.meeting/review` ile `ekonomi.projection` arasında sonuç görünümü. Harcama izni ile taahhüt edilen hedefin ayrı ayrı görünmesi, yönetim etkileşimini anlamlı kılar.

## Önceliklendirilmiş somut öneriler

| Öncelik | Değişiklik ve kod odağı | Kabul ölçütü |
|---|---|---|
| P0 | `mac.detail`, `arayuz.report`, `mac_gorunum` içinde mevcut taktik ve olay verilerini aynı zaman çizelgesinde göster | Bir canlı talimat zamanında görünür. Hızlı ve 2D skor/olay eşitliği korunur. Gözlenen olay, kesin nedensellik iddiası taşımaz. |
| P1 | `arayuz`, `arama_bilesenleri` ile haber → oyuncu → geri dönüşte liste durumunu koru | Arama, filtre, sıralama ve seçili satır korunur. Klavye odağı geri gelir. Kayıt değişikliği gerekmez. |
| P1 | `antrenman`, `oyuncu.prepare_player`, `kariyer.apply_match` üzerinden kadroda kısa kondisyon ve yük uyarısı | Yorgun veya sakatlıktan dönen oyuncuda uyarı, gerçek sakatlık/yük durumuyla güncellenir. Aynı bilgi TR ve EN görünür. |
| P1 | `yasayan_kulup.meeting/review`, `finans.commitments` üzerinden yönetim kararının koşulunu ve beklenen mali etkisini göster | Oyuncu talebi vermeden önce koşulu görür. Onay ve ret mevcut güven/bütçe mantığına dayanır. |
| P2 | `arayuz.live` üzerinden devre arası konuşması için küçük tasarım deneyi | Önce takım durumu, etki süresi ve iki farklı oyuncu tepkisi doğrulanır. Sırf arayüz seçeneği olarak eklenmez. |

Doğrudan oynanış kıyasını tamamlamak için eksik kanıt, her oyunda ana menüden başlayan yeni test kariyeri ve mümkünse bir hazırlık maçının üç evresidir. FM 2006 için ayrıca `Access Denied` penceresinin tam metni gerekir. Bu bilgiler elde edilene kadar ilgili ekran ve davranışlar **incelenemedi** olarak kalır.
