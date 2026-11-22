# Atlas devir raporu · Top Antrenörü v0.8.6

1. **Ofsayt hesaplanıyor.** Model 3 pas anında topu, ikinci son rakibi ve yönü kontrol eder. Aktif pas bağlantısı kararı tetikler. 500 maçta 147 karar görüldü. Doğrudan taç, korner ve kale vuruşu istisnaları test edildi.
2. **Hakem motor kaynaklı.** 1.943 faul, 196 avantaj, 64 ikinci sarı ve 69 ihraç motor olaylarıdır. İhraç yerleşimi ve takım gücünü değiştirir. Faul frekansı yeniden kalibrasyon gerektiriyor.
3. **Korner gerçek pozisyon.** Taker, hedef ve savunma seçimi saha koordinatlarına yansır. Kafa, uzaklaştırma, pas veya ikinci top oluşabilir. 30. dakika kornerinden dört gerçek Tkinter karesi saklandı.
4. **Penaltı ve serbest vuruş işleniyor.** Doğrudan şut, teslim veya kısa seçenekleri, baraj, penaltı düzeni ve sonuç motor olaylarına bağlı. Penaltı ve baraj gerçek maçtan görüntülendi.
5. **Taç neden düşüktü?** Yanal pas hataları önceden saha içinde top kaybına dönüşüyordu. Yeni model yanal hatanın çizgiyi aşmasını işler. 6 → 137 kullanılan taç. Frekans hâlâ düşük.
6. **Denge.** Eşlenik 500 maçta gol 2,350 → 2,204, şut 11,950 → 11,966, kurtarış 979 → 1.106. Güçlü takım eşitsiz 268 maçta 156 → 162 kazandı. Pas seçiminin erken fazla ofsayt üretmesi savunma hattıyla düzeltildi.
7. **Roller.** Sekiz rol boş alana kaçma, pas seçeneği olma, çizgi genişliği, savunma önü ve baskıya yaklaşma gibi konum kararlarını etkiler.
8. **2D.** Canvas köşe bayrakları, küçük hakem, gerçek ofsayt işareti, korner kullanıcısı, baraj ve penaltı yerleşimi. Sekiz gerçek ekran görüntüsü mevcut.
9. **Kayıtlar.** Kayıt şeması korunuyor. Model 1 ve 2 bir haftalık eşleşmeyi geçti. Önceki motorlar ve ekonomi işaretleri yüklenirken korunuyor. Yeni kişisel kayıt yeri sürüme özel.
10. **Testler.** 119 başarılı otomatik test, 17 kariyerde 345 sezon, 105.570 maç. En uzun kariyer 100 sezon. Paket açıldı ve izole kayıt yeniden yüklendi.
11. **Performans.** Ölçüm döngüsünde Model 2 4,50 ms, Model 3 6,04 ms/maç. Sezon/RAM ayrıntıları V086_PERFORMANS.md dosyasında.
12. **Ertelenenler.** Tam hakem kural kapsamı, daha ayrıntılı ofsayt etkileşimleri, tarihsel olay frekansı doğrulaması ve özgün ses varlıkları. İnsan tester ve temiz Windows onayı bekliyor.

Windows paketi v0.8.6 TESTER BETA altındaki Top Antrenoru klasöründe. Tester'a klasörün tamamı gerekir. Top Antrenoru.exe gerçek açılış ve kayıt testini bu Windows makinesinde geçti. Genel Beta onayı verilmedi.
