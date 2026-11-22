# Transfer dengesi

v0.8.2'de satın alma sayısı, satış eşiği ve serbest oyuncu maliyet üstünlüğü birlikte piyasayı daralttı. v0.8.3 gerçek mevki açığında ikinci bonservisli alıma izin veriyor. AI satıcı daha geniş yedek havuzunu değerlendiriyor ve gerçekleşen her satıştan önce güncel mevki tabanını tekrar kontrol ediyor. Bütçe, ilk kadro oyuncularını koruma, aynı sezonda yeniden satmama ve satıcı tarama sınırı sürüyor. Sonuçlar, ayarların ayrı ayrı nedensel etkisini ölçen faktöriyel test değildir.

| Sürüm | Galatasaray 811 sezonu | Bonservisli | Bedelsiz | Bedelsiz payı | Toplam bonservis | Medyan bedel | Mevki açığı |
|---|---:|---:|---:|---:|---:|---:|---:|
| 082 | 10 | 15 | 177 | 92.2% | 11.878.121 | 728.204 | 0 |
| 083 | 10 | 14 | 187 | 93.0% | 8.289.100 | 581.633 | 0 |
| 082 | 25 | 60 | 573 | 90.5% | 31.192.136 | 456.766 | 0 |
| 083 | 25 | 82 | 603 | 88.0% | 38.917.592 | 417.218 | 0 |


| Sürüm | Sezon noktası | Koşu | Medyan bonservisli işlem | Medyan bedelsiz payı | Medyan toplam bonservis |
|---|---:|---:|---:|---:|---:|
| 082 | 10 | 15 | 15 | 93.1% | 11.301.603 |
| 083 | 10 | 15 | 18 | 91.6% | 11.134.350 |
| 082 | 25 | 3 | 75 | 88.5% | 36.175.505 |
| 083 | 25 | 3 | 97 | 86.0% | 39.777.244 |

Transfer hacmi kulübe ve süreye göre değişti. Galatasaray 10. sezon kesitindeki işlem sayısı önceki sürümü aşmadı. 25. sezon örnekleri daha fazla bonservisli alım gösterdi. Piyasa hâlâ bedelsiz ağırlıklı.
