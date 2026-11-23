# Top Antrenörü · Oyuncu alımı araştırması ve geliştirme raporu

GitHub’daki `develop/v096-ali-beta` dalı ve kaynak commit’i `8868b52fca6b285474f6ef4a946bf44eb034721b` temel alındı. Çalışma dalı `develop/scouting-recruitment-depth`. [Ali Beta kaynak kodu](https://github.com/eminburak94/Top-Antrenoru/tree/8868b52fca6b285474f6ef4a946bf44eb034721b)

## Referans kanıtı

| Kaynak | Kanıt türü | Bulgular |
| --- | --- | --- |
| FM 2005 | **Doğrudan doğrulanan, önceki test kariyeri** | Gözlem, oyuncu araması ve kısa liste ayrı ekranlar. Profilde sözleşme eylemleri ve transfer durumu görüldü. Gelen kutusunda oyuncu için fiyat sorgusu görüldü. Finans özeti ve oyuncu araması bütçeyi gösterdi. İki ekrandaki tutar farkının nedeni doğrulanmadı. |
| FM 2005 ve FM 2006 | **Dosyalardan doğrulanan, bu tur** | Kurulum değişiklik notlarında FM 2005 kısa liste, maaş bütçesi ve ezeli rakibe transfer düzenlemelerini, FM 2006 ise sözleşme maaşı ve gelecekteki transferin durum göstergesini anıyor. Bu notlar karar formüllerini göstermiyor. |
| FM 2008 | **Dosyalardan doğrulanan, bu tur** | Kurulumdaki `changelist.txt`, transfer merkezinde iptal edilen işlemler, gözlem raporunda görevin hatırlanması ve Türkiye ligi bilet/maaş/finans ayarlarını belgeliyor. |
| FM 2009 | **Dosyalardan doğrulanan, bu tur** | Kurulumdaki `changelist.txt`, rekor bonservisin transfer geçmişiyle tutarlı görünmesi ve transfer penceresi kapanınca listeye alınma taleplerinin zamanlamasını belgeliyor. |
| CM 03/04 ve CM4 | **Dosyalardan doğrulanan, bu tur** | CM 03/04 `readme.rtf` dosyasında personel ve oyuncu/personel arama kısayolları var. CM4 klasöründe disk imajı bulundu. Disk bağlanmadı ve oynanış çıkarımı yapılmadı. |
| Top Antrenörü için sonuç | **Çıkarım** | Oyuncunun bir adayı keşfetme, araştırma ve maliyeti değerlendirme adımları arasındaki geçiş kolaylaştığında mevcut ekonomi ve gözlem mekaniği daha anlaşılır kararlar üretebilir. |

Bu turda referans kurulumları salt okunur incelendi. Yeni FM veya CM kariyeri oynanmadı. FM 2006, 2008, 2009 ve CM için yeni doğrudan oynanış kanıtı yok. Kurulum varlığı lisanslı, bağımsız bir oynanış oturumuna erişimi kanıtlamıyor. Önceki FM 2005 oynanış raporu doğrudan gözlem kaynağıdır. [FM 2005 oynanış raporu](https://github.com/eminburak94/Top-Antrenoru/blob/45a3b479c078f4d774c9fd2281ea2bf145883749/V093_FM2005_GERCEK_OYNANIS_INCELEMESI.md) · [Birleşik araştırma](https://github.com/eminburak94/Top-Antrenoru/blob/45a3b479c078f4d774c9fd2281ea2bf145883749/V093_CM_FM_BIRLESIK_SONUC.md)

## Top Antrenörü’nde değişen üç karar

1. **Transfer ve yenileme teklifi.** v0.9.6 tek seferlik maliyeti ve mevcut bütçeyi gösteriyordu. Taksit seçildiğinde toplam maliyetin yanında ayrıca ödeme planı görünüyordu. Yeni taslakta bugün ödenecek tutar, önceki taahhütler sonrası kullanılabilir nakit, kalan transfer bütçesi, haftalık maaş toplamı ve kalan maaş payı gösterilir. Üç taksit teklifinde sonraki iki ödeme de listelenir. Mali nedenleri, kabulde kullanılan aynı hesap üretir. Mali kontrol uygun görünse bile oyuncu veya satıcı reddedebilir ve kadro sınırı ayrıca uygulanır. Kulübün mali kuralları ve sözleşme pazarlığı korundu.
2. **Gözlem.** v0.9.6 oyuncu başına iki haftalık rapor üretiyordu, ancak atanmış veya ilk gözlemci meşgulse ikinci kişi kullanılamıyordu. Artık dış oyuncu profilinden **Gözlem iste** kullanılabilir. Profilde rapor tarihi, yaşı, güveni veya bekleyen işin süresi görünür. Atanmış gözlemci müsaitse önceliklidir, meşgulse kulüpteki uygun meslektaşı görevi alır. Kulüpte gözlemci bulunmaması, tümünün meşgul olması ve bekleyen rapor arayüzde ayrı mesajlar verir. Eski raporlar ve belirsizlik aralıkları yüklenmeye devam eder.
3. **Dizilişe göre oyuncu arama.** **Transfer → Futbolcu arama → Gelişmiş → Diziliş mevkii** seçili formasyonun mevkilerini sunar. Doğal, ikinci veya maç motorunda yeterince yakın sayılan mevkilerde adaylar listelenir. Özet, o mevkiden dizilişte kaç yer olduğunu ve mevcut kadroda sakat/cezalı olmayan kaç oyuncunun o mevkiye uyduğunu gösterir. Bir futbolcu birden fazla mevkiye sayılabilir. Bu sayı tek bir mevkinin kapsamasını anlatır, aynı anda kurulabilen iki ilk 11’i hesaplamaz.

Bu değişikliklerde oyunların kodu, veri tabanı veya varlıkları kullanılmadı. Yeni kayıt şeması, oyun içi para birimi, tarih veya simülasyon modeli eklenmedi. Mevcut arama tercihlerindeki isteğe bağlı filtre alanı tekrar kullanıldı.

## Doğrulama

Ayrı Windows test masaüstünde, geçici kayıt dizini ve `--gui` ile **200 test metodu, 0 başarısızlık, 0 hata ve 26 atlama kaydı**. 22 kayıt eksik isteğe bağlı tarihsel kaynaklar, dördü `--long` gerektiren eski kariyer koşuları nedeniyle atlandı. Beş yeni regresyon geçti. Bunlar taksit özeti ve defter uyumu, iki gözlemcinin kullanılması ve kayıt dönüşü, diziliş mevkilerinin hazır oyuncu sayısı, dış profilde gözlem isteği ve arayüzden diziliş filtresi ile mali özeti kapsıyor. Top Antrenörü’nün mevcut transfer, 2D maç ve kayıt akışları da genel koşuda geçti.

Model 4 ile sabit tohum 970 kullanılarak Gençlerbirliği kariyeri, v0.9.6 tabanında ve yeni dalda normal gözlem isteği verilmeden ayrı ayrı iki sezon oynatıldı. Her iki kariyer 2002 başına ve 19 transfer kaydına ulaştı. Rastgele oluşturulan kariyer kimlikleri çıkarıldığında kayıt içerikleri eşleşti. Bu bir eşdeğerlik kontrolü, genel ekonomi kalibrasyonu değildir.

## Değiştirilen dosyalar

- `finans.py`, `arayuz.py`, `yonetim_metinleri.py` — teklif ve yenileme önizlemesi.
- `personel.py`, `personel_ui.py`, `ise_alim_ui.py` — gözlem dağıtımı, görünür durum ve diziliş filtresi.
- `test_recruitment_depth.py` — motor ve Windows arayüz regresyonları.

## Sonraki öncelikler

1. Birkaç 2000–2010 kariyerinde yaşa, kulüp gücüne ve sözleşme bitimine göre bedelsiz transfer payını ölç. Eski rapordaki 400/470 oranını güncel piyasa oranı sayma.
2. Rapor tazeliği ile bilgiyi ayıran gelişim takibi ekle. Son gözlem aralığı bugün hangi seviyenin bilinmekte olduğunu gösterir. Zaman içindeki değişimin ölçümü için farklı tarihlerde alınmış raporları karşılaştırmak gerekir.
3. Teknik ekip raporlarına oyuncu başına gelişim yönü ve forma süresi bağlamı ekle. Kontrollü uzun koşularla altyapıdan ilk 11’e geçişi ve yaşlanma dağılımını ölç.
