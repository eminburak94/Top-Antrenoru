# Windows paketleme

PyInstaller 6.22.3 ile Windows x64 için onedir paket üretildi. Başlatıcı v0.8.2 TESTER BETA/Top Antrenoru/Top Antrenoru.exe. _internal klasörü EXE ile birlikte tutulur. Python 3.12 ve Tcl/Tk çalışma zamanını paket içerir. Üç oyun JSON dosyası kaynakla birebir eşleşti. CM/FM DAT dosyaları, eski yedekler ve kişisel kariyerler pakete dahil edilmedi.

Geliştirme bilgisayarındaki yerel Windows testinde PATH yalnız System32 ile sınırlandı, Python ve Tk ortam değişkenleri kaldırıldı, çalışma dizini ve LOCALAPPDATA geçici dizine taşındı. Gerçek pencere 0,27 saniyede göründü ve normal biçimde kapandı. Ayrı paket kontrolü 18 kulüp yükledi, bir haftada 9 maç simüle etti ve kaydı yeniden açtı. Paket 28.737.943 bayt. EXE SHA-256 375f962fefbf4e3eb81030e04127436d6b506cd505372c3c4c3ad0d4586df34c.

İlk paketleme denemesinde spec dizinindeki göreli veri yolları yanlış çözüldü. Tarif kaynak dizininden kurulan mutlak veri yollarıyla yeniden çalıştı. PAKETLE.bat aynı sürümde yenilenebilir tarif ve mevcut PyInstaller için TOP_ANTRENORU_BUILD_TOOLS değişkenini sağlar.

Temiz Windows donanımı, farklı Windows sürümleri ve imzalı dağıtım doğrulaması bu aşamada yapılmadı.
