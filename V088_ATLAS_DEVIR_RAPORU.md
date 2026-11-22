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
