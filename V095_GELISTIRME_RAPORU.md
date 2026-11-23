# Top Antrenörü v0.9.5 geliştirme raporu

Dal `develop/v095-preseason`. Taban v0.9.4, `920f3d7aca52bb82017fffb642ffc09c96c9b11c`. İlk aşama `d1f4a44`. 2000 başlangıcı, alternatif tarih ve Türkçe varsayılanıyla Türkçe/İngilizce oynanış korundu.

## Sezon öncesi

Kulüple başlayan yeni kariyer Temmuz 2000 takvimini açar. 4, 11, 18 ve 25 Temmuz için **Rakibi planla** ile ligdeki bir kulüp ve iç saha/deplasman seçilebilir. **İptal et** henüz oynanmamış randevuyu kaldırır. **Hazırlık haftasını ilerlet** program boşsa antrenman ve toparlanmayı yürütür, maç varsa seçili izleme moduyla maç merkezine veya hızlı sonuca gider. Dört haftadan sonra ilk lig haftası açılır. Sonuçlar lig fikstüründeki **Temmuz 2000 hazırlık programı** bağlantısından da okunabilir.

- Maçtan önce mevcut ilk 11 ve taktik ekranı kullanılabilir. Hazırlık maçında takım başına en fazla altı değişiklik yapılabilir. Çıkan oyuncu geri dönemez. Lig cezaları hazırlık maçında oyuncuyu engellemez ve hazırlık turunda çekilmiş sayılmaz.
- Süre alan oyuncunun kondisyonu ve formu değişir. Kullanılan dizilişe maç başına 0,12 takım gücü puanı ekleyen küçük bir uyum etkisi vardır. Bu etki ilk dört lig haftasında azalır. Diziliş değiştirilirse eski dizilişin puanı yeni düzene aktarılmaz.
- Hazırlık skorları kendi takviminde tutulur. Lig puanları, lig gol ve oyuncu istatistikleri, menajer sicili ve lig fikstürü yalnızca resmî maçla güncellenir. Hazırlık haftasında lig geliri, maaş veya bonservis taksiti kaydedilmez.
- Takvim sabit dört hafta ve 2000 yazı için geçerli. Rakip seçimi mevcut lig kulüpleriyle sınırlı. Rakipten onay alma, saha kiralama, turnuva, hazırlık maçı geliri ve sonraki sezonlarda yeniden yaz takvimi bu aşamanın dışında.

## Birikimli yük ve sakatlıktan dönüş

**Antrenman** tablosu son üç tamamlanan haftayı eskiden yeniye dakika ve antrenman yükü olarak gösterir. Hazırlık ve lig dakikaları aynı pencereye girer. Yorgunluk arttıkça kondisyonun toparlanma tavanı düşer ve lig maçında sakatlık olasılığı artar. Boş haftalar ve toparlanma seansları pencereyi hafifletir. Otomatik antrenman yüksek yorgunlukta toparlanmaya geçebilir. Son maçı tek başına kullanan v0.9.4 göstergesi, kayıtlı haftalık yük yoksa geçişte kullanılmaya devam eder.

- Sakat oyuncu normal tedavi sayacını tamamladıktan sonra bir veya iki hafta hafif toparlanma çalışır. Kademeli dönüşte kondisyon tavanı ve artmış sakatlık riski sürer. Sağlık protokolü yoğun bireysel planı geçici olarak geçersiz kılar. Hafif toparlanma gelişim kredisi kazandırmaz. Ana gelişim ve yaşlanma formülü korundu.
- **Teknik ekip → Personel arama** bölümünden fizyoterapist bulunabilir. Yeni adaylar mevcut maaş ve kontenjana tabidir. Antrenörün çalıştırma becerisi antrenman yükünü azaltır. Kondisyoner ve fizyoterapist toparlanma tavanını artırır. Fizyoterapistin becerisi 15 veya üzerindeyse kademeli dönüş iki haftadan bir haftaya iner. Kulübe özgü etki değerleri Antrenman ekranında yazıyor.
- Sabit girdili testte antrenör becerisi 16 iken yoğun fiziksel seans yükü 8’den 6’ya düştü. Kondisyon becerisi 15 olan kondisyonerle toparlanma tavanına 3 puan eklenirken fizyoterapist alımından sonra ek puan 5 oldu ve dönüş bir haftaya indi. Üç dinlenme haftası aynı örnek oyuncunun birikimli yükünü sıfırladı.

