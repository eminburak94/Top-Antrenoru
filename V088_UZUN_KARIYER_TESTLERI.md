# v0.8.8 uzun kariyer denetimi

Model 4 ile üç bağımsız kariyer çalıştı. Toplam 175 sezon, 5.950 hafta ve 53.550 lig maçı. Her sezonda 34 hafta, 306 karşılaşma, 18 takım için puan tablosu ve kadro tekilliği denetlendi. Beş kontrol noktasında sezon sonu dosyası önce kaydedilip yeniden açıldı, sonra sezon geçişi ve yeni sezon kaydı sınandı. Süre sınırı olan süreçler başarıyla sonlandı.

| Başlangıç / tohum | Sezon | Son kulüp | Süre* | Yavaş hafta* | Son kayıt | Süreç RAM zirvesi |
|---|---:|---|---:|---:|---:|---:|
| Galatasaray / 88025 | 25 | Bursaspor | 85,98 sn | 0,262 sn | 4,89 MB | 101,2 MB |
| Gençlerbirliği / 88050 | 50 | Gençlerbirliği | 176,00 sn | 0,273 sn | 7,78 MB | 139,5 MB |
| Kulüpsüz, Erzurumspor başlangıç bağlamı / 88100 | 100 | Adanaspor | 336,00 sn | 0,274 sn | 13,64 MB | 212,8 MB |

*Süreler paralel koşuda, son sezon devri ve son ikinci disk yazımı öncesinde kaydedildi. Yavaş hafta yalnızca maç haftası işlemesini ölçer. RAM zirvesi kayıt doğrulaması ve JSON kopyalarını da içerir. Ölçümler Tkinter ve EXE açılış performansını kapsamaz.

| Sezon hedefi | Bedelli / serbest transfer | Toplam ücret bedeli | Emeklilik / üretilen genç | Sözleşme bitişi / aktif | Başvuru / işe alınma / görevden alma |
|---:|---:|---:|---:|---:|---:|
| 25 | 89 / 541 | 45.600.205 | 885 / 1.120 | 1.558 / 351 | 12 / 5 / 5 |
| 50 | 147 / 1.347 | 76.366.360 | 2.002 / 2.239 | 3.358 / 344 | 12 / 6 / 6 |
| 100 | 295 / 2.408 | 166.256.546 | 4.633 / 5.091 | 7.182 / 351 | 23 / 12 / 11 |

Bonservisler oyun baz biriminde. Transfer, sözleşme bitişi, genç ve emeklilik sayıları birikimli. Aktif sözleşmeler son kesitteki sayıdır. Test politikası menajer kulüpsüzken eldeki işlere başvurdu ve uygun ilk teklifi kabul etti. 25 sezonluk koşuda iki reddedilme görüldü. Farklı başvuru stratejilerinin dengesi ölçülmedi.

Sezon sonu medyan kasa 6,94 / 7,87 / 8,26 milyon. 100 sezonluk aynı kariyerde medyan kasa 25, 50 ve 100. sezonlarda sırasıyla 7,00 / 7,71 / 8,26 milyon. Haftalık örneklerde negatif kasa ve borç görülmedi. Tüm kariyerlerin sezon sonu dip kadroları sırasıyla 16 / 17 / 17. 100 sezonluk koşuda en yüksek tekil kulüp kasası 28,18 milyon. Bu örneklemde finansal çöküş ya da kontrolsüz kasa sıçraması görülmedi. Kriz ve iflas mekaniklerinin yeterince çalıştığı bu senaryolardan çıkarılamaz.

Sezon geçişlerinde takılma ve kontrol noktalarında veri kaybı görülmedi. Uzun vadede arşiv, disk ve tepe bellek büyümesi sürüyor. Üç tohumdan her kariyere genellenemez. Ham ölçümler yerelde .build/v088-long-25.json, .build/v088-long-50.json ve .build/v088-long-100.json. Yeniden üretim: kariyer_denetim_v088.py, kulüp indeksi 0/1/2, yukarıdaki tohum ve ilgili sezon sınırı.
