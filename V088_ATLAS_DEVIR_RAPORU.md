# v0.8.8 Atlas devir raporu

Model 3 açık oyun şutunda takımın hücum gücü ile rakip savunması arasındaki farkı kullanıyordu. Model 4 iki aşamalı isabet/kurtarış hesabına geçtiğinde bu terim kaybolmuştu. Bu, düşüşün kodda görülen bir açıklaması. Doğal maç dinamiğinin diğer değişiklikleri de sonucu etkiliyor.

- Açık oyun isabet hesaplamasına aktif kadroların hücum ve savunma farkına bağlı, ±10 yüzde puanla sınırlı konumsal avantaj geri eklendi. Duran top ve penaltılara uygulanmaz. Model 1–3 kodu korunur. Model 4 kayıt şeması değişmedi, ilerideki maç sonuçları yeni dengeyi kullanır.
- Gecikmiş ikinci sarı duraklamada oyuncuyu ihraç etmişse aynı oyuncuya yeni kart yazılmaz. Faul ve yeniden başlatma korunur. Taç geometrisinde doğrulanmış yeni hata saptanmadı, sıklık için katsayı eklenmedi.

| Aynı 500 maç / tohum | Model 3 v0.8.7 | Model 4 v0.8.7 | Model 4 bu dal |
|---|---:|---:|---:|
| Güçlü galibiyeti / 268 eşitsiz maç | 162 | 144 | 150 |
| Gol / maç | 2,204 | 2,080 | 2,190 |
| Şut / maç | 11,966 | 11,038 | 11,118 |
| Kullanılan taç | 137 | 595 | 573 |
| Faul | 1.943 | 2.417 | 2.405 |
| İhraç | 69 | 143 | 133 |

İlk iki sütun v0.8.7 arşivindeki aynı 500 maçtan. Bu dal için eş tohumlu tek çalıştırma yapıldı. İki düzeltmenin etkisi ayrı ölçülmedi. 133 ihraç toplamı tek başına çift kart hatasının ne kadar yaygın olduğunu göstermez. Taç ve faul sıklığı düşük kalıyor. Güçlü takım farkı kısmen geri geldi.

Sonraki adım: Yeni tohumlarla takım gücü etkisini ayrı ölçmek ve kalan ihraçları direkt kırmızı/ikinci sarı ile olay nedeni bazında incelemek. Uzun kariyer ve EXE bu oturumun kapsamı dışındaydı.

Hedefli testler 10/10 geçti. Tek genel regresyon koşusu 129 test keşfetti: 123 geçti, 6 koşullu test çalıştırılmadı, 0 hata.

## İkinci tur

Takım gücü aktif kadrodaki yeteneği, mevkiye uygunluğu ve oyuncu özelliklerini birleştiriyor. Tempo ve saha derinliği şut seçimini, açı, mesafe ve yakın savunmacı baskısı şut isabetini ve blokları etkiliyor. Birinci turun hücum-savunma farkına bağlı ±10 yüzde puanlık açık oyun katkısı korundu. İkinci turda denge katsayısı değişmedi.

| 500 maç, 268 eşitsiz eşleşme / tohum bandı | Model 3 | Model 4 isabet katkısı kapalı | Model 4 ilk tur | Model 4 ikinci tur |
|---|---:|---:|---:|---:|
| 83000–83249, güçlü takım galibiyeti | 161 | 165 | 174 | 174 |
| 86000–86249, güçlü takım galibiyeti | 156 | 150 | 169 | 169 |

Aynı kulüp eşleşmeleri iki ev/deplasman yönüyle çalıştırıldı. Katkıyı izole etmek için yalnızca açık oyun isabet terimi geçici olarak kapatıldı ve birinci turun kart koruması korundu. Etki iki bantta +9 ve +19 güçlü galibiyetti. İlk tur 81000 bandında 150 ile Model 3'ün 162 altında kalmıştı, dolayısıyla Model 3 karşısındaki üstünlük tohuma bağlı. 83000 ve 86000 bantlarında katkıyla gol/maç 2,136→2,226 ve 2,116→2,236. İkinci turun ölçülen maç toplamları ilk tur koluyla aynı.

Kart denetiminde ikinci tur için 83000 bandında 34 direkt kırmızı ve 125 ikinci sarıdan ihraç, 86000 bandında 46 direkt kırmızı ve 119 ikinci sarıdan ihraç bulundu. Maç içinde bir oyuncuya tekrar kırmızı kaydı yoktu. Ayrı regresyonda, oyuncunun bekleyen sarı kartla değiştirilince kartın kaybolduğu doğrulandı. Model 4 artık değişiklik sırasında bekleyen kartı gösteriyor. Bu ikinci sarıysa oyuncu ihraç ediliyor ve yerine oyuncu giremiyor. Bekleyen kartı olmayan değişiklikler saha önbelleğinden bağımsız kaldı.

Model 4 iki bantta 1.247 taç verdi, 1.219 taç kullanıldı ve 4.833 faul üretti. İki izole haftada ham motor kaydı, haftalık sonuç ve kaydet/yükle sonrası günlük aynıydı. 18 maçta 24 taç kararı, 23 kullanılan taç ve 102 faul korunmuştu. Bu örneklemde düşük sıklık depolama kaybından kaynaklanmıyor. Verilen ve kullanılan taç arasındaki farkın tamamı için ayrı sonlandırma nedeni izlemesi yapılmadı. İhraç hacmi ve düşük taç/faul üretimi açık kaldı. Uzun kariyer, EXE ve yeni lig bu turda çalıştırılmadı.

Hedefli testler 11/11, tek genel koşu 124 geçti ve 6 koşullu test atlandı. Kartı olmayan değişiklik için son küçük koruma sonrası dört v0.8.8 hedefli testi yeniden geçti. Genel koşu ve kalibrasyon tekrarlanmadı.
