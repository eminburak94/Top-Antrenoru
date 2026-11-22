# v0.8.8 kayıt güvenliği

## Uyumluluk

Kayıt şeması 3 ve maç modeli alanı korundu. v0.8.6 kaynak klasörü salt okunur çalıştırıldı. v0.8.7 kaynakları main commit'i 4317e9d'den geçici dizine çıkarıldı. Kişisel kayıt kullanılmadı.

| Kaynak | Şema | Maç modelleri | Sonuç |
|---|---:|---|---|
| v0.8.6 | 3 | 1, 2, 3 | 3/3 |
| v0.8.7 | 3 | 1, 2, 3, 4 | 4/4 |

Her kombinasyonda özgün dosya SHA-256 ile korundu. Aynı kariyer ayrı hedefe yeniden kaydedildi, kaynak sürümün okuyucusu bu kopyayı açtı. Geliştirme dalında özgün ve kopya kariyer bir hafta aynı RNG durumundan ilerletildi ve sonuçları eşleşti. İzole hedefe ikinci kayıt haftayı ilerletti, yedek önceki haftada kaldı. Model 4'ün önceki sürümle gelecekte aynı maç sonucunu vermesi beklenmiyor. Burada format uyumu ve güncel okuyucuda deterministik devam sınandı.

## Doğrulanmış hata

Ana dosya yedeklenirken UTF-8 hataları yerine geçici karakter konabiliyordu. Hasar menajer adı gibi bir metin alanına denk geldiğinde JSON ve şema bunu kabul edip sağlam yedeği hasarlı içerikle değiştirebiliyordu. Yedek adayı artık sıkı UTF-8 okumasından ve kayıt doğrulamasından geçmek zorunda. Geçersiz ana dosya mevcut sağlam yedeğin yerine alınmıyor. Kilitli hedefi canlandıran ayrı testte atomik yazma başarısız olunca ana dosya korunuyor ve geçici dosya kalmıyor.

Kişisel kariyerler, mevcut kayıt klasörü ve kayıt şeması değiştirilmedi. Ham uyumluluk kanıtı yerelde .build/v088-save-compat.json.
