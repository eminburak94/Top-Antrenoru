# v0.8.8 2D oynanabilirlik

## Düzeltilen davranışlar

- Son animasyon karesi tüketildiğinde maç tamamlanır. 90. dakikadan sonra eski kare yeniden kuyruğa alınmaz. Önemli Anlar modunda ara dakikada son gerçek saha konumu çizilir.
- Pas, şut ve top sahipliği motor karelerinden gelir. Duran top yerleşimi, ofsayt bayrağı ve hakem sinyali değiştiğinde araya sentetik geçiş karesi eklenmez. Komşu aynı kareler elenir. Top sahibinin saha konumu çakışma giderme sırasında korunur.
- Maçı bitirme işlemi Tk olay döngüsüne dönen bloklara ayrıldı. Duraklatma zamanlanmış işi iptal eder. Oyuncu değişikliği iletişim kutusu kendi odağını alır, ardından maç penceresi odağını geri alır. Başarılı değişiklikten sonra eski oyuncu kareleri temizlenir.
- Takım adları saha renkleriyle eşleşir. Skor ve dakika ayrı satırda, faul, kart ve ofsayt günlüğü vurgu renginde. Olay listesi değişmedikçe yeniden yazılmaz.
- Pres, tempo, genişlik ve yaklaşım mevcut motor komutuna gider. Uygulanan değişikliğin dakikası kullanıcıya gösterilir. Geri bildirim motorun komutu kabul ettiğini bildirir.

Maç kuralları, mevcut modeller ve kayıt yapısı düzenlenmedi. 90. dakika hedefli testinde aynı Model 4 maçının hızlı ve 2D sonuçları ve olayları eşleşti.

## Ölçüm ve Windows doğrulaması

Gerçek Model 4 maçı, tohum 988. 272 ham kare, iki kez art arda çizim isteğiyle 544 istek. Aynı Windows Tk Canvas üzerinde üç tekrarın medyanı 318,34 → 144,29 ms. Koordinat çağrıları 25.568 → 12.737. İnterpolatör çıkışı 604 → 561 kare. Tekrarlı iş yükü özellikle gereksiz çizim maliyetini ölçer. Bu, normal oynatma FPS'i veya bütün donanımlarda aynı hızlanma iddiası değildir. Motor örneklemesi dakika tabanlı kalır.

960×600 TR ve 1280×720 EN kök pencere ayarlarında gerçek maç penceresi açıldı, oynatıldı ve görünür düğmelerin yatay sınırları kontrol edildi. Yerel görüntüler .build/v088-2d altında. 1x/2x/4x kontrolü mevcut, hız seçimi ve duraklatma 4x ile sınandı. Ayrı Windows DPI ölçekleri, 1920×1080 ve insan tester bu turda sınanmadı. EXE paketlenmedi.

## Test sonuçları

Son hedefli koşuda 22 test geçti. Genel keşifte 138 testten 132'si geçti, 6 koşulluydu. İki koşullu Tkinter testi ayrıca geçti. Bu turda dört koşullu uzun kariyer testi yeniden çalıştırılmadı. İlk genel koşuda iki eski test eşzamanlı bitiş bekliyordu. Olay döngüsünü bekleyecek şekilde uyarlandı. Kapanışta zamanlayıcı iptali de eklendi. Son genel koşuda hata yok.

main ve v0.8.7 EXE özeti korundu. Testlerde otomatik kayıt kapatıldı veya geçici kopya kullanıldı.
