# 2D maç mimarisi

Maç motoru, beş dakikalık aralıklarda güce, enerjiye, takım yaklaşımına ve konumsal katsayılara göre hücumları çözer. Konumsal katman hücumun ilerleme derinliği, genişliği ve rakip baskısını şut sıklığına, bazı şut açılarına ve bitiriş gücüne bağlar. Hareket, aynı hücumun konumları ve pass, shot/goal olaylarından çıkar. Pasör ve şutör motorun gerçek olay kimlikleridir. Top yolunda aradaki kareler doğrusal hesaplanır. Boşa çıkan hücumu motor kaydeder ve tüm maç gösteriminde geri dönen top yolu çizer.

Maç sonucu, skor ve oyuncu dakikaları Match üzerinden bir kez işlenir. Canvas karelerini yalnız izlenen maç için hesaplar. Kısa kare kuyruğunu Tkinter after ile işler. İzleme rastgelelik kullanmaz. Eski kayıtların maç modeli bayrağı kendiliğinden eklenmez. Şema 3 korunur. Model 1, kariyer başında açıkça açılır. Canlı maç ortası kayıt desteği yoktur. Maç tamamlanınca taktik kararların ve 18 dönemin özeti yalnız son raporda tutulur.

Bu ilk konumsal katman yaklaşık takım yerleşimi üretir. 22 bağımsız oyuncunun kesintisiz fizik simülasyonu, tam maçta her pasın dökümü veya gerçek zamanlı mevki izleme sistemi henüz yok.
