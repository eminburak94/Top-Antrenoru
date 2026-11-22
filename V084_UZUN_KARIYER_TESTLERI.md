# Uzun kariyer testleri

Üç kulüp seviyesi, beş tohum, 15 eşleşen 10 sezon koşusu, üç 25 sezon kesiti ve ayrıca 50/100 sezonluk kariyerler. 17 kariyer, 345 sezon ve 105.570 maç tamamlandı. 25 kontrol noktasında süre alanı çıkarıldığında v0.8.3 ham sonuçlarının tamamı byte düzeyinde aynı alan değerlerine sahip. Eski matris koşucusunun 083 sürüm etiketi aynı maç/ekonomi modelini temsil etmek için korundu.

| Kulüp | Sezon | Nakit medyanı | Borç | Aktif oyuncu | Minimum kadro | Kayıt bayt | Süre sn |
|---|---:|---:|---:|---:|---:|---:|---:|
| GALATASARAY | 50 | 7562353 | 0 | 348 | 19 | 6466303 | 53.87 |
| ERZURUMSPOR | 50 | 7909900 | 0 | 350 | 18 | 6425173 | 52.27 |
| ERZURUMSPOR | 100 | 7994068 | 0 | 349 | 19 | 11956612 | 104.29 |

Ekonomi, maaş payı, bonservisli/bedelsiz ve derinlik değerleri V084_KARIYER.csv içinde. Çalıştırılan kariyerler kullanıcı arama tercihleri ve gözlem siparişi olmadan simüle edildi. Bunlar ayrı regresyonlarda tamamlandı. Duvar süreleri farklı VM yüklerinden etkilenebilir. Doğrudan v0.8.3 hız üstünlüğü iddiası yok.
