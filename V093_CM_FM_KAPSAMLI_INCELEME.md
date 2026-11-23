# Top Antrenörü v0.9.3 — CM/FM karşılaştırması ve geliştirme araştırması

## 1. Yönetici özeti

Denetim, `develop/v093-match-engine` dalındaki yerel `4c8c4fa86639d26b57ecd094bc3dc4ccb953c76c` kalite düzeltmesini temel alıyor. Bu commit, v0.9.3 maç motoru commit'i `9bdea207` üzerine geliyor. İncelenen oyun kodu ve kişisel kayıtlar üzerinde yazma işlemi yapılmadı.

- **Model 4, taktik seçimleri sahaya yansıtıyor.** Yüksek pres üç eşleşmede de yüksek bölgede daha çok top kazandırdı ve maç sonu kondisyonunu yaklaşık sekiz puan düşürdü. Uzun pasın şut getirisi ise kadroya ve dizilişe göre yön değiştirdi. Bu, üzerinde kalibrasyon yapılabilecek bir temel.
- **Sahadaki en büyük eksik, top çevresindeki seçeneklerin niteliği.** Bazı kararlar bir dakikalık adımda tek bir ağırlıklı tercih olarak çözülüyor. Koşu, rakibin pas kanalını kapatması ve pasın yolda kesilmesi arasındaki ilişkiyi güçlendirmek, yeni taktik düğmelerinden daha çok değer sunar.
- **Kariyer ekonomisi çalışıyor, piyasa çeşitliliği ölçülmeli.** İki 12 sezonluk denemede ölçülen 470 işlemin 400'ü bedelsizdi. Bu oran, özellikle serbest oyuncu erişimi ve kulüpler arası ücretli transfer değerlendirmesi için inceleme önceliği. İki kariyerden genel denge kararı çıkarmak erken.
- **2000 başlangıcının en önemli yatırımı veri kökeni ve tarih kilidi.** İlk sezon fikstürü ve sonuçları tam kapsanıyor. Ana oyuncu kataloğunda satır başına kaynak alanı yok, tarihli katılım kataloğu 13 kayıt içeriyor. Doğum, futbol dünyasına giriş ve tahmini yetenek ayrı anlamlar taşımalı.
- **Önerilen v0.9.4 odağı** pas kanalı ve topsuz destek, maç analizindeki kanıt ve genişletilmiş maç regresyonu. Büyük lig genişlemesi, yeni kayıt şeması ve 3D bu pakete dahil edilmemeli.

## 2. Yedi oyunun kurulum envanteri

`PF86` aşağıda `C:/Program Files (x86)` anlamına geliyor. Sürüm değerleri EXE'nin Windows dosya/ürün meta verisi. Sürüm etiketi boşsa kurulumun yama seviyesi açık bırakıldı.

| Oyun | Konum ve çalıştırıcı | Bilinen sürüm | Oyun açılmadan görülen izler |
|---|---|---|---|
| CM 01/02 | `PF86/Championship Manager 01-02`, `cm0102.exe` ve `cm0102_GDI.exe` | İki çalıştırıcıda da sürüm alanı boş | `Data`, `readme.txt`; Masaüstünde ayrı disk imajı görüldü |
| CM4 | `PF86/Eidos Interactive/CM4/cm4.exe` | Dosya ve ürün `4.0.0.0`; Enhancement Pack seviyesi belirsiz | `data`, `readme.rtf`; Masaüstünde ayrı disk imajı görüldü |
| FM 2005 | `PF86/Sports Interactive/Football Manager 2005` ve Masaüstü `Football Manager 2005/Football Manager 2005`, `fm2005.exe` | İki kopyada dosya meta verisi `1.0.0.0`; yama seviyesi belirsiz | Masaüstünde İngilizce readme, `db`, `config`, `tactics`, `preset_tactics`, grafik ve panel klasörleri |
| FM 2006 | `PF86/Sports Interactive/Football Manager 2006/fm.exe` | Dosya `6.0`, ürün `6.0.0f68542` | `db`, `help`, `tactics`, `preset_tactics`; Masaüstü kısayolu ayrıca görüldü |
| FM 2007 | Masaüstü `Football Manager 2007/Football Manager 2007/fm.exe` | Dosya `7.0.2`, ürün `7.0.2f94768` | `db`, `hints`, `tactics`; ayrı disk imajı görüldü |
| FM 2008 | Masaüstü `Football Manager 2008/fm.exe` | `8.0.2f117931` | Fransızca ve Felemenkçe kılavuz PDF adları, `db`, `league_sim`, `updates`, `facegen` |
| FM 2009 | Masaüstü `Football Manager 2009/fm.exe` ve `PF86/Sports Interactive/Football Manager 2009/fm.exe` | Sırasıyla `9.3.1f88284` ve `9.0.0f23544` | İngilizce readme iki kopyada da var; masaüstünde `db`, `league_sim`, `match events`, `updates`. Readme, 2D'nin bir görüntüleme seçeneği olduğunu destekliyor |

Masaüstünde görülen CM 03/04 ayrı bir oyun ve CM4 yamasına kanıt oluşturmuyor. Disk imajları bağlanmadı.

## 3. Kaynaklar, yöntem ve sınırlamalar

Kurulum taraması Masaüstü'ndeki oyun adlarına, iki Program Files köküne ve erişilebilen ek disklerin kökleri ile yaygın oyun klasörlerine odaklandı. Salt okunur dosya meta verisi, klasör yapısı ve seçilmiş kullanıcı belgeleri incelendi. Klasik oyunlar açılmadı. EXE/DLL sökümü, koruma atlatma, paket/veritabanı çıkarma ve varlık kopyalama yapılmadı.

Klasik oyunlarda **belgelenmiş** bir özellik, yayıncı kılavuzu/bilgi notu veya geliştirici açıklamasında geçiyor. **Yerel doğrulama** yalnızca kurulum meta verisi ve erişilen belgeleri kapsıyor. **Belirsiz** özellikte sürüme özgü ekran davranışı, hesaplama kuralı veya erişilebilirlik teyit edilmedi. Açıklanan özelliklerin puanlama formülleri, yapay zekâ karar ağırlıkları ve çalışma hızı karşılaştırmaya dahil edilmedi. Kılavuzlar ve görüşmeler, yayımlandıkları sitelerdeki geliştirici/yayıncı materyali olarak kullanıldı.

Top Antrenörü kanıtı üç düzeyde ele alındı. **Doğrulandı** kaynak akışı veya koşulan senaryo ile destekleniyor. **Kısmi** temel mekanizma var, tarif edilen kapsamın bir bölümü eksik. **Eksik** ilgili akışta uygulanmış karşılık bulunmadı. **İncelenemedi** manuel davranış ya da genelleme için veri yetersiz. Kontrollü maçlarda eşleştirilmiş 24 tohum ve üç kadro/diziliş kullanıldı. İki sentetik kariyerde yeni dünyalar bellekte kuruldu ve kayıt kodlayıcısı/çözücüsü 1, 6 ve 12. sezonlarda çağrıldı. Ölçümler araştırma senaryosuna ait. Kişisel kayıt, saatlerce açık kalan Tk penceresi, temiz Windows kurulumu ve başka bilgisayarlar üzerinde ölçüm yapılmadı. Arşiv test günlükleri yeni test koşusu olarak sayılmadı.

## 4. Top Antrenörü mevcut sistem denetimi

