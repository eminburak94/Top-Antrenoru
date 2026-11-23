# Top Antrenörü v0.8.8 — Menajerlik derinliği

Karşılaştırmanın başlangıç noktası `2c4c608`. Dört davranış değişikliği Model 4 kariyerlerinde etkin. AI transfer planı Ekonomi Modeli 2 üzerinden çalışıyor. Kayıt şeması 3 olarak kaldı ve yeni bir kayıt alanı eklenmedi.

## Düzeltilen sorunlar ve yeni davranışlar

1. **AI transferleri ve sözleşmeler.** AI zaten mevki uyumunu, kadro derinliğini, yaşlanan oyuncuları ve nakit tahminini hesaba katıyordu. Aday sıralamasındaki ayrı bonservis ve maaş cezaları, maaşı yüksek serbest oyuncuların sözleşme boyunca neye mal olacağını doğrudan yansıtmıyordu. AI artık bonservis, imza parası ve sözleşme süresindeki maaş toplamını, kulübün transfer bütçesi ve kalan maaş kapasitesiyle karşılaştırıyor. Nakit, maaş bütçesi ve sezon sonu rezervi kontrolleri işlem sırasında da uygulanıyor. Yenilemelerde AI, oyuncu kabul ediyorsa temel ücret isteğini kullanıyor. Önceki %23 artış, temel teklif yetersiz kaldığında devreye giriyor.
2. **Karşı teklifler.** Önceki sabit %22 artış sınırı, oyuncunun alıcının kadrosundaki önemine göre %8–26 aralığında değişiyor. Alıcının işlem anındaki bütçesi ve oyuncunun sözleşme şartları kabulü hâlâ belirliyor. Geri çevrilen karşı teklif açık kalıyor ve tamamlanan satış aynı oyuncuya gelen diğer açık teklifleri sonlandırıyor. Karşı teklif penceresi mevcut tutarla açılıyor ve kabulü belirleyen etkenleri Türkçe ve İngilizce gösteriyor.
3. **Oyuncu gelişimi.** Yaş, potansiyel, antrenman kredisi, forma süresi, sakatlık ve personel etkileri korunuyor. 16–26 yaş aralığındaki aktif oyuncularda sezonluk maç puanları, yeterli maç ve dakika biriktikçe pozitif gelişimi en fazla %13 oranında artırabiliyor veya azaltabiliyor. Zirve yaşından sonra doğal kondisyon yaşa bağlı gerileme hızını en fazla %23 oranında değiştiriyor. Yıllık gelişim raporu bu etkenleri iki dilde açıklıyor.
4. **Yönetim ve iş piyasası.** Yönetim hedefleri ilk 11 gücü ile maaş bütçesinden türetiliyor. Sportif ve mali görevden alma koşulları, sezon sonu itibar değişimi ve kötü mali sicilin başvuruya etkisi aynı şekilde işliyor. Kulüpsüz bir menajerin başvurabileceği uygun bir fırsat kalmadığında, yönetim kontrol haftalarında ligin son altısından boş pozisyonu olmayan bir kulüp yeniden giriş fırsatı açabiliyor. Seçimde kasası negatif olmayan ve itibarı daha düşük kulüpler öncelikli. Normal ilanlar kulüp itibarı, başvurular menajer itibarı, birikmiş galibiyetler ve yakın dönem mali görevden almalar üzerinden değerlendiriliyor. İş piyasası bu başvuru puanını iki dilde gösteriyor. İlan kapanmadan sonuçlanamayacak başvurular engelleniyor.

## Önce ve sonra ölçümleri

Model 4 ve Ekonomi Modeli 2 ile iki başlangıç senaryosu, başlangıç ve değişiklik sürümlerinde aynı tohumlarla 12’şer sezon oynatıldı. Galatasaray bağlamında 88025 kariyeri kulüpte, 88100 kariyeri kulüpsüz başladı. İşsizken mevcut ilanlara başvuruldu ve ilk geçerli teklif kabul edildi. Kullanıcı adına transfer yapılmadı. Her koşuda 408 lig haftası işlendi. Tablodaki transfer sayıları birikimli ve yalnızca tamamlanan işlemleri içeriyor. Kasa ve aktif oyuncu havuzu sezon devrinin hemen ardından, asgari kadro ise kapanan sezonlar boyunca ölçüldü.

