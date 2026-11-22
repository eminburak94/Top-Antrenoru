# Performans

Windows geliştirme bilgisayarı, aynı Python ve 2000/01 katalog. Eş 500 maçlık tanı döngüsü (kaleci konum denetimi dahil) Model 2: 4,50 ms/maç, Model 3: 6,04 ms/maç; yaklaşık %34 daha uzun. Tkinter çizimi bu ölçüme dahil değildir.

| Test | Kümülatif süre | Windows çalışma kümesi | Zirve çalışma kümesi | Kayıt |
|---|---:|---:|---:|---:|
| Model 2 kariyer başlatma | 0,007 sn | 28,3 MB | 29,0 MB | — |
| Model 2 sezon 1 | 1,66 sn | 36,0 MB | 36,0 MB | 1,56 MB |
| Model 3 kariyer başlatma | 0,006 sn | 37,7 MB | 42,8 MB | — |
| Model 3 sezon 1 | 2,58 sn | 39,1 MB | 42,8 MB | 1,74 MB |
| Model 3 sezon 10 | 33,02 sn | 41,2 MB | 44,4 MB | 3,02 MB |
| Model 3 sezon 25 | 75,48 sn | 47,2 MB | 50,6 MB | 4,79 MB |
| Model 3 sezon 50 | 141,14 sn | 57,0 MB | 61,9 MB | 7,59 MB |

Sezon denemesi aynı Galatasaray tohumu 813 ve aynı süreçten iki motor sırasıyla çalıştırılarak yapıldı. Bu nedenle ikinci başlatma RAM'i önbellek ve önceki tahsisleri içerir. Uzun matris aynı anda çalıştığından duvar saati karşılaştırmaları makine yüküne duyarlıdır. Başlatma satırları Python içindeki kariyer oluşturma süresini ölçer. Windows EXE soğuk açılış süresi ölçülmedi.

Model 3 100 sezonluk Erzurumspor kariyerinde kayıt 13,23 MB. Windows paket klasörü 28.825.490 bayt. Canlı görüntü karesi motorun son dakika verisiyle üretilir; hızlı hesaplama koordinatları diskte saklamaz. Farklı donanımlarda çizim kare hızı henüz ölçülmedi.

Ham ölçüm: .build/performans.jsonl.
