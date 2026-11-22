# Kayıt uyumluluğu

v0.7.9.1, v0.7.9.2, v0.7.9.3 ve v0.8.0 yedeklerinin koduyla örnek kariyerler üretildi. Yeni sürümde bu örnekler yüklenip bir hafta ilerletildi. Sonuçlar, fikstürden türetilen tablo, finans, oyuncu sahipliği, personel ve RNG durumu eski çalıştırmanın sonucu ile aynıydı.

Kayıt şeması 3, isteğe bağlı sürümlü menajer durumu ve ekonomi model işareti alır. Eski kayıtlarda bu işaretler kendiliğinden eklenmez. Yeni başlatılan kariyerlerde başvuru ve kişisel görev geçmişi saklanır. Kulüpsüz kayıt geçici dizinde yazılıp iki kez okunarak aynı hafta sonucuna ulaştı. Kesik JSON güvenli biçimde reddedildi. Mevcut atomik yazma ve yedek davranışı regresyon paketinde çalıştırıldı. Kişisel kariyer dosyaları test girişi olarak kullanılmadı. Yeni kayıtların eski çalıştırıcıda açılması destek kapsamı dışındadır.
