# Top Antrenörü v0.9.4 geliştirme raporu

Geliştirme dalı `develop/v094-playtest`, başlangıç noktası `4c8c4fa86639d26b57ecd094bc3dc4ccb953c76c`. Türkçe varsayılan dil. Yeni ekran metinleri İngilizceye de çevrildi. 2000–01 başlangıcı korundu.

## Antrenman ve maç hazırlığı

Ana ekrandaki **Antrenman** düğmesi haftalık plana açılıyor. Tabloda kondisyon, son lig maçındaki dakika ve hazırlık notu birlikte görülüyor. İstediğiniz oyuncuları seçip **Planı uygula** düğmesine basabilirsiniz. Seçim boşsa plan listedeki oyuncuların tamamına uygulanır. **Haftalık rapor**, uygulanan odak ve yoğunluğu, katılım durumunu ve seansın kondisyon etkisini gösteriyor.

- Son lig maçında en az 60 dakika oynayan oyuncunun yoğun seansı en fazla 2 ek kondisyon puanı tüketir. Bu ek yük gelişim kredisi vermez.
- Otomatik mod düşük kondisyonu rutin haftalık toparlanmadan önce değerlendirir. Son maçta süre almamış, kondisyonu yeterli 25 yaş altı oyuncular teknik çalışma yapar. Sakat oyuncuların mevcut tedavi akışı sürer.
- Yaşa, performansa ve süreye bağlı mevcut gelişim formülleri korundu. Son maç dakikası bir hazırlık göstergesi olarak kullanılıyor. Özellikle ilk hafta ve kulüp değişimi sonrası veri yoksa dakika sütununda işaret gösterilir.

## Maç merkezi ve taktikler

- Maç penceresinin üst kısmından yaklaşım, pres, tempo ve desteklenen kariyerlerde **Taktik planı** açılabilir. Talimat satırı kararın verildiği dakikayı, bekleyen motor adımını ve uygulandığı dakikayı gösterir. Aynı dakikada değişen kararların son geçerli hâli dikkate alınır.
- 2D görünümünde, yakalanan pas karelerinde pası veren ve alan oyuncu, şut karelerinde olay sonucu yazıyor. Yapılan değişiklik anlatıma giriyor, yeni oyuncu sahada vurgulanıyor ve maç raporunda iki oyuncunun adı yer alıyor.
- **Maç raporu**, talimatın çevresindeki beşer dakikada şutları ve kayda giren başarılı/denenen pasları gösteriyor. Uyumlu Model 4 kariyerlerinde savunma, orta saha ve hücum üçte birindeki topa sahip olma adımları takım başına raporlanıyor. Şut konumları mevcut pozisyon kaydında görülebiliyor. Önce/sonra rakamları gözlenen akışı gösterir ve rakibin eşzamanlı hamlelerinden ayrıştırılamaz.
- Sabit tohumlu testte gerçek taktik talimatı hem 2D kaydı açık hem kapalı simülasyona uygulandı. Sonuç, saha bölgesi ölçümleri ve sonraki hafta dâhil seri hâle getirilen kariyer durumları eşleşti.

## Yönetim ve taraftarlar

**Yönetim / Taraftar** ekranında son rakip ve skor, güven ve iş riski farkları, sportif ve mali baskı, sonuçlanan taahhüdün etkisi ve taraftar tepkisinin maç bağlamı görülebiliyor. İlk maçtan önce risk, kulübün başlangıç güveninden hesaplanıyor. Eski kayıtlarda ilk değerlendirmeye kadar görülebilen sıfır risk, ilk maçın farkı hesaplanırken doğru başlangıç değerine oturtuluyor.

Önceden ilk galibiyet, sıfır başlangıç yüzünden risk artışı gibi görünebiliyordu. Sabit 3–0 testinde mali stres olmadan güven +2, risk 10’dan 9’a indi. Negatif nakit senaryosunda güven değişmedi, risk 10’dan 18’e çıktı ve mali baskı gerekçesi kaydedildi. Taraftar tepkisi her iki örnekte de pozitifti.

## Testler ve kayıt uyumluluğu