| Sistem ve durum | Kaynak / giriş noktası | Doğrulanan davranış, açık ve teknik risk |
|---|---|---|
| Tarihsel veritabanı · Kısmi | `veritabani/`, `tarihsel.load_entries/reconcile`, `oyuncu.age_at` | 606 temel oyuncu ve 324 ilk sahiplik. 306 açılış fikstürü ve 306 tarihsel sonuç. 13 tarihli katılım kaydı. Temel 606 satırda doğrudan `source` alanı yok. Normalleştirilmiş isim + doğum tarihi eşlemesi işe yarıyor; kaynak saklama ve kimlik çakışması denetimi genişlemeyi sınırlıyor. |
| Yetenek, mevki, potansiyel · Kısmi | `oyuncu.state/attributes/power`, `mevkiler.fit_level` | Potansiyel ve özellikler tekrarlanabilir, mevkiye göre ayrışıyor. Temel yetenek ve özelliklerin ortak türetimi farklı oyuncu tiplerini birbirine yaklaştırabilir. Tarihsel gerçek ile özellik tahmini ayrımı gerek. |
| Kadrolar ve dizilişler · Doğrulandı | `mac.select_slots`, `kadro_atama.assign`, `yarisma.formation_for/style_for` | Altı diziliş düzeni, otomatik ve elle yerleşim. Kırmızı kart sonrası görev devrinde çıkmış oyuncunun konumu korunabiliyor. Gelecekte yeni diziliş eklemek rol ve duran top regresyonu gerektirir. |
| Taktik ve roller · Doğrulandı | `mac.instruction/assign_role`, `CalibratedPitch.role/slot_fit`, `duran_top_ui.tactical_plan_page` | Geçersiz rol için mevkiye uygun geri dönüş, aynı dakikadaki talimatların son değeri ve sezon planından ayrı maç durumu. Roller arası destek ve boşluk kapatma adımları sınırlı. |
| 2D motor · Doğrulandı | `saha_motoru.PitchState.tick`, `CalibratedPitch.shoot`, `mac_gorunum.Pitch.draw` | Model 4'te görselleştirme simülasyon karelerini kullanıyor. Eski modellerin olaylardan görsel üretme yolu ayrı. Karelerle taşınan semantik sınırlı; yavaş oynatmada makul hareket ile gerçek kararın sınırı açık olmalı. |
| Maç içi müdahaleler · Doğrulandı | `mac.LiveMatch`, `mac.instruction/assign_role/substitute_side`, `arayuz.live/report` | Taktik ve değişiklik oturuma uygulanıyor; maç kaydı sırasında hafta ve RNG koruması var. Analiz kısa bir değişiklik öncesi/sonrası penceresi veriyor, rakip değişimini ve oyun durumunu ayrıca okumak gerekiyor. |
| Rakip hoca · Kısmi | `mac.coach_step/replace_tired_player`, `yarisma.formation_for/style_for` | 45. dakikadan itibaren beşer dakikada skor ve yorgunluk eşikleri. Kalıcı bireysel teknik adam tercihi ve gözlenen kanalı hedefleyen karşı hamle bulunmadı. Sık tepki eklemek talimat salınımı yaratabilir. |
| Transfer/sözleşme · Doğrulandı | `transfer.purchase_offer/answer_offer/deal/loan_deal/return_loans`, `sozlesme.player_objection/renew/expire`, `piyasa_ai.assess/recruit` | Teklif, karşılık, kiralama, yenileme ve sözleşme sonu var. Kiralamada ücret paylaşımı destekleniyor, opsiyon/geri çağırma sınırlı. Simülasyonda bedelsiz payı yüksek. |
| Finans · Kısmi | `finans.book_deal/pay_due_transfers/payroll/service`, `ekonomi.projection/can_commit`, `donem.index`, `para` | Maaş, bonservis, taksit, nakit ve taahhütler hesapta. Dönem katsayısı ve para gösterimi var. Kulüp bazında ekonomik şokların, yeniden yapılanmanın ve piyasa etkilerinin derinliği sınırlı. |
| Antrenman/gelişim · Kısmi | `antrenman.apply_plan/record_month`, `oyuncu.prepare_player/develop`, `dunya.age_world` | Antrenman, oynama, performans, yaş, personel ve altyapı girdi. İki sentetik sezon dizisi bireysel gelişim eğrilerinin geniş dağılımını kanıtlamıyor. |
| Sakatlık/kondisyon · Kısmi | `kariyer.apply_match`, `oyuncu.prepare_player/develop`, `saha_motoru` | Maç yükü, kondisyon ve sakatlık süreleri kariyere bağlanıyor. Bir önceki sakatlığın yeniden sakatlanma riskine etkisi ve karar ekranında belirsizlik daha sınırlı. |
| Gözlemcilik · Doğrulandı | `personel.start_scout/finish_scouting`, `ise_alim_ui` | Gözlemci başına aktif iş, iki haftalık rapor, yetenek/potansiyelde aralık ve gözlemci etkisi. Tam bilginin başka ekranlardan sızmasını ölçen arayüz denetimi gerekli. |
| Yönetim ve taraftar · Doğrulandı | `yasayan_kulup.review/update_support/transfer/press_answer/meeting`, `menajer.evaluate`, `is_piyasasi.weekly` | Hedef, sonuç ve finans güveni etkiliyor. Basın yanıtı, görüşme ve iş piyasası kariyere bağlı. Taraftarın uzun hafızası ve derbilerin kapsamı sınırlı. |
| Haberler/dünya · Kısmi | `gundem.record`, `yasayan_kulup`, `piyasa_ai` | Sınırlı gelen kutusu, basın ve transfer haberleri. Çok sezonlu dönüm noktası dizini ve yeni rekabetlerin oluşması için sürdürülebilir bir olay hafızası yok. |
| Lig ve turnuva · Kısmi | `yarisma.schedule`, `kariyer`, `tarihsel` | 2000 açılışı ve sonraki 34 haftalık iç lig döngüsü. Denetlenen akışta tam çok lig, Avrupa ve milli takım takvimi bulunmadı. Kural sürümleri takvimle birlikte tasarlanmalı. |
| Sezon geçişi · Doğrulandı | `dunya.age_world`, `altyapi.replenish`, `yarisma.schedule`, `kariyer` | Yaşlanma, yeni oyuncu ve sezon döngüsü. İki 12 sezonluk kariyer tamamlandı. 30–50 sezonluk güncel davranış, kuyruk riskleri ve gelir dağılımı yeniden ölçülmeli. |
| Kayıt/uyumluluk · Doğrulandı | `kayit.migrate/validate/validate_world/validate_match_options/decode/save_game/atomic_write` | Şema 3, eski model ayarı, değer doğrulama, atomik yazma ve yedek davranışı. Dinamik dünya ekleri, eksik alan ve eski kayıt için varsayılan ister. |
| Türkçe ve İngilizce · Kısmi | `arayuz.dashboard/tactics/live/report`, `arama_bilesenleri`, `tema` | Yanaşık ekran akışları ve mevcut dil desteği kaynakta görüldü. Pencere boyutu, Türkçe arama karakterleri, odak ve bütün metinlerin kapsaması bu denetimde ekran üzerinden sınanmadı. |
| Performans ve oynanabilirlik · Kısmi | `mac.LiveMatch`, `saha_motoru.PitchState.tick`, `mac_gorunum.Pitch.draw`, `kariyer.complete_week` | Kare toplama ve tüketim ayrılmış. İki kariyerde haftalık ve bellek ölçümü var. Tk ana döngüsü, uzun oturum ve geniş oyuncu havuzu için henüz etkileşim ölçümü yok. |

## 5. CM/FM karşılaştırma matrisi

Zorluk, performans ve kayıt riski düşük/orta/yüksek olarak ayrı değerlendirilmiştir. Güven, belgelenen özelliğe ilişkindir. Her satırdaki maliyet Top Antrenörü önerisi içindir.

