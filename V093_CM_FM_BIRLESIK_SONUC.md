# Top Antrenörü v0.9.3 — CM/FM birleşik araştırma sonucu

**Araştırma durumu:** Yedi klasik oyun için kurulum veya belge incelemesi tamamlandı. Son çalışmanın kapsamı FM 2005, 2006, 2008 ve 2009. Dört oyun için yerel menü, yeni kariyer ve maç içi davranış doğrulanamadı. Oynanan maç sayısı her oyun için **0**. Top Antrenörü kaynak denetimi yerel `4c8c4fa` commit'ine, yayımlanan rapor dalı uzak `9bdea207` commit'ine dayanıyor.

## Raporlar

- [Kapsamlı CM/FM karşılaştırması ve 30 öneri](V093_CM_FM_KAPSAMLI_INCELEME.md)
- [FM 2005 ve FM 2006 ilk başlatma incelemesi](V093_FM2005_FM2006_UYGULAMALI_INCELEME.md)
- [Dört FM sürümünün sıralı incelemesi, ses tablosu ve 23 öneri](V093_FM2005_2006_2008_2009_DERIN_INCELEME.md)

## Kaynak oyuna göre doğrulanabilen sonuçlar

| Oyun | Doğrulama yöntemi ve bulgu | Top Antrenörü için etkisi |
|---|---|---|
| CM 01/02 | **Belge.** Eidos kılavuzunda diziliş, takım/bireysel talimatlar ve metinle maç akışı. | Kısa kadro→maç→rapor zinciri. `arayuz` ekranlarında geri dönüş ve klavye odağı. [Eidos kılavuzu](https://oldgamesdownload.com/manual/championship-manager-season-01-02-mac-windows-manual-english/) |
| CM4 | **Belge.** Eidos bilgi notunda gerçek zamanlı 2D ve canlı taktik müdahale. | `kariyer.LiveMatch` ve `mac_gorunum` üzerinde talimatın etkin olduğu dakika ve ilgili olay birlikte görünmeli. [Eidos bilgi notu](https://www.worthplaying.com/article/2003/2/10/news/8163-championship-manager-4-fact-sheet/) |
| FM 2005 | **Belge.** Stüdyo arşivinde geri/ileri gezinme, genişlik, tempo ve yaratıcı serbestlik. **Süreç gözlemi.** Başlıklı pencere açıldı. | Mevcut ayarların işe yaradığı konumu göster. Yeni ayardan önce bağlamlı gezinme ve pasın riskini açıklama. [SI FM 2005](https://www.sports-interactive.com/games/football-manager-2005) |
| FM 2006 | **Belge.** Antrenman görevi, fizyo raporu, devre arası konuşması ve yönetimle görüşme. **Süreç gözlemi.** Masaüstü kopyası başlıklı pencere oluşturdu. | `antrenman`, `oyuncu.prepare_player` ve `yasayan_kulup.review` kararlarının etkisini kendi ekranlarında göster. [SI FM 2006](https://www.sports-interactive.com/games/football-manager-2006) |
| FM 2007 | **Belge.** Önceki araştırmada SI gözlem ve bağlı kulüp demoları. Son uygulamalı kapsamın dışında. | `personel.finish_scouting` aralığını karar ekranına taşı. Bağlı kulüp için önce lig ve oyuncu akışı. [SI gözlem demosu](https://www.youtube.com/watch?v=9fMi04n9n84) · [SI bağlı kulüp demosu](https://www.youtube.com/watch?v=u952cZ7pfIQ) |
| FM 2008 | **Belge.** Transfer/kiralama merkezi, finans ve güven görünümü. **Süreç gözlemi.** Başlıklı pencere açıldı. | `finans.book_deal` ve `ekonomi.projection` ile teklifin maaş, nakit ve taksit etkisini aynı yerde göster. [SI FM 2008](https://www.sports-interactive.com/games/football-manager-2008) |
| FM 2009 | **Belge.** 2D/3D, zaman çizelgesi ve yardımcı raporu. **Süreç gözlemi.** Pencere ilk örnekten sonra oluştu. | `mac.detail` ile ortak olay zaman çizelgesi. Canlı/özet simülasyon eşdeğerliği. 3D'yi bağımsız karar olarak ele al. [SEGA FM 2009 kılavuzu](https://manualzz.com/doc/41576512/sega-football-manager-2009-user-manual) |
| FM 2005/06/08/09 | **Dosya yapısı.** Dördünde WAV tablosu ve gol, vuruş, direk, tribün, karar/bitiş düdüğü eşlemeleri. FM 2009'da daha ayrıntılı adlandırılmış hakem ve başlama olayları. Duyum sınanmadı. | `mac_gorunum` katmanında az sayıda özgün ses, gol doğrulandıktan sonra tepki, görsel tekrar ve hızlı maç için tekilleştirme. |

## Çelişkiler ve belirsizlikler

- **FM 2006 başlatma.** Program Files kopyası ilk incelemede `Access Denied` başlığını verdi. Sonraki sıralı incelemede Masaüstü kopyası `6.0.2f72973` oyun penceresi oluşturdu. İki farklı kurulum ölçüldü. İlk hatanın nedeni ve ikinci kopyanın ana menüsü açık.
- **Pencere ve oynanış.** Başlıklı pencere bir açılış gözlemi. Görünür menü, profil, CA/PA göstergesi, oynanan maç ve taktik etkisi için kanıt yok. Menüye erişim dört oyunda da doğrulanamadı.
- **Ses dosyası ve tetikleyici.** WAV adı, dosyanın yapıda bulunduğunu gösterir. CFG, tanımlı eşlemeyi gösterir. Varsayılan ayar, tetiklerin tüm koşulları ve yama önceliği çalıştırma sırasında ölçülmedi.
- **Top Antrenörü maç modeli.** Olaydan görüntü üreten eski modeller ile Model 4'ün simülasyon karesi farklıdır. Hızlı/2D aday eşdeğerliği Model 4 için değerlendirilmeli.

## Top Antrenörü ile teknik bağ

| Sistem | Kaynakta doğrulanan temel ve araştırma sonucu |
|---|---|
| Maç, rol ve rakip | `saha_motoru.PitchState.pass_ball`, `CalibratedPitch.shoot`, `mac.coach_step` ve `mac.detail` yerleşim, vuruş, rakip müdahalesi ve olay raporunu taşır. Önceki 24 eşleştirilmiş tohumlu örneklerde yüksek pres üç profilde kondisyonu yaklaşık sekiz puan düşürdü ve yüksek kazanımları artırdı. Uzun pasın şut etkisi profil bazında değişti. FM için eşdeğer oynanış ölçümü yok. |
| Gelişim ve sakatlık | `oyuncu.develop/prepare_player`, `antrenman` ve `kariyer.apply_match` dakika, yaş, hazırlık, yük ve toparlanmayı ilişkilendirmek için mevcut kancalar. Yaş/mevki dağılımı ve sakatlık sonrası geri dönüş ölçülmeli. |
| Transfer ve gözlem | `transfer`, `sozlesme`, `finans.book_deal` ve `personel.finish_scouting` teklif, sözleşme, maliyet ve gözlem belirsizliğini işliyor. Önceki iki 12 sezonluk kariyerde kiralama dışındaki 470 işlemin 400'ü bedelsizdi. Bu bir piyasa kalibrasyonu işareti, genel oran tahmini için küçük örneklem. |
| Lig, ekonomi ve haber | `yarisma.schedule`, `kariyer.complete_week`, `yasayan_kulup.review` ve `gundem.record` yerel sezonu, yönetim hedeflerini ve haberleri bağlıyor. 2000 dönem kuralları ve kaynaklı katılım tarihleri yeni liglerden önce doğrulanmalı. |

## Önerilen sıra

1. **v0.9.4 · Maç kararını görünür kıl.** Pas araya girme, topsuz destek ve arkada örtü için az sayıda ölçülebilir kural. Aynı olay kaynağından canlı saha işareti ve maç raporu. 10 kişi, rol uygunluğu ve hızlı/2D regresyonu sürüm kapısı.
2. **v0.9.5 · Pazarlık ve 2000 başlangıcı.** Teklifin gerçek mali taahhüdü, gözlem aralığı, bedelsiz piyasa dengesi ve tarihsel oyuncunun katılım kaynağı.
3. **v0.9.6 · Yönetim, kondisyon ve ses.** Sağlık/yük raporu, yönetim kararının bütçe ve hedef koşulu, sınırlı kariyer hafızası. Motor RNG'sini kullanmayan, ayarlanabilir özgün maç sesi.
4. **Sonraki · Uzun kariyer ve futbol dünyası.** Çok tohumlu 30–50 sezon, kayıt/performance bütçesi ve dönem kuralları geçildikten sonra hafif dış lig ve yıl bazlı Avrupa turnuvası.

Bir sonraki uygulamalı adımı engelleyen unsur, test oturumunda masaüstü aracının pencere, ekran ve giriş erişimi sağlayamaması. FM 2005 ana menü ve Yeni Oyun görüntüleri kullanıcı tarafından sağlanırsa o iki ekran değerlendirilebilir. Canlı taktik etkisi için tamamlanmış maç ve zaman damgalı sahne kanıtı gerekir. Bu koşuldan önce oynanışa ilişkin belge ve çıkarımlar, doğrudan gözlem sayılmaz.

**Kullanıcının açtığı pencereyle son deneme.** Windows, FM 2005'in tek süreçte ve yanıt veren başlıklı pencereyle açık olduğunu bildirdi. Computer Use, `HRESULT = 0x8007000F` nedeniyle ekran ve girdi aşamasına ulaşamadı. Alternatif aracın çekirdeği de pencere envanteri çıkarmadan kapandı. Kullanıcı tarafından açılan pencere, başlatmanın çalıştığına ek kanıt sağladı; ana menü veya maç davranışına yeni kanıt sağlamadı. Bu turda test kariyeri ve oynanan maç sayısı dört oyun için sıfır. FM 2006, 2008 ve 2009'a geçilmedi. [Erişim denemesi ve oyun bazında durum](V093_FM2005_2006_2008_2009_DERIN_INCELEME.md#10-kullanıcının-açtığı-fm-2005-penceresiyle-erişim-denemesi)