| Tohum / sezon | Bedelli transfer | Serbest transfer | Medyan kulüp kasası | Aktif oyuncu | Aktif yetenek std. sapması |
|---|---:|---:|---:|---:|---:|
| 88025 / 3 | 6 → 8 | 40 → 32 | 1.803.956 → 1.939.844 | 346 → 349 | 2,979 → 2,992 |
| 88100 / 3 | 9 → 8 | 41 → 36 | 1.846.096 → 1.716.882 | 349 → 347 | 2,871 → 2,900 |
| 88025 / 12 | 27 → 34 | 238 → 178 | 5.226.366 → 5.301.072 | 345 → 350 | 2,293 → 2,315 |
| 88100 / 12 | 35 → 33 | 230 → 178 | 5.071.714 → 5.386.634 | 344 → 347 | 2,441 → 2,425 |

12. sezonda iki koşunun toplamında serbest transfer payı **%88,3’ten %84,2’ye** indi. Bedelli transferler 62’den 67’ye, serbest işlemler 468’den 356’ya değişti. Her iki tohumda da en küçük sezon sonu kadrosu önce ve sonra 17, herhangi bir kulübün kasasının negatif olduğu hafta sayısı 0 oldu. Kasa tutarları oyunun baz biriminde gösteriliyor.

12. sezon devrinde aktif kalmış 16–23 yaş oyuncularının ortalama yetenek değişimi 88025 için +0,240 → +0,229, 88100 için +0,239 → +0,227. Aktif kalan 33–40 yaş oyuncularında değişim sırasıyla −0,899 → −0,831 ve −0,891 → −0,866. Bu kesit emekli olanları dışarıda bırakıyor. Yetenek dağılımı her iki sürümde de 3. sezondan 12. sezona daraldı. Değişikliğin iki tohumdaki 12. sezon dağılımına etkisi küçük ve farklı yönlerde.

12 sezonda işe alınma / görevden alma 88025’te 4 / 4 → 3 / 3, 88100’de 3 / 2 → 6 / 5 oldu. Kariyer sonuçları transferler ve kadrolar değiştikçe ayrıştığı için işe dönüş yolunun etkisi ayrıca sabit senaryoda doğrulandı. İtibarı 10, mali kesinti sonrası puanı 6 olan menajer 7. haftada uygun ilan buldu, 8. haftada teklif aldı ve kayıt yeniden açıldıktan sonra göreve başladı.

## Test sonuçları

- `python -B -X utf8 -m unittest -v test_v088_menajerlik` ile 6 hedefli test geçti. Karşı teklifte aynı tutarın kadro ihtiyacına göre reddedilmesi veya kabul edilmesi, bütçenin satışı durdurması, toplam maliyet sıralaması, genç performansı, yaşlı kondisyonu ve iş başvurusu zamanlaması doğrulandı.
- `4317e9d` v0.8.7 kaynaklarından Model 1, 2 ve 3 için sentetik kayıtlar üretildi. Yeni sürümde açılıp bir hafta ilerletildiklerinde kodlanmış sonuçlar v0.8.7 referansıyla aynı çıktı.
- Temiz GitHub kopyasında `python -B -X utf8 -m unittest discover -v` başlangıçta 138, değişiklikle 144 test keşfetti. Her iki sürümde aynı 22 tarihsel fixture erişim hatası ve 6 isteğe bağlı test atlaması raporlandı.
- Yerel tarihsel sürümlerin yalnızca kaynak ve veritabanı dosyaları yalıtılmış test dizinlerine kopyalandı. Aynı genel komut bu fixture’larla başlangıçta 132, değişiklikle **138 test geçirdi**. Altı isteğe bağlı test atlandı ve iki koşuda da hata alınmadı. Depodaki Tkinter regresyonları ve eski sürüm kayıtlarının tekrar oynatılması bu koşuya dahil.

## Kalan riskler

- Serbest transferler hâlâ çoğunlukta. Sözleşme yenilemeleri, akademiden takviye ve pazara giren bedelli oyuncu arzı uzun vadeli oranı etkileyebilir.
- İki tohumda finansal kriz görülmedi. Borç altında kadro yenileme ve uzun vadeli kasa birikimi için bu örnekler sınırlı.
- Yetenek standart sapması dağılımdaki daralmayı gösteriyor. Ölçüm, tek tek teknik ve zihinsel özelliklerin farklılığını veya yeni oyuncuların yaş gruplarına göre kalitesini kapsamıyor.
- Yeniden giriş fırsatları kontrol haftalarında oluşuyor ve başvuru süresi sınırlı. Son altı kulübün tümünde açık ilan varsa yeni ilan açılmıyor.