| Oyun ve belgelenmiş özellik | Top Antrenörü karşılığı ve oyuncu etkisi | Öneri | Zorluk / performans / kayıt | Kanıt ve güven |
|---|---|---|---|---|
| CM 01/02 · Diziliş ve takım/oyuncu talimatları; kılavuz ayrıca metinle maç ve menajerlik ekranlarını tarif ediyor | `duran_top_ui` ve Model 4 hızlı/2D yolları var. Sık yapılan kadro, haber ve sonraki maç işlemlerinin hızını manuel olarak karşılaştırmadık | Aynı kariyer özetinden kadro, maç ve geri dönüş. Belirgin klavye kısayolları | Düşük / düşük / düşük | Yüksek, [Eidos CM 01/02 kılavuzu](https://oldgamesdownload.com/manual/championship-manager-season-01-02-mac-windows-manual-english/) |
| CM4 · Gerçek zamanlı 2D ve maç sürerken taktik müdahale | `LiveMatch` ve `mac_gorunum` temel eşdeğerliği sağlar. Kararın görsel izi kaybolursa oyuncu müdahaleyi değerlendiremez | Aynı olaydan saha vurgusu ve yorum. Duraklatınca seçim yapılan oyuncuyu bağlamda tut | Orta / düşük / düşük | Yüksek, [Eidos CM4 bilgi notu](https://www.worthplaying.com/article/2003/2/10/news/8163-championship-manager-4-fact-sheet/) |
| FM05 · Geliştirici 2D motor ile transfer ve antrenman üzerindeki çalışmayı açıklıyor | `transfer`, `antrenman` ve 2D var. Yönetim ekranları arası oyuncu rolü, mevcut yük ve transfer ihtiyacı birlikte okunamıyor | Kadro ihtiyacı ve gözlem raporunu seçili rol bağlamında birlikte sun | Orta / düşük / düşük | Orta, [Miles Jacobson söyleşisi](https://www.gamer.no/artikler/intervju-med-si-games-om-football-manager-2005/7897) |
| FM06 · Devre arası konuşmaları, mutsuz oyuncular, menajer sözleşmeleri ve antrenman değişiklikleri duyuruldu | `sozlesme.player_objection`, moral ve iş piyasası kısmi karşılık. Oyuncu beklentisinin hangi davranışla değiştiği daha az görünür | Beklenti nedeni, kısa süre ve gerçekleşme kaydı. Devre arası seçeneği ancak etkisi kalibre edilirse | Orta / düşük / orta | Orta, [Sports Interactive geliştirici söyleşisi](https://www.gamespot.com/articles/football-manager-2006-qanda/1100-6124092/) |
| FM07 · Gözlem sistemi ve bağlı kulüp ilişkisi geliştirici tarafından gösterildi | `personel.finish_scouting` belirsizlik ve süre verir. Bağlı kulübün düzenli gelişim hattı için karşılık bulunmadı | Önce raporların zamanla güncellenmesi ve arama filtreleri. Bağlı kulübü lig altyapısına bağımlı tut | Orta / düşük / orta | Yüksek, [SI gözlem demosu](https://www.youtube.com/watch?v=9fMi04n9n84), [SI bağlı kulüp demosu](https://www.youtube.com/watch?v=u952cZ7pfIQ) |
| FM08 · Transfer merkezi, maaş/transfer bütçesi ayarı, taraftar ve yönetim güveni | `finans`, `transfer`, `yasayan_kulup` merkezi mantığı sağlar. Oyuncu bir teklifin uzun vadeli nakit ve güven etkisini ayrı yerlerde izler | Anlaşma ekranında ödeme ufku ve onay gerekçesi. Yeniden tahsis ancak yönetim politikasıyla | Orta / düşük / orta | Yüksek, [Sports Interactive FM08 arşivi](https://www.sports-interactive.com/games/football-manager-2008) |
| FM09 · 2D/3D, maç zaman çizelgesi, yardımcı yorumları, basın görüşmeleri ve tercih edilen hareketler | `arayuz.report/live`, `yasayan_kulup.press_answer` ve taktik roller kısmi karşılık. Maç incelemesine dakika ve durum üzerinden geri dönmek güç | Özet olay zaman çizelgesi, gözlenen taktik örüntü ve açıklanabilir uyarılar | Orta / orta / düşük, kalıcı tekrar kaydı seçilirse yüksek | Yüksek, [SEGA FM09 kullanıcı kılavuzu](https://manualzz.com/doc/41576512/sega-football-manager-2009-user-manual) |

Klasiklerin rol ve oyuncu kişiliği formülleri, transfer yapay zekâsının ayrıntıları, gerçek zamanlı eşdeğerliği ve 30 sezon performansı incelenemedi. İleride ekran karşılaştırması istenirse en yararlı üç örnek CM 01/02'de kadrodan maça geçiş, CM4'te canlı talimat sonrası maç görünümü ve FM08'de teklife bağlı bütçe ekranı olur.

## 6. En önemli 30 eksik veya zayıf özellik

Fayda ve tarih katkısında 5 en yüksek değerdir. Maliyet ve riskte 5 en ağır yükü gösterir. P0 bir sonraki sürümün ölçüm ve güvenlik kapısı, P1 yakın dönem, P2 bağımlılıkları tamamlandıktan sonra, P3 düşük öncelik. Öncelik puanların aritmetik toplamına indirgenmedi.

| # | Durum ve uygulanabilir iyileştirme | Kod odağı | Fayda | Tarih | Maliyet | Risk | Öncelik |
|---:|---|---|---:|---:|---:|---:|---|
| 01 | Pas boyunca rakibin kanala erişimini ölç | `saha_motoru.PitchState.pass_ball`, `CalibratedPitch.pass_miss` | 5 | 3 | 3 | 4 | P0 |
| 02 | Baskı altında güvenli ikinci seçeneği ve kararsız topu üret | `saha_motoru.PitchState.tick/pass_ball` | 5 | 3 | 3 | 4 | P0 |
| 03 | Bek çıkınca komşu oyuncunun desteğini ve arkada kalan güvenliği modelle | `CalibratedPitch.target_adjust`, `PitchState.shape` | 5 | 4 | 3 | 4 | P0 |
| 04 | Şut, baskı ve top kaybını aynı olaylardan açıklayan maç raporu | `mac.detail`, `arayuz.report` | 5 | 2 | 2 | 2 | P0 |
| 05 | Model 4 için olay muhasebesi ve eşleştirilmiş hızlı/2D regresyonu | `mac.LiveMatch`, `mac_gorunum`, `saha_motoru` | 5 | 1 | 2 | 2 | P0 |
| 06 | Kırmızı kart, yeniden yerleşim ve kaleci senaryolarını genişlet | `mac.substitute_side`, `futbol_kurallari` | 4 | 2 | 2 | 2 | P0 |
| 07 | İlk kadrolarda satır başı kaynak ve tahmin ayrımı | `veritabani/`, `tarihsel.reconcile` | 5 | 5 | 3 | 2 | P1 |
| 08 | Gelecekteki tarihsel futbolcular için kanıtlı yaş/tarih kilidi | `tarihsel.load_entries`, `oyuncu.age_at`, `dunya` | 5 | 5 | 3 | 4 | P1 |
| 09 | Bedelsiz–ücretli piyasa dağılımını ve ücret yükünü kalibre et | `piyasa_ai.recruit`, `transfer.deal`, `finans` | 5 | 5 | 3 | 4 | P1 |
| 10 | Döneme ve yarışmaya göre kayıt/yabancı kurallarını tanımla | `yarisma`, `transfer`, `kayit` | 5 | 5 | 4 | 4 | P1 |
| 11 | Gelecek 12 haftalık maaş ve taksit görünümü | `finans.commitments/pay_due_transfers`, `ekonomi.projection` | 5 | 4 | 2 | 2 | P1 |
| 12 | Gözlem raporunda aralık ve güveni arama/karşılaştırmaya taşı | `personel.finish_scouting`, `ise_alim_ui` | 4 | 4 | 2 | 2 | P1 |
| 13 | Şampiyonluk, rekor ve tarihi transferlerin sınırlı olay hafızası | `gundem.record`, `yasayan_kulup`, `kayit` | 5 | 5 | 3 | 3 | P1 |
| 14 | Rakip hocalara istikrarlı risk profili ve hamle aralığı | `mac.coach_step`, `yarisma.formation_for/style_for` | 5 | 3 | 3 | 3 | P1 |
| 15 | Oynama beklentisi ve transfer isteğini gözlenebilir gerekçeye bağla | `sozlesme.player_objection`, `kariyer.apply_match` | 5 | 4 | 3 | 3 | P1 |
| 16 | Sakatlık dönüşünde yük ve yeniden sakatlanma takibi | `oyuncu.prepare_player`, `kariyer.apply_match` | 4 | 3 | 3 | 3 | P1 |
| 17 | Gelişim eğrilerinde mevki ve yaşa göre dağılım denetimi | `oyuncu.develop/attributes`, `antrenman`, `dunya.age_world` | 4 | 4 | 3 | 3 | P1 |
| 18 | Kariyer ve maç için birincil klavye yolları ile odak dönüşü | `arayuz`, `arama_bilesenleri` | 4 | 2 | 2 | 1 | P1 |
| 19 | Çok tohumlu 30–50 sezon sağlığı ve kayıt büyüme sınırı | `kariyer.complete_week`, `kayit`, `altyapi` | 5 | 4 | 3 | 3 | P1 |
| 20 | Alternatif tarih haberlerinde olay kaynağı ve kronoloji | `gundem.record`, `yasayan_kulup`, `tarihsel` | 5 | 5 | 3 | 3 | P1 |
| 21 | Kadro arama ve yan yana kıyası rol, yaş, ücret ile destekle | `arayuz`, `ise_alim_ui`, `mevkiler.fit_level` | 4 | 3 | 3 | 2 | P2 |
| 22 | Sınırlı açık oyun markajı ve duran top eşleşme sonrası yerleşimi | `CalibratedPitch.target_adjust`, `futbol_kurallari.prepare_layout` | 4 | 4 | 4 | 4 | P2 |
| 23 | Kalecide çıkış, yer tutma ve dağıtım kararını ayır | `CalibratedPitch.shoot`, `PitchState.tick` | 4 | 3 | 4 | 4 | P2 |
| 24 | Kulüp itibarını sonuçlar ve kaynaklarla zaman içinde güncelle | `yasayan_kulup.review`, `piyasa_ai.assess`, `finans` | 4 | 5 | 3 | 4 | P2 |
| 25 | Kademeli ikinci lig ve ligler arası oyuncu hareketi | `yarisma.schedule`, `dunya`, `transfer`, `kayit` | 5 | 5 | 5 | 5 | P2 |
| 26 | Yıl sürümlü Avrupa katılımı ve turnuva formatı | `yarisma`, `kariyer.complete_week`, `finans` | 5 | 5 | 5 | 5 | P2 |
| 27 | Ekonomik şok ve mali toparlanmayı kontrollü uygula | `finans.service`, `ekonomi.projection`, `donem.index` | 4 | 5 | 4 | 4 | P2 |
| 28 | Mentorluk ve liderliği kısa süreli somut etkilere bağla | `antrenman.apply_plan`, `oyuncu.develop`, `kariyer` | 3 | 3 | 3 | 3 | P3 |
| 29 | Uluslararası maç takviminden başlayan milli takım modeli | `yarisma`, `kariyer`, `dunya` | 3 | 4 | 5 | 4 | P3 |
| 30 | Belgelendirilmiş rekabetlerden ve simülasyon olaylarından dinamik rakiplik | `yasayan_kulup.update_support`, `gundem`, `yarisma` | 4 | 5 | 4 | 4 | P3 |

## 7. Maç motoru ve taktik sistemi

### 7.1 Kararların bugünkü karşılığı ve iyileştirme noktası

| Konu | Model 4 bugün | Ölçüm veya öneri |
|---|---|---|
| Takım/oyuncu talimatları | `mac.instruction/assign_role` ile canlı seçenekler. `CalibratedPitch.role/slot_fit` uyumsuz tercihte emniyetli rol seçer. | Önce-sonra durumunu olayla bağla. Aynı dakikada son talimat, maçtan çıkış ve varsayılan plana dönüş için test. |
| Rol etkileşimi, topsuz koşu, bindirme | `target_adjust` hat, genişlik ve role göre hedef konumu değiştiriyor. Bek rolü sahadaki ortalama x konumuna yansıyor. | Mevcut kare modeline bir destek koşusu ve bir örtü görevi ekle. Bek çıkarken ters bek veya ön liberonun konumunu ve kayıp sonrası açık koridoru ölç. |
| Pres ve pres kırma | `press_recovery` ve baskı, yeniden kazanım ve kondisyonu etkiliyor. | Birden çok baskıya rağmen ilk dokunuşuyla çıkan oyuncuya yakın şut değil, önce boş pas kanalı ver. Eşleştirilmiş testte yüksek presin getirisini, yükünü ve arkasında bıraktığı alanı birlikte izle. |
| Savunma çizgisi | Canlı ileri/geri çizgi komutu aynı maçın konumlarını değiştiriyor. `futbol_kurallari.before_delivery` teslimat öncesi ofsayt kontrol ediyor. | Rakip hızlı forvetli/forvetsiz, pasöre baskılı/baskısız dört durum. Arkaya koşu, ofsayt ve kaleciyle karşı karşıya kalma oranlarını birlikte izle. |
| Alan ve adam markajı | `futbol_kurallari.prepare_layout` duran top yerleşimini destekliyor. Açık oyun şekli ve yakın baskı mevcut. | Açık oyunda takip devri, bir adam takibi ve kalan zonun örtülmesi kısmi prototip. İki savunmacının aynı oyuncuyu izlerken boş yere ayrılması ölçülsün. |
| Pas kanalları | `PitchState.pass_ball` adayları ağırlıklı değerlendiriyor. Mesafe, teknik ve baskı hesaba giriyor. | Hat üzerindeki tahmini kesiciye göre seçenek puanı. `pass_miss` sonrası en yakın savunmacının temiz kazanım oranını ve aynı alıcının tekrar seçilmesini ölç. İkisi koddan gelen hipotez; bu çalışmada sıklıkları ölçülmedi. |
| Geçiş ve kontra | Gerçek top kazanımı sonrası yaklaşık üç adımlık geçiş durumu var. | Kazanılan bölge, rakibin top arkasındaki oyuncuları ve ilk iki karar ile kontra tanımı. Sırf pas uzadı diye kontra sayma. |
| Kanat ve merkez | Genişlik ve yön tercihleri konumları, servis profilini ve pası değiştiriyor. | 5-3-2 ile 4-3-3'e aynı genişlik talimatını verip kullanılabilir geniş opsiyon sayısını denetle. Kanat ile ceza alanındaki hedef oyuncu arasındaki bağı ölç. |
| Duran top | Yakın/uzak/merkez/kısa seçenekler, vuran oyuncu ve hava topu vekil ölçüsü var. | İlk temastan sonra seken top, ikinci şut ve ofsayt/avantaj sırasını aynı olaylardan doğrula. Duran top gollerini açık oyundan ayır. |
| Kaleci | `CalibratedPitch.shoot` engellenen şut, hedef, kurtarış ve sekme akışına sahip; kaleci becerisi, açı ve baskı giriyor. | Çıkış ve dağıtımın kararlı kuralı sonraki paket. Önce aktif kalecinin değişim/kırmızı kart selepas doğru kişi olduğunu doğrula. |
| Yorgunluk, sakatlık ve özellikler | Kondisyon, güç ve şut kararına bağlanıyor; pas, hava topu ve kaleci farklı özellikleri kullanıyor. | Kondisyonu skorla tek başına doğrulama. Baskıda karar kaybını, sprint/geri dönüşü ve gecikmeli sakatlık yükünü ayrı ölç. |
| Rakip karşı hamle | `mac.coach_step` skor/zaman/yorgunluk eşiklerine tepki veriyor. | Önce görülen tehlikeyi 10–15 dakikalık örnekle toplasın. Hamle aralığı ve gerekçesi olsun. Kalıcı hoca kimliği ayrı paket. |
| İstatistik ve 2D | `mac.detail` olaylardan şut ve olasılık bağlamı topluyor; `mac_gorunum` Model 4 karelerini tüketiyor. | Olay sırası, oyuncu/top sahipliği ve restart kareleri için veri eşitliği. Ara kareler, izlenebilirlik için kullanılsın; karar anı ve top yönü değişmesin. |

### 7.2 Sabit tohumlu ölçümler

Sayılar eşleştirilmiş 24 maç başına ortalamadır. Ok, aynı profilde düşükten yükseğe veya tabloda yazılı ilk tercihten ikinciye geçişi gösterir. Örnekler dengeyi dar bir çerçevede ölçüyor. Rakip simülasyonunun tepki vermesi sonuçlara dahil.

| Deney | Profil 1 · Galatasaray ağırlıklı eşleşme | Profil 2 · Trabzonspor–Beşiktaş, 4-3-3 | Profil 3 · Erzurumspor–Gaziantepspor, 5-3-2 |
|---|---|---|---|
| Düşük → yüksek pres | Yüksek kazanım 0,79→1,58; kondisyon 88,34→80,24; şut 5,71→8,25 | Kazanım 1,58→3,88; kondisyon 86,45→78,33; şut 3,62→6,46 | Kazanım 0,75→1,12; kondisyon 84,67→76,58; şut 1,29→3,29 |
| Dar → geniş | Geniş bölge ölçümü 8,07→38,76; şut 4,83→7,21 | Geniş bölge ölçümü 3,58→42,32; şut 4,75→5,62 | Geniş bölge ölçümü 0,59→4,51; şut 2,38→2,25; yenilen gol 1,96→2,17 |
| Kısa → uzun pas | Pas mesafesi 14,69→37,54 m; başarısız pas 15,84→23,23; şut 6,25→3,04 | Mesafe 18,06→31,17 m; şut 4,83→5,42; yenilen gol 0,88→0,58 | Mesafe 14,67→34,25 m; başarısız pas 27,02→32,75; şut 2,67→1,79 |
| Savunmacı bek → hücumcu bek | Bek konumu 22,53→32,44; şut 6,75→6,54 | Bek konumu 22,85→30,93; yenilen gol 0,71→0,75 | Bek konumu 21,52→29,84; yenilen gol 1,92→2,04 |

İlk profilde canlı çizgi değişiminde ortalama hat konumu 20,05'ten 33,93'e çıktı. İlk kondisyon 100'den 62'ye indirildiğinde maç sonu kondisyonu 84,28'den 46,26'ya, şut 6,54'ten 5,54'e indi. Gol ortalaması 1,54 ile 1,58 arasında kaldı. Bu örnekte gol sinyali daha gürültülü. Güçlü–zayıf ayrı karşılaşmada baskın taraf 2,96 gol atıp 0,33 gol yedi.

Yüksek pres üç profilde de şutu artırdı. Gelecek test, geç gol yeme, maç sonu geri koşu ve sonraki hafta tazeliğini de dahil etmeli. Aksi hâlde yüksek presin uzun vadeli maliyeti kullanıcıya az hissedilebilir. Bir dakikalık karar adımı, pası ve desteği oynanabilir bir maliyetle sınırlıyor. Çok sayıda küçük zaman adımı eklemeden önce bir pozisyon içinde pas, kesme ve ikinci top aşamalarını tutarlı hâle getirmek daha düşük riskli.

### 7.3 Regresyon seti

- Her maçta isabetli şut ≤ toplam şut. Gol, ofsaytla iptal, penaltı, kendi kalesine ve sekme olayları tanımına göre ayrı terkiple uzlaşmalı.
- Top sahibi sahada aktif olmalı ya da top boşta olmalı. Uzaklaştırılan oyuncu sonraki karede topa dokunmamalı. Değişiklikten sonra doğru kaleci ve savunma slotları çözülmeli.
- Aynı tohum, kadro ve talimat sırasıyla hızlı ve 2D Model 4 skor, olaylar, son kariyer etkisi ve RNG'de eşleşmeli. Hızlı/2D şartı kare toplama ve görüntü oynatma için sonuçları ayrıştırmamalı.
- Maç içi müdahale sadece oturum durumuna yazılmalı. Maç sonrası sezon planı, rol eşleşmeleri ve varsayılan çizgi aynı kalmalı.
- İki büyük takım, denk orta sıra ve biri eksik zayıf takım. Ev/deplasman çevrimi, düşük/yüksek kondisyon ve skor koruma eklensin. Ortalama yanında medyan ve kuyruklar yayımlansın.
- Oyuncuya bir gözlem örneği `60–70. dakikada rakibin solundan üç giriş`. Talimat, rakip değişiklik, kart ve skor bilgisi aynı zaman şeridinde yer almalı. Karşı-olgusal hesap olmadan şut artışını bir taktikte kesin nedensellik olarak etiketleme.

## 8. Oyuncu gelişimi, insan davranışı ve transfer

| Davranış | Mevcut karşılık ve uygulanabilir kapsam |
|---|---|
| Profesyonellik ve hırs | `oyuncu.state/develop` içinde varsayılan eğilim ve gelişim girdileri var. Gerçek kişilere kaynaksız karakter hükmü atamadan, sınırlı profil varyansı ve gelişim etkisi. Hırsı birinci takım hedefi ve rekabet arzusuna bağla. |
| İstikrar ve büyük maç | Form ve moral zaten performansa bağlanıyor. İstikrarı tek maçlık varyansla ölç, yüksek ve düşük becerinin ortalamasını ezmesin. Büyük maç etkisini ilk etapta mevcut moral ve skor baskısıyla karşıla; ayrı sabit etiket düşük öncelik. |
| Disiplin ve baskı altında karar | Oyun kuralları kart üretiyor; özellik temelli baskı karşılığı kısmi. Disiplini yorgunluk ve gecikmiş müdahaleyle, karar kalitesini algılanabilir pas seçenekleriyle ilişkilendir. Aynı özelliği iki kez cezalandırma. |
| Sadakat, dakika ve transfer isteği | `sozlesme.player_objection/renew` karar vermeye yarayan mevcut kanca. Sözleşme rolü, yakın dönem dakika ve kulüp itibarı birlikte düşünülsün. Düşük dakika önce görüşme, sürerse yenileme isteksizliği veya transfer talebi. |
| Moral ve özgüven | `oyuncu.power` mevcut moral, kondisyon ve formu birleştiriyor. Anlık özgüven ile kalıcı kulüp memnuniyetini ayrı zaman pencerelerinde özetle; üst üste aynı form etkisini yükleme. |
| Takım arkadaşı/teknik direktör ilişkisi | Tam ilişki ağı için mevcut ölçeğe göre maliyet yüksek. Birlikte oynama ve verilen sözlerin yerine getirilmesi kademeli başlangıç. Tüm oyuncu çiftleri için kalıcı matris düşük öncelik. |
| Liderlik ve mentorluk | Kaptan veya kıdemli oyuncunun birkaç gençle süreli grubu. Etkin antrenmana ve tutuma küçük etki; doğrudan potansiyel puanı aktarma yok. Önce yaş eğrisi ve gözlem güveni. |
| Sakatlık geçmişi ve yaş | `kariyer.apply_match`, `oyuncu.prepare_player/develop`, `dunya.age_world` tabanı sağlar. Sakattan dönüşte seans yükü ve dokunun toparlanması için sınırlı geçmiş. Hız, güç ve teknik için farklı yaş eğrisi. |

**Piyasa.** `piyasa_ai.assess/recruit/borrow_cover` kadro ihtiyacıyla piyasa arasında, `sozlesme` ise kulüp ve oyuncu kararları arasında mevcut sınır. Bu sınırı koruyup önce işlemleri serbest, sözleşme bitişi, ücretli ve kiralık olarak ayrı raporlayın. Genç, kısa sözleşmeli, ilk 11 oyuncusu ve yüksek maaşlı yedek için farklı gerçekleşme olasılığı ölçün. Yapay zekâ için kalan maaş, beklenen dakika, alternatif oyuncu ve nakit taksit farkını tek teklifte değerlendirip tekrar teklif sınırı koyun.

**On iki sezonluk araştırma ölçümü.** Galatasaray (9321) 37 ücretli, 198 bedelsiz; Erzurumspor (9322) 33 ücretli, 202 bedelsiz işlem verdi. Ölçülen ücretli+bedelsiz havuzda toplam bedelsiz payı %85,1. Kiralama bu payın paydasına dahil edilmedi. En küçük haftalık kadro gözlemleri 16 ve 17. Negatif nakitli takım haftası gözlenmedi. Ortalama maç golü 2,123 ve 2,185. Sonuçlar iflas veya denge garantisi vermez. Takımların bağlayıcı ödemeler nedeniyle tekliften vazgeçme oranı, taksit temerrüdü ve kulüp tipi kırılımı ayrıca ölçülmeli.

**Ekonomi ve gelişimi aynı ekranda bağlama.** Oyuncu karşılaştırması mevcut maaş ile sözleşme sonunu, yeni transfer önerisi işlem türü ile gelecek 12 haftanın maliyetini göstermeli. Gözlem aralığı bir üst sınır tahmini olarak sunulmalı; menajer zamanla oyuncuyu izleyebilmeli. Uzun vadede yaş, mevki ve kulüp tipine göre doğan oyuncu sayısı, dakika dağılımı ve yetenek yüzdelikleri kaydedilirse altyapının lig kalitesini tek tipleştirip tipleştirmediği görülebilir.

## 9. Yaşayan futbol dünyası ve alternatif tarih

`yarisma.schedule` 2000 başlangıcını sabit gerçeklerden kuruyor, `dunya.age_world` ve `altyapi.replenish` sonraki akışı üretiyor. Başlangıç kaynağı ve simülasyon sonucu ekran dilinde ayrı görünmeli. Tarihsel fikstür, oynanan alternatif sezonun skorlarını tayin etmemeli. Her tarihsel oyuncu kimliğinde doğum ve kariyere giriş için ayrı kanıt alanı, erişim tarihi ve tahmini özellik etiketi olmalı. Doğum tarihi bilinip katılım tarihi belirsizse onu güvenilir tarihe kadar dışarıda tutmak veya açık bir editoryal inceleme kuyruğunda göstermek uygun. Yerleşik yaş eşiğine dayalı geri dönüş kuralı, bir futbolcunun tarihsel debut'unu doğrulayamaz. Kurgusal altyapı oyuncuları ayrı kimlik kaynağıyla ve kaynak işaretiyle gelmeli. [TFF 2000–01 lig arşivi](https://www.tff.org/default.aspx?pageID=781)

**Kural paketi.** V0.9.3'teki yabancı limitinin 99'a varan pratik serbestliği dönem doğruluğu sağlamıyor. Kesin tarihli TFF talimatı bulunmadan belirli sayı girilmemeli. Kural bileşenleri tescil dönemi, maç kadrosu ve sahadaki sınır gibi farklı seviyelere ayrılmalı. UEFA'nın 2000/01 aşamalarında ikinci grup evresi bulunuyordu; 2003/04 değişikliği ikinci grubu eleme turuna dönüştürdü. Yıl tablosu bu farkı temsil etmeli ve kulübün o oyunda kazandığı katılım hakkına uygulanmalı. [UEFA 2000/01 arşivi](https://www.uefa.com/uefachampionsleague/history/seasons/2000/clubs/) · [UEFA format değişikliği](https://www.uefa.com/uefachampionsleague/news/025a-0eab034a2393-c36661944dab-1000--new-format-for-champions-league/)

| Dönem | Tasarım hedefi | Veri ve oynanış sınırı |
|---|---|---|
| 2000 | Kaynaklı başlangıç kadrosu, doğru yaş, yerel basın ve ölçülü nominal bütçe. 4-4-2, 3/5'li yerleşim ve oyun tarzlarını kulüp kimliğiyle sun. | Gerçek kulüp gelir/maaş verisi yoksa aralık veya model varsayımı. Modern ekonomik ölçüleri doğrudan döneme taşıma. |
| 2005 | Doğrulanan tescil/kupa kuralı değişiklikleri, yeni profesyoneller, daha geniş gözlem erişimi. | Gerçek oyuncunun gelişimi ve transferi oyunun koşullarına bağlı. Gerçek turnuva formatı ile alternatif kazananlar birlikte mümkün. |
| 2010 | Analizin yaygınlaşması, bütçesi olan kulüplerin daha geniş pazar taraması, antrenör stillerinin gelişmesi. | Kulüp için gelir, personel, itibar eşikleri; küresel zorunlu taktik değişimi uygulama. |
| 2020 | Gelir farkı, daha pahalı üst pazar ve daha hızlı haber akışı varsa doğrulanmış altyapıyla yansıt. | Gerçek olaylardan otomatik sonuç üretme. Tarihi olaylar kapalı ve açık senaryo politikasıyla açıkça etiketlenmeli. |
| 2030 | Oyuncunun kariyerinden türeyen itibar ve rekabet, kuşak değişimi, bölgesel ekonomi farkları. | Gelecek yıllar sentetik aralık ve senaryo. Kurgusal haberi gerçek tarihsel kayıt gibi gösterme. |

**Ölçekleme.** Kullanıcının ligi tam Model 4 ile çalışmaya devam edebilir. Diğer liglerde önce yalnızca takvim, kulüp bütçeleri, kadro derinliği, özet maç ve transfer aktörleri gerekir. Uzak ligleri haftalık veya tur bazında toplu hesapla; oyuncu transfer alanına girince kaydı ayrıntılandır. Bir lig aktif edildiğinde geçmiş puan, sahiplik ve RNG kimliği korunmalı. `is_piyasasi.weekly` ile hoca boşlukları, `piyasa_ai` ile değişen teknik tercih ve güç dengesi kurulabilir. Milli takım ve Avrupa takvimi aynı sakatlık/maç yükü akışına bağlanmalı. Kapasite doğrulanmadan iki sistemi birden açma.

**Rekabet ve hafıza.** `yasayan_kulup` üç İstanbul kulübü arasındaki ilişkiye başlangıç sağlıyor. Yeni rekabet için tekrar eden şampiyonluk yarışı, kupa eşleşmeleri veya kritik transfer gibi olayların birkaç sezon birikmesi gerekir. Gündem kutusunu olay arşivi olarak büyütmek yerine `gundem.record` üzerinden yılda ve kulüp başına sınırlı sayıda dönüm noktası sakla. Eski haber yeni sezonda yıl ve rakiple geri çağrıldığında kullanıcının kendi kariyerini hatırlamasını sağlar.

## 10. Arayüz ve oynanış

CM 01/02 kılavuzunun kısayol ve ana ekran odaklı akışı ile FM08–09'un karar anında ayrıntı veren ekranları iyi karşılaştırma çiftidir. Sürümlerin tepki süresi ve tıklama sayısı ölçülmedi. Top Antrenörü'nde `arayuz.dashboard` günün sonraki eylemini, `arayuz.tactics/live/report` maç zincirini ve `arama_bilesenleri` aramayı taşıyor. Yeni ekran yerine bu zincirin içinde ayrıntı açmak gerekir. [CM 01/02 kılavuzu](https://oldgamesdownload.com/manual/championship-manager-season-01-02-mac-windows-manual-english/) · [FM08 stüdyo özeti](https://www.sports-interactive.com/games/football-manager-2008) · [FM09 kılavuzu](https://manualzz.com/doc/41576512/sega-football-manager-2009-user-manual)

| Görev | Oyuncunun göreceği tasarım | Doğrulama |
|---|---|---|
| Haftayı ilerletme ve gelen kutusu | Sonraki maç, zorunlu cevap ve bütçe engelini tek kariyer özetinde göster. Haber seçildiğinde bağlı oyuncu/kulübe git ve aynı listeye dön. | Klavyeyle aç, işle, dön. Filtre ve seçili satır korunsun. |
| Oyuncu karşılaştırma ve transfer arama | Kullanılabilir mevki, iki/üç temel rol uygulaması, yaş, gözlem aralığı, maaş ve sözleşme sonu. Kiralık ve bedelsiz filtreleri. | Türkçe İ/ı ve İngilizce arama, isim benzerliği, filtre korunması ve kapsam dışı sonuç. |
| Kadro ve taktik | Seçili oyuncu, uygunluk nedeni ve otomatik rol seçimini net göster. Canlı maçta uygulanma dakikası ve maç planı etiketi. | A→B→A rol düzenleme, uyumsuz mevki, kırmızı kart, son talimat, pencere kapama. |
| Maç ve analiz | Maç hızı, duraklatma, önemli olay listesi, seçili olayın saha noktası ve rapor. Rakip hamlesi aynı zaman çizelgesinde. | 2D ve hızlı rapor eşitliği, sıkıştırılmış pencere, klavye/fare, düşük hızda olay sırası. |
| Öğrenilebilirlik ve bilgi yoğunluğu | İlk görünümde sonuç ve gerekçe; ayrıntıda dağılım, taahhüt ve rol etkisi. Tam rapor isteğe bağlı. | Yeni kullanıcı temel görevleri yardım almadan bitirebilsin. Her iki dilde taşan etiket ve açık odak testi. |

## 11. Teknik mimari ve performans riskleri

**Bağımlılıklar.** `arayuz` kullanıcı eylemlerini kariyer ve maç giriş noktalarına yönlendiriyor. `mac` maç kadrosu, taktik, kurallar ve saha çözümü arasında; `saha_motoru` ile `futbol_kurallari` konum ve karar katmanlarında çalışıyor. `kariyer.complete_week` maç, maaş, transfer, itibar, antrenman ve takvimi bir araya getiriyor. `kayit` ortak dünya verisinin sınırı. Yeni taktik önce `saha_motoru` içinde küçük karar fonksiyonuyla, raporlama ise `mac.detail` olay alanıyla sınırlandırılmalı. UI'ye simülasyon kararı taşıma. Yeni kalıcı alanın eski kayıt uyumluluğu ve varsayılanı ayrı karar.

**Ölçülen taban.** Kare yakalama kapalı iki kısa 24 maç koşusu yaklaşık 0,325 ve 0,352 saniye sürdü. Bu değer ekran çizimini içermez. İki 12 sezonluk kariyer yaklaşık 44,7 ve 44,2 saniyede tamamlandı. Örnek başına haftalık p95 sırasıyla 148 ms ve 131 ms. Ölçülen süreç tepe belleği yaklaşık 53,5 ve 54,6 MiB. Kodlanmış kayıt ilk sezonda yaklaşık 0,36 MB, 6. sezonda 0,88–0,90 MB, 12. sezonda 1,50 MB. 1, 6 ve 12. sezon kodlama/çözme noktaları tamamlandı. İki kariyerden 50. sezon dosya boyutu veya masaüstü etkileşim gecikmesi tahmin edilmemeli.

**Büyüme noktaları.** Büyük bir katalogda tekrarlı kadro ve transfer filtreleri oyuncu sayısı ile büyür. Önce ülke, uygun mevki ve sözleşme durumu dizinleri ile haftalık önbelleği profil çıkararak değerlendirin. Tek bir dünya RNG akışına çok lig eklemek mevcut lig sonuçlarını değiştirir. Yarışma ve hafta bazlı kararlı RNG akışları, açık bir geçiş politikasıyla ele alınmalı. LiveMatch önizlemesindeki kopya maliyeti, dünya ve geçmiş büyüdükçe artabilir. Sıcak alanları ölçmeden kopyayı kaldırmak, iptal/tekrar durumunda kaydı kirletebilir. 2D için küçük olay penceresi ve çizim nesnelerinin yeniden kullanımı uygun. Bütün maç karelerini kalıcı kayda yazmak büyüme bütçesini hızla tüketir.

**Test kapsamı ve hata ayıklama.** Mevcut kalite günlüğü 183 yürütülen test kaydı, 4 atlama ve 179 başarılı test bildiriyor. Arşivdeki uzun kariyer koşuları ek kanıt; bu denetimde yeniden çalıştırılan kariyerler 12 sezonla sınırlı. İleride logda atlanan her testin nedeni ve gerekli fixture kaynağı ayrı görünmeli. Yeni maç tanılaması tohum, maç kimliği, komutlar ve kritik karar olaylarını içerebilir. Varsayılan oyun oturumunda ayrıntılı iz oluşturmaya gerek yok. Tk callback p95, kullanıcı tıklaması sonrası gecikme ve çok sezon sonra filtreleme süreleri ayrıca ölçülmeli.

## 12. Atlas'ın sekiz önerisi

| Fikir | Karar, değer ve kapsam sınırı |
|---|---|
| A · Dünya hafızası | **Uygula, P1.** `gundem` yanında sezonluk, sınırlı dönüm noktası dizini. Bir kupayı ve bir rekoru yıllar sonra kaynak olayına bağla. Her maçı ve diyalogu kalıcı saklama. |
| B · Rakip hoca kimliği | **Kademeli uygula, P1.** `mac.coach_step` içinde risk ve rotasyon profili. `is_piyasasi` değişen hocayı taşır, `piyasa_ai` tercihi kullanır. Birkaç gözlenebilir fark yeterli. |
| C · Gerçekçi belirsizlik | **Uygula, P1.** `personel.finish_scouting` aralıklarını mevcut ekrana taşı. Süre ve gözlemci kalitesi belirsizliği azaltır. Kural sonucu, teklifin geçerliliği ve ödenecek tutar açık kalmalı. |
| D · Dinamik ekonomi | **Aşamalı, P1–P2.** `donem.index` üzerine gerçekleşen yerel gelir/maaş dağılımı, `finans` ile ödeme yükü. Şoklar ancak piyasa ölçümü ve mali limitler sağlandıktan sonra. |
| E · Alternatif tarih haberi | **Uygula, P1.** `gundem.record` gerçek başlangıç ve simülasyon olayını tarih ve kökenle ayrı tutar. Tarihsel sonucu haber üretimine gelecekte zorunlu girdi yapma. |
| F · Akıcı kariyer | **Koru ve geliştir, P0–P1.** Aynı Model 4 ile hızlı ve 2D. `LiveMatch` yalnızca maçta uygulanan komutu taşır. Vakit kazanmak için kuralları değişen bir hızlı yol düşük değerli. |
| G · Uzun kariyer | **Yayın kapısı, P1.** 30–50 sezon ekonomisi, oyuncu yapısı ve kayıt büyümesi. Tam ayrıntılı küresel simülasyon bu koşulu ölçmek için gerekli değil. |
| H · Açıklanabilir maç | **Uygula, P0.** `mac.detail` olaylarından gözlemlenebilir ölçü ve örnek sayısı. Tek maçta hamleye kesin gol/puan katkısı atanması elenmeli. |

## 13. Hızlı kazanımlar ve uzun vadeli projeler

- **Hızlı kazanımlar.** `arayuz.report` üzerinde hangi beş dakikanın veya olayın gösterildiğini belirtmek, `duran_top_ui` rol uygunluğu ipucunu netleştirmek ve `finans.commitments` ile ödeme özeti çıkarmak düşük kayıt riski taşır. Kaynak dosya kontrolünden sonra aynı dil anahtarlarıyla TR/EN doğrulanmalı.
- **Orta vadeli projeler.** `tarihsel.reconcile` için kaynaklı giriş, `piyasa_ai` için transfer dağılımı ve `personel.finish_scouting` için belirsizlik. Bunlar doğru kimlik, ücret takibi ve gösterim katmanına dayanır. Kadro ve takas verisi daha iyi ölçüldükçe kulüp itibarı güvenle değiştirilebilir.
- **Uzun vadeli projeler.** `yarisma` dönem kuralları ve takvim üzerinden Avrupa, bir hafif dış lig ve ardından milli takım. `gundem` hafızası ve `kayit` için büyüme bütçesi aynı planın parçası. Çok ligli genişleme, ilk ligin oynanış ve performans kapılarından sonra gelmeli.

## 14. Bağımlılıklarıyla geliştirme yol haritası

| Sıra | Sürüm adayı | Çıktı ve bağımlılık |
|---|---|---|
| 1 | v0.9.4 · Maç kararları | Kalibre edilmiş pas kanalı, destek/örtü ve anlaşılır olay analizi. Başlangıç koşulu mevcut eşleştirilmiş maç ve kayıt tabanı. Çıkış koşulu Bölüm 15. |
| 2 | v0.9.5 adayı · 2000 başlangıcı ve piyasa | Kaynaklı başlangıç/katılım, tescil kuralı doğrulama, ücret ve transfer dengesi, sözleşme görünümü. Bağımlılık kaynak sözlüğü, sahiplik doğrulayıcısı ve işlem telemetrisi. |
| 3 | v0.9.6 adayı · Kariyerin hafızası | Hoca kimliği, gözlem aralığı, basın ve olay geçmişi, performans kabul ölçümleri. Bağımlılık olay kimliği, dönem kuralı, istikrarlı yıllık bütçe ve şema migrasyon kararı. |
| 4 | v0.9.7 ve sonrası · Futbol dünyası | Bir hafif lig, sonra yıllık Avrupa formatı ve takvim. Bağımlılık haftalık bütçe, oyuncu/lig kimliği, dönem kuralları ve 30 sezon kabulü. İkinci genişleme ilk performans kapısından sonra. |
| 5 | v1.0 · Yayın kabulü | Bölüm 16 koşulları sağlandığında aday sürüm. Tarihsel veri doğrulama, geri uyum ve uzun kariyer ölçümleri birlikte raporlanmalı. |

## 15. v0.9.4 için önerilen kapsam

1. **Pas kanalı ve boşta top.** `saha_motoru.PitchState.pass_ball` adaylarını, pas yolunda topa önce ulaşabilecek rakibe göre değerlendir. `CalibratedPitch.pass_miss` mevcut top kaybı yoluyla aynı olayı üretmeli. Açık ve kapanan kanal için sabit sahne testi, 3 kadro profili için maç ölçümü ekle.
2. **Bir topsuz destek ve bir örtü kuralı.** `CalibratedPitch.target_adjust` içinde ölçülebilir tetikleme. Çıkmış bek, destek oyuncusu, kalan savunma. 10 kişi, otomatik rol ve kaleci durumunda mevcut `mac.substitute_side` davranışı korunmalı.
3. **Kararın ekrandaki izi.** `mac.detail` ve `arayuz.report` üzerinde seçili olay, baskı, pas kaybı ve taktik değişim zamanı. 2D aynı olayın karesini vurgulayabilir. Yeni kalıcı maç geçmişi gerektirmeden çalışmalı.
4. **Küçük sürüm kapısı.** Sabit tohumla en az üç eşleşmede analiz; hızlı/2D ve eski modeller için regresyon; eski şema açma/kaydetme; Türkçe ve İngilizce metin. Kapalı kanal senaryosunda kesilme veya alternatif pas artmalı. Açık kanal senaryosu gereksiz cezalandırılmamalı. Pres kondisyon farkı, rol konum farkı ve 10 kişi/kaleci olayları korunmalı.

Bu sürüm için ligler, şema değişimi, ayrıntılı oyuncu ilişki ağı, tam maç tekrar kaydı ve 3D ertelenmeli. Ölçümlerde etkisiz çıkan rol etkileşimi, ayrı bir yeni arayüz kontrolüne dönüşmemeli.

## 16. v1.0 kabul kriterleri

Hedefler önerilen yayın kapılarıdır. Bellek ve gecikme bütçeleri referans Windows makinesi, Python/Tk sürümü ve etkin lig profili sabitlenerek sınanmalı.

| Alan | Ölçülebilir kabul |
|---|---|
| Maç doğruluğu | En az 300 eşleştirilmiş Model 4 hızlı/2D maçında skor, olay dizisi ve kariyer sonucu birebir. Altı diziliş; kırmızı kart, kaleci değişimi, aynı dakika talimatları ve süre sonu dahil. Olay muhasebesinde sıfır tutarsızlık. |
| Taktik çeşitlilik | En az 6 kadro eşleşmesi × 30 tohum. Pres/top kazanımı/kondisyon ve genişliğin sahadaki konumu için beklenen yön. Her pakette hem fayda hem bedel görünür. Gol, şut ve kart dağılımları rol ve lig bazında incelenir; eşiklerin kaynağı sürüm raporunda yazılır. |
| Tarihsel veri | Açılış fikstürü ve sonuçlarında 306/306. Başlangıç kadrosundaki tüm tarihsel oyuncular için doğum ve kulüp kanıtı veya yayımlanmış eksik listesi. Gelecekteki kayıtlı tarihsel oyuncularda kanıtlı girişten önce sıfır kullanılabilirlik. Kurgusal kimlikler %100 işaretli. |
| Dünya ve ekonomi | En az 10 farklı tohumda 30 sezon, en az 3 tohumda 50 sezon. Her hafta sahiplik ve kadro kontrolü, sezon sonu gelir/maaş/borç dengesi. Sıfır yinelenen sahiplik, takvim kopması ve kayıpsız kayıt testinde hata. Transfer türü ve yaş/pozisyon dağılımı yayımlanır. Bedelsiz oranı, takımların bağlayıcı ödemeleri ve bütçe tipi uç değerleri incelenmeden onay verilmez. |
| Kayıt | Desteklenen her eski şema/modelden anonim fixture, aç–ilerlet–kaydet–yeniden aç. Kesintili yazmada doğrulanabilir yedek. Kariyerin RNG durumu ve sahiplikleri korunur. 30. sezonda kayıt hedefi ≤ 12 MiB, 50. sezonda ≤ 20 MiB, referans profilde. |
| Performans | Referans profilde hızlı hafta p95 ≤ 250 ms. Arama/filtre p95 ≤ 150 ms ve 2D oynatımda Tk olay döngüsü gecikmesi p95 ≤ 50 ms. 30 sezon noktasında bir ligli profil tepe bellek hedefi ≤ 150 MiB. Ek ligler için ayrı bütçe yayımlanır. |
| Türkçe/İngilizce arayüz | Kadro kurma, teklif verme, canlı değişiklik, maç raporu ve yeni sezon akışı iki dilde geçer. Altı temel görevden en az beşini ilk kez oynayan kullanıcılar yardım almadan tamamlayabilmeli. Klavye odağı ve 1280×720 görünüm kontrol edilir. |
| Yayın regresyonu | Temiz kopyada genel test özeti geçti/atlandı/başarısız olarak yayımlanır. Açık kritik hata ve açıklamasız atlama sayısı sıfır. Ölçüm komutları ve tohumlar yeniden üretilebilir. |

Bu kapsam için ilk karar, v0.9.4'te pas kanalı/destek ile maç açıklamasına odaklanıp odaklanılmayacağıdır. Rapor araştırma teslimatıdır.
