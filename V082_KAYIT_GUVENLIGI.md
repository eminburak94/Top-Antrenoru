# Kayıt güvenliği

Şema 3 aynı kaldı. Ekonomi bayrağı kayıt üzerinde korunur. Bayrak bulunmayan kayıtlar eski hesapları, 1 işaretli v0.8.1 kayıtları v0.8.1 ekonomisini kullanır. Yalnızca yeni kariyerler model 2 başlatır. Eski sürümlerden üretilen örnekler yalıtılmış koşullarda açıldı. v0.8.1'den alınmış örnek ilk haftayı JSON düzeyinde birebir yeniden üretti.

Yeni genele yazma dizini %LOCALAPPDATA%/TopAntrenoru/v0.8.2. Eski kişisel kayıtlar yerinde kalır. Yükleme diyalogunda önceki dizin kullanılabilir. Geçerli önceki kayıt ayrı bir yedeğe alınır. Yeni içerik aynı dizinde geçici dosyaya yazılır ve değiştirme işlemi atomiktir. Son değiştirme sırasında OSError enjekte edildiğinde önceki dosya ve yedeğin byte içeriği korundu. Geçici dosya temizlendi. Bozuk kayıt reddedildi ve sonraki kayıt sağlam yedeği korudu. Fiziksel güç kesintisi veya arızalı depolama aygıtı üzerinde test yapılmadı.
