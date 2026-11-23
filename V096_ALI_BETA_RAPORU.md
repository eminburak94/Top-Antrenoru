# Top Antrenörü v0.9.6 · Ali Beta

Kaynak dalı `develop/v095-preseason`, temel commit `aeb47040e27d2ebe0028eb208477d182c7395363`. Beta dalı `develop/v096-ali-beta`. Paketin kaynak commit’i `e2a7e6c552eee26b181a7682cf0af4f2865111a9`.

## Kariyer dayanıklılığı

`beta_kariyer_v096.py` sabit tohum 960 ile iki hazırlık maçı, sezon başına 34 hafta ve sezon geçişi çalıştırır. 2000, 2004, 2009, 2019 ve koşunun son sezonu denk geldikçe geçici diske kayıt alınıp geri yüklendi. Her sezon geçişinden hemen sonra kariyer JSON karşılaştırması yapıldı. Kadro sahipliği, emekli kayıtları, bütçeler, gol toplamları ve haftalık maç sayısı denetlendi.

| Kulüp | Motor | Sezon | Lig maçı | Üretilen oyuncu | Emekli | Transfer kaydı | Sakat oyuncu-haftası | Kadro aralığı |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gençlerbirliği | Model 4 | 5 | 1.530 | 186 | 47 | 81 | %1,99 | 19–22 |
| Galatasaray | Model 4 | 10 | 3.060 | 400 | 200 | 201 | %2,10 | 19–24 |
| Erzurumspor | Eski hızlı motor | 20 | 6.120 | 957 | 687 | 494 | %2,22 | 19–23 |

Sakatlık oranı, sezon içindeki tüm kadrolu oyuncu-haftalarının sakat görünen payıdır. Tekil sakatlık olay oranı değildir. Son geçişlerde ortalama haftalık maaş sırasıyla 1.964, 1.925 ve 1.627 USD, medyan transfer bütçesi 1.442.733, 2.455.667 ve 3.454.833 USD oldu. Bu koşularda veri denetimi hatası veya takılan sezon geçişi görülmedi. En uzun modern motor denemesi 10 sezon sürdü.

## Rakip teknik direktör

Model 4 taktik planı etkinse rakip, devreden itibaren beş dakikada bir skoru, zamanı, sahada kalan dizilişi ve oyuncuların profillerini değerlendirir. 60. dakikadan sonra gerideyse veya devreden itibaren iki farkla gerideyse hücuma yönelir. Yüksek pres için yeterli kondisyon ve çalışma oranı gerekir. Eksik kalan takım yüksek pres uygulamaz. Son bölümde öndeyse çizgiyi derinleştirip bekleri tutabilir ve kontra arar. Rakip forvetlerin hızı kendi savunmasını aşıyorsa çizgiyi daha derine alabilir. Orta sahanın sayısı ve pas becerisi pas uzunluğunu, kanat genişliği ve bek sayısı bindirme seçimini etkiler. Motor talimatları maç analizine yazar.

| Oyuncu takımı ve dizilişi | Rakibin tamamladığı pas | Rakibin hücum üçte birinde topa sahip olduğu adım | Rakibin ileride top kazanımı |
| --- | --- | --- | --- |
| Galatasaray 4-4-2, tohum 960 | 26 → 19 | 12 → 4 | 2 → 0 |
| Erzurumspor 3-5-2, tohum 961 | 20 → 22 | 1 → 1 | 0 → 0 |
| Gençlerbirliği 4-3-3, tohum 962 | 36 → 29 | 15 → 4 | 3 → 2 |

Her satır eski ve yeni karar politikalarını aynı tohum ve aynı başlangıç koşulunda karşılaştırır. Yeni politika bu örneklerde hem artan hem azalan ölçümler üretti. Bu üç karşılaşma genel rekabet dengesini kanıtlamaz.

## Ali için açılış ve paket doğrulaması

Ana ekranda kulüp seçiminin Temmuz 2000 hazırlıklarına götürdüğü belirtiliyor. Varsayılan dil Türkçe, TR / EN geçişi korunuyor. Yeni varsayılan kayıt klasörü `%LOCALAPPDATA%\TopAntrenoru\v0.9.6\saves`. Önceki kayıt klasörleri yükleme aramasında. Kayıt şeması 3.

Kaynak regresyonu ayrı Windows test masaüstünde geçici kayıtlarla tamamlandı. **195 test metodu, 0 hata, 0 başarısızlık ve 26 atlama kaydı.** 22 atlama eksik isteğe bağlı tarihsel kaynaklardan geldi. Genel regresyonda dört eski çok sezonlu koşu atlandı. Bu rapordaki ayrı 5, 10 ve 20 sezon denemeleri yürütüldü. Küçük pencere ve iki dilde gezinme testleri geçti.

PyInstaller 6.22.3 ile hazırlanan Windows x64 paketinin ZIP bütünlük kontrolü geçti. EXE, kaynak ağacından uzak bir geçici klasöre ZIP’ten ayıklandı. Sistem için ayrılmış PATH ve geçici kullanıcı dizinleriyle, dış Python ve Tcl ortam değişkenleri olmadan sınandı.

1. EXE’ye argüman vermeden başlatıldığında **Top Antrenörü v0.9.6 Ali Beta** ana penceresi açıldı ve normal kapanışta çıkış kodu 0 alındı.
2. Aynı dondurulmuş EXE’nin test senaryosu Türkçe ilk açılış, İngilizceye geçiş, Fenerbahçe kariyeri, Galatasaray ile bir hazırlık maçı, antrenman planı, personel ve yönetim ekranları, transfer, 4-3-3 seçimi, 2D lig maçı ve geçici diske kayıt sonrası yeniden açılışı doğruladı.
3. ZIP oyun EXE’sini, `_internal` çalışma zamanı ve veri dosyalarını, `BASLANGIC_REHBERI.txt`, `BILINEN_HATALAR.txt` ve `SURUM.txt` dosyalarını içeriyor. Testte kişisel kayıtlar kullanılmadı.

## Bilinen sınırlar

- Paket kod imzası taşımıyor. Windows SmartScreen veya kurumsal güvenlik kuralları Ali’nin bilgisayarında uyarı gösterebilir. Doğrulama eldeki Windows x64 ortamında yapıldı. Ali’nin bilgisayarında test yapılmadı.
- Sezon öncesi yalnızca Temmuz 2000 için açık. Uzun kariyer sonuçları birer sabit tohumlu denemedir. 20 sezon Modern Model 4 ile sınanmadı.
- 5/10/20 sezon denetimlerinde ve doğrulanan paket senaryosunda kritik hata görülmedi. Eski tarihsel kaynakları gerektiren atlamalar doğrulama kapsamı dışında.

## İndirme

Dosya `Top_Antrenoru_v0.9.6_Ali_Beta.zip` · **13.575.651 bayt**.

SHA-256 `d66a5950bfedba493b4897ac4625c58dec3172a9c12c86da851e1b29918303ec`

[Windows x64 ZIP dosyasını indir](https://github.com/eminburak94/Top-Antrenoru/releases/download/v0.9.6-ali-beta/Top_Antrenoru_v0.9.6_Ali_Beta.zip) · [GitHub ön sürümü](https://github.com/eminburak94/Top-Antrenoru/releases/tag/v0.9.6-ali-beta)
