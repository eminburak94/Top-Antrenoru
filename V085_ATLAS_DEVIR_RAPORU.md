# Atlas devir raporu · Top Antrenörü v0.8.5

1. **Motor değişti.** Yeni kariyerler beş dakikalık eski hücum zarları yerine model 2'nin bir dakikalık saha durumunu kullanır.
2. **Konumlar simülasyona ait.** Saha durumu 22 oyuncu, top, sahiplik ve yeniden başlama bilgisi taşır. Oyuncu hareketlerini saha motoru hesaplar.
3. **Pas zincirleri gerçek.** Oyuncular arası pas, kayıp, top sürme ve şut model olaylarıdır. Hedef, mesafe, baskı ve taktik pas kararına girer.
4. **Taktik hareketi etkiler.** Pres yaklaşmayı ve yükü, tempo ve genişlik yerleşimi veya kararları değiştirir. AI yaklaşımı ve yorgunluk değişimi yapabilir.
5. **Hızlı, metin ve 2D eşdeğerliği geçti.** Aynı karar ve RNG ile tam sonuç eşleşti. Ara kare hesabı RNG tüketmedi.
6. **Eski kariyer korunuyor.** v0.8.4 model 1 örneğinin bir haftalık JSON sonucu birebir üretildi. Tarihsel katalog, kayıt şeması ve eski ekonomi bayrakları korunur.
7. **Menajer masası değişti.** Altı işlevsel kartta sonraki maç, takım, yapılacaklar, gelişmeler, mali durum ve antrenman var.
8. **Arama sadeleştirildi.** Gelişmiş filtreler açılır panelde, aktif gizli filtre sayısı düğmede. Uygulama otomasyonu sol bek aradı, gözlem istedi ve gerçek teklif verdi.
9. **Ertelenenler.** Kesintisiz saniyelik fizik, tam faul/ofsayt/duran top taktikleri, canlı diziliş, maç ortası kayıt ve insan tester. Şut sayısı ve güçlü takım farkı izlenmeli.
10. **Test.** 110 otomatik test geçti. İlk metin, yerleşim ve test seçici sorunları yeniden test edildi. Son 17 kariyer koşusunda 345 sezon ve 105.570 maç. Kalibrasyonda her modelde 500 maç.
11. **Windows.** Yerel kaynak başlatıcı ve bağımsız x64 paketi açıldı. Yeni model, arama, kare üretimi, kayıt ve yükleme doğrulandı. Genel Beta bekliyor.
12. **İnsan testinde.** Hücum ve topun izlenebilirliği, hızın konforu, pres ve oyuncu değişikliğinin okunması, güçlü takım avantajı, şut sıklığı ve transfer/teknik ekip iş akışı değerlendirilmeli.

## Dosyalar ve görüntüler

Ana değişiklikler saha_motoru.py, mac.py, istatistik.py, kariyer.py, kayit.py, mac_gorunum.py, arayuz.py, arama_bilesenleri.py, ise_alim_ui.py, tema.py, oyun.py, BASLAT.bat ve PAKETLE.bat. Yeni otomasyon test_v085.py, mac_kalibrasyonu_v085.py, kalibrasyon_v085.py, gorsel_kontrol_v085.py. Eski GUI bağlayıcı testleri test_v060.py, test_v0791.py ve test_v084.py yeni etiket ve denetimlere uyarlanmıştır.

V085_EKRANLAR altındaki dokuz PNG gerçek Tkinter pencerelerinden. Aynı şutun dört karesi sut_kareleri altındadır. V085_MAC_KALIBRASYONU.json ve V085_KARIYER_NIHAI.csv ham kanıttır.
