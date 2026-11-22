# 2D ve görsel kontrol

Görüntü match.capture ile gerçek saha durumlarını okur. Açık oyundaki hareket ve uçuş uçları korunur. Görsel ara kareler yeni pas, şut veya rastgelelik üretmez. Top sahibini artık kesin motor kimliği belirler. Eski maç modelinde eski görsel davranış sürer.

V085_EKRANLAR içinde dokuz gerçek Tkinter ekranı var. Menajer masası, maç başlangıcı, hücum, şut, maç sonrası, basit arama, gelişmiş arama, personel ve oyuncu profili. sut_kareleri altında aynı motor şutunun dört görüntüsü var. İlk görsellerde arama eylemleri dar pencerede tek satıra sığmayabiliyordu ve analiz panelinin kaydırması yetersizdi. Eylemler iki sıraya bölündü, analiz kaydırıldı ve maç olayları sözcük kaydırmalı hale geldi. Düzeltilmiş pencereler yeniden yakalandı.

Hız/duraklatma, pres, değişiklik, 2D/hızlı eşitlik ve saha sınırları otomatik test edildi. Gerçek kullanıcı ve fiziksel DPI matrisi henüz yok.
