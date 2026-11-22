# v0.8.4 motor ön analizi

1. Mevki eşleşmesi, futbolcu özellikleri, grup gücü, takım yaklaşımı ve kadro sayısı şut olasılığını etkiliyor. Bitiricilik, savunma ve kaleci gücü gol olasılığını belirliyor.
2. Match.step beş dakika ilerliyor. Her iki taraf o aralıkta birer hücum denemesi yapabiliyor. Dakikalar, disiplin ve analiz bu aralıkta işleniyor.
3. Konumsal modelde hücum derinliği, genişlik ve baskı sayısal katsayılar. Oyuncu koordinatları kalıcı maç durumu değil. Görsel kareler diziliş ve hücum yolundan kuruluyor.
4. Kalıcı top sahibi ya da pas içinde bekleyen top durumu yok.
5. Şutör ve varsa son pasör gerçek oyuncu kimliklerine bağlı. Kayıt düzenli pas zinciri taşımıyor.
6. Rakip orta saha ve savunma gücü, pres ve enerji şut denemesine/bitirişe oran olarak giriyor. Özel bir savunmacının alan takibi yok.
7. Finishing, Passing, kaleci ve mevki seçimi grup ve olay hesaplarına giriyor.
8. Takım yaklaşımı, pres, tempo, genişlik ve değişiklik sonraki adımın gücünü ve enerji kaybını etkiliyor.
9. Canlı ve hızlı mod Match çekirdeğini paylaşıyor. Capture yalnız kare arabelleği.
10. Ana maç RNG'si şut eşiği, şutör ve golü kullanıyor. Ayrı detail RNG pasör/isabeti, ayrı card RNG kartları, kariyer RNG haftalık fikstür tohumlarını belirliyor. Canvas RNG kullanmıyor.

Yeni motor model 2 ile ayrılacak. Model 0 ve 1 kendi hesaplarına devam edecek.
