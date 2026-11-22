# AI finans sonuçları

Galatasaray başlangıcı, tohum 811, her sürümde 25 sezon. Ölçümler oyun içi hesap biriminde ve sezon sonu ödülleri öncesinde. Aynı başlangıç tohumu kullanıldı; işe alım ve transferler değiştikçe maç dizilerinin ayrışması beklenir.

| Sürüm | Sezon | AI medyan nakit | Negatif nakitli AI | Toplam AI borcu | Personelsiz AI |
|---|---:|---:|---:|---:|---:|
| 0.8.0 | 5 | 191073 | 2 | 8415210 | 1 |
| 0.8.0 | 10 | -10792 | 12 | 8312693 | 0 |
| 0.8.0 | 25 | 255964 | 4 | 4907290 | 0 |
| 0.8.1 | 5 | 1982331 | 0 | 0 | 0 |
| 0.8.1 | 10 | 3530683 | 0 | 0 | 0 |
| 0.8.1 | 25 | 4319189 | 0 | 0 | 0 |

Nihai 15 kariyer matrisi V081_UZUN_KARIYER_TESTLERI.md dosyasındadır.

## İlk deneme · Personel toparlanma istisnası eklenmeden önce


Üç kulüp / güç sınıfı × beş tohum (811–815). Her koşu 10 sezon, tohum 811 için 25. Her sezon 306 maç. Bu ilk denemede kayıt gidiş dönüşü 10 ve 25. sezon kontrol noktalarında yapıldı. Ölçüm ödül öncesi. AI, görevdeyken kullanıcı kulübü dışındaki kulüpler.

| Kulüp | Tohum | Sezon | AI medyan nakit | AI negatif kulüp | AI toplam borç | AI personelsiz |
|---|---:|---:|---:|---:|---:|---:|
| GALATASARAY | 811 | 10 | 3326599 | 0 | 0 | 5 |
| GALATASARAY | 811 | 25 | 4233091 | 0 | 0 | 2 |
| GALATASARAY | 812 | 10 | 3335281 | 0 | 0 | 6 |
| GALATASARAY | 813 | 10 | 3691010 | 0 | 0 | 6 |
| GALATASARAY | 814 | 10 | 3390783 | 0 | 0 | 5 |
| GALATASARAY | 815 | 10 | 3501000 | 0 | 0 | 6 |
| GENÇLERBİRLİĞİ | 811 | 10 | 3395680 | 0 | 0 | 6 |
| GENÇLERBİRLİĞİ | 811 | 25 | 4324770 | 0 | 0 | 3 |
| GENÇLERBİRLİĞİ | 812 | 10 | 3441019 | 0 | 0 | 5 |
| GENÇLERBİRLİĞİ | 813 | 10 | 3503048 | 0 | 0 | 6 |
| GENÇLERBİRLİĞİ | 814 | 10 | 3170372 | 0 | 0 | 6 |
| GENÇLERBİRLİĞİ | 815 | 10 | 3431366 | 0 | 0 | 5 |
| ERZURUMSPOR | 811 | 10 | 3403009 | 0 | 0 | 5 |
| ERZURUMSPOR | 811 | 25 | 4261047 | 0 | 0 | 3 |
| ERZURUMSPOR | 812 | 10 | 3292045 | 0 | 0 | 5 |
| ERZURUMSPOR | 813 | 10 | 3725932 | 0 | 0 | 3 |
| ERZURUMSPOR | 814 | 10 | 3413003 | 0 | 0 | 6 |
| ERZURUMSPOR | 815 | 10 | 3474586 | 0 | 0 | 5 |

Toplam 195 sezon ve 59670 lig maçı. Tüm kariyerler bellekte.

## 10 sezonluk piyasa kesiti · Galatasaray 811

| Sürüm | Defter toplam bonservis | Toplam imza parası | Transfer geçmişi satırı |
|---|---:|---:|---:|
| 0.8.0 | 54559885 | 3985100 | 182 |
| 0.8.1 | 32348308 | 2578750 | 224 |

Defter toplamı her sezon ödül öncesi ölçüldü. Geçmiş satırları transfer kaydındaki işlemleri sayar; bonservisli ve bonservissiz işlemleri tek başına ayırmaz.
