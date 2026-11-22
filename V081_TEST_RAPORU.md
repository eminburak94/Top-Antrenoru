# v0.8.1 test raporu

## Otomatik regresyon

Windows üzerinde `python -B -X utf8 -m unittest discover -q` ile 79 farklı senaryo bulundu. 73 geçti, 6 isteğe bağlı senaryo normal keşifte atlandı, 0 başarısız. Başlangıçtaki v0.8.0 keşfinde 66 senaryodan 60'ı geçmiş ve aynı altı senaryo atlanmıştı.

İlk geliştirme turunda değişen maliyet, personel havuzu ve iş piyasasına ilişkin 11 eski beklenti başarısız oldu. Eski model davranışını denetleyen vakaların girişleri o modeli açıkça seçecek şekilde güncellendi. Yeni davranışlar test_v081.py içinde ayrıca test edildi. İsteğe bağlı ilk eski GUI turunda sürüm başlığı v0.8.0 beklendiği için bir test başarısız oldu. Başlık beklentisi v0.8.1'e güncellendi ve test geçti. Yeni GUI akışının ilk denemesinde başlangıç kadrosu onayı açık kaldı. İkinci denemede otomasyon onay vererek akışı tamamladı.

- 13 yeni senaryo geçti. Bunlar iş başvurusu ve kulüp değişiklikleri, eski ve yeni kayıtlar, mali defter, kredi, personel, bütçe baskısı ve iki dilde gerçek Tkinter eylemlerini kapsıyor.
- Galatasaray başlangıçlı aşırı harcama senaryosu, oyuncu başına haftalık 30.000 ek maaşın nakit ve borç etkisini ölçtü. Bu, piyasada kendiliğinden gerçekleşen bir transfer zinciri değildi.
- Erzurumspor örneği, transfer alımı kapalı ilk sezon 34 haftayı tamamladı. Nakit pozitif kaldı ve açılış bakiyesi ile faaliyet defteri mutabık çıktı.
- 15 bağımsız kariyerde 195 sezon ve 59.670 lig maçı oynandı. İlgili kontrol noktalarında kayıt gidiş dönüşü yapıldı.
- Dört eski sürümden üretilen örnek kayıtların bir haftalık sonuçları karşılaştırıldı. Kullanıcıya ait kariyer dosyaları kullanılmadı.

## İsteğe bağlı eski regresyonlar

- v0.6.0 Tkinter ve altı 10 sezon koşusu geçti.
- v0.7.0 arayüz ve 25 sezon senaryosu geçti.
- v0.7.5 üç ayrı 50 sezon koşusu geçti.
- v0.7.6 iki 50 ve bir 100 sezon koşusunu tamamladı. Sezonluk defter mutabakatı ve kadro/maç kontrolleri geçti. Üç CSV yalnız geçici dizinde oluşturuldu.

Normal keşifte atlanan altı senaryo ayrı çalıştırmalarda başarıyla tamamlandı. Birleştirilmiş sonuç 79 farklı senaryo geçti, 0 başarısız, 0 atlandı.

## Yerel açılış

v0.8.0 yedeği ve v0.8.1 başlatıcılarından başlıkları eşleşen görünür Windows pencereleri açıldı. 960×600 otomasyon testinde TR ve EN iş başvurusu, hafta ilerletme, teklif kabulü, hızlı maç ve rapor adımları tamamlandı. İki dilde hem kulüple hem kulüpsüz başlangıç, 960×600 karşılama ekranındaki düğmelerle ayrıca tamamlandı. Önceki tester alfa, tarihsel veri ve 2D prototip geliştirme dışında kaldı. Kök dizindeki katalog, tarihsel giriş ve tarihsel skor dosyaları yedekle SHA-256 düzeyinde eşleşti.

İnsan tester, Python'sız temiz Windows kurulumu, yeni bağımsız EXE ve çoklu dilde uzun insan oyun oturumu doğrulanmadı.