Windows’ta `unittest` keşfi, `--gui` ile 187 test metodu çalıştırdı. Günlükte 163 başarılı sonuç satırı, 26 atlama kaydı, 0 başarısızlık ve 0 hata var. Alt test atlamaları ayrı sayıldığından bu sütunlar test metodu sayısına doğrudan toplanmıyor.

- **Başarılı.** Dört yeni v0.9.4 testi, 2D/hızlı maç eşdeğerliği, aynı dakikadaki son talimat, oyuncu değişikliği ve kırmızı kart sonrasında pozisyon, küçük pencerede maç kontrolleri, iki dilde gezinme ve test kariyerinin diske kaydedilip yüklenmesi.
- **Atlanan.** Yerel tarihsel sürüm kaynakları bulunmadığı için 22 atlama kaydı. İsteğe bağlı çok sezonlu dört test için `--long` açılmadı. Bu yüzden uzun kariyer dengesi ve eksik tarihsel kaynakları gerektiren sürüm karşılaştırmaları bu koşuda doğrulanmadı.

Testler geçici kayıt diziniyle çalıştırıldı. Tk regresyonları ayrı bir Windows test masaüstünde yürütüldü. Aktif masaüstünde fare, klavye veya ekran yakalama kullanılmadı. Kişisel kayıtlar ve mevcut EXE paketleri test girdisi olarak kullanılmadı. Kayıt şeması 3 kaldı. Yeni alanlar isteğe bağlı, eski alanların biçimi aynı. Yeni varsayılan kayıt dizini v0.9.4 sürümüne ait. Yükleyici v0.9.3 ve önceki sürüm dizinlerini de arıyor.

## FM 2005 karşısında ilerleme

Önceki uygulamalı incelemede FM 2005’in seans yükü çubukları, maç içi taktik bekleme durumu ve saha bölgesi ekranı doğrudan görüldü. v0.9.4 bu üç ihtiyaca haftalık oyuncu tablosu, motor adımıyla eşleşen talimat geri bildirimi ve rapordaki saha bölgesi sayımlarıyla karşılık veriyor. Karşılaştırma, önceki oynanış gözlemlerine ve bu paketin otomatik testlerine dayanıyor. Bu turda FM yeniden çalıştırılmadı. [FM 2005 gerçek oynanış incelemesi](https://github.com/eminburak94/Top-Antrenoru/blob/45a3b479c078f4d774c9fd2281ea2bf145883749/V093_FM2005_GERCEK_OYNANIS_INCELEMESI.md)

## Açık kalan mekanikler ve sonraki adımlar

1. **Antrenman.** Tek maçlık süre göstergesini birkaç haftalık maç yüküyle değiştirmek ve sakatlıktan dönen oyunculara kademeli seans planı vermek. Günlük seans takvimi ve antrenör kapasitesinin seanslara etkisi bu pakette yok.
2. **Maç.** Kararı aynı tohumda karşılaştıran otomatik deneyleri farklı dizilişlerle genişletmek. Bölge sayımları bir temas haritası veya oyuncu koşu analizi düzeyinde ayrıntı sunmuyor. Taktik penceresindeki kısa dönem istatistikleri, birbirine yakın talimatlarda örtüşebilir.
3. **Kulüp.** Son maç açıklamasını birkaç haftalık beklenti ve tepki geçmişine yaymak. Son maç gerekçesi kayda geçiyor. Uzun bir yönetim ve taraftar tepkisi arşivi tutulmuyor.

## Değiştirilen dosyalar

| Alan | Dosyalar |
| --- | --- |
| Haftalık plan, gelişim verisi ve rapor | `antrenman.py`, `oyuncu.py`, `kariyer.py`, `yonetim.py`, `yonetim_metinleri.py` |
| Maç simülasyonu, 2D ve gezinme | `arayuz.py`, `mac.py`, `mac_gorunum.py`, `saha_motoru.py` |
| Kulüp tepkileri | `yasayan_kulup.py`, `kulup_ui.py` |
| Kayıt, sürüm ve başlatma | `kayit.py`, `oyun.py`, `BASLAT.bat`, `PAKETLE.bat` |
| Regresyon | `test_v060.py`, `test_v085.py`, `test_v088_2d.py`, `test_v088_kayit.py`, `test_v094.py` |
| Teslimat | `V094_GELISTIRME_RAPORU.md` |