## Doğrulama

Son Windows regresyonu `--gui` etkin, ayrı test masaüstünde tamamlandı. **193 test metodu**, günlükte **169 başarılı sonuç satırı**, **26 atlama kaydı**, **0 başarısızlık**, **0 hata**. Alt testlerin atlama kayıtları ayrı sayılır. Tarihsel kaynaklar bulunmadığı için 22 kayıt atlandı. İsteğe bağlı dört çok sezonlu test `--long` gerektirdiği için çalıştırılmadı.

- İlk aşama için 13 hedefli test geçti. Yük, personel ve hazırlık odaklı sonraki koşuda 20 test metodu çalıştı. Tarihsel kaynak gerektiren bir test atlandı, hata görülmedi.
- Testler yeni takvimden lige geçişi, 6 değişiklik sınırı ve yeniden giriş yasağını, lig verisinin ayrılığını, fizyoterapist sözleşmesi ve kayıttan yüklemeyi, birikimli yük penceresini ve aynı tohumla 2D kayıtlı/hızlı simülasyon eşdeğerliğini kapsıyor.
- İlk kapsamlı koşuda mevcut Tk testleri yeni kariyerin doğrudan ligde başladığını varsaydığı için başarısız oldu. Senaryolar Temmuz akışıyla güncellendi. Yedek kayıt testinde yeni isteğe bağlı alanlar hesaba katıldı ve JSON anahtar sırasından bağımsız karşılaştırma yapıldı.
- 960×600 ve yüksek Tk ölçeğinde planlama ve ilerleme düğmelerinin kesildiği tespit edildi. Kontroller takvim tablosunun ve açıklamanın üstüne alındı. Düzeltilen yerleşim iki dilde hedefli Tk testinden geçti.
- Tohum 195 ile üç kulübün her biri iki hazırlık ve altı lig maçı tamamladı. Altıncı lig haftası sonunda ortalama kadro kondisyonu Galatasaray’da 82,7, Gençlerbirliği’nde 81,1 ve Erzurumspor’da 79,2 idi. Aktif sakat sayıları sırasıyla 0, 0 ve 1. Bu kısa koşu kariyer akışını sınar. Uzun vadeli sakatlık kalibrasyonu için örneklem yetersiz.
- Kayıt şeması 3 korundu. Eski kariyerler mevcut lig haftasından devam eder. v0.9.5 arayüzünde yük takibi açıldığı andan itibaren veri biriktirir. Önceki sürüm dizinleri yükleme aramasında, varsayılan kayıt dizini v0.9.5 altında. Kişisel kayıtlar test girdisi olarak kullanılmadı. FM oyunları açılmadı.

## Kalan işler

Rakip teknik direktör yapay zekâsı bu turda değiştirilmedi. Bir sonraki turda diziliş ve oyuncu özelliklerine göre verilen kararları aynı tohumla pas, pres sonrası top kazanımı, pozisyon kalitesi ve kondisyon üzerinden karşılaştırmak gerekir. Yeni yük modelinin çok sezonlu sakatlık oranı ve kadro derinliğine etkisi ayrıca ölçülmeli. Sağlık modeli kademeli kondisyon sınırı uygular. Pozisyona özel rehabilitasyon ve oyuncu başına tıbbi dakika tavsiyesi henüz yok.

FM 2005 incelemesinden alınan iki tasarım hedefi, lig öncesinde kadroyu deneyebileceğin bir takvim ve kondisyonun arkasındaki yükü görebileceğin bir oyuncu tablosuydu. Yeni mekanikler Top Antrenörü’nün kendi maç motoru, takvimi ve personel bütçesi üzerinde çalışır. [FM 2005 gerçek oynanış incelemesi](https://github.com/eminburak94/Top-Antrenoru/blob/45a3b479c078f4d774c9fd2281ea2bf145883749/V093_FM2005_GERCEK_OYNANIS_INCELEMESI.md)
