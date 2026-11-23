# FM 2005 — Bağımsız arka plan otomasyonu

**Karar — DOĞRULANAMADI.** Bu bilgisayarda, mevcut koşullarla FM 2005'in hem görüntüsünü alıp hem de kullanıcı oturumunun odağına, imlecine ve fiziksel girişlerine dokunmadan oyuna komut gönderen bir yöntem doğrulanmadı. Açık bir `fm2005` süreci salt okunur sorguda bulundu. Bu çalışmada oyuna mesaj veya giriş gönderilmedi, ekran yakalama çağrısı yapılmadı ve pencere durumu değiştirilmedi.

## 1. Kullanıcının aktif masaüstüne dokunmadan yapılabilecekler

- **İşlem ve pencere meta verisi.** Kurulu EXE ve çalışan süreç, pencere başlığı, oturum numarası ve yanıt durumu gibi bilgiler salt okunur sorgulanabilir. Bu bilgi pencere içeriğini, menüleri veya giriş uygunluğunu göstermez.
- **Görüntü yakalama adayı.** Windows Graphics Capture'ın `CreateForWindow` çağrısı tek bir pencere tanıtıcısını hedefler. Kurulu Computer Use belgeleri pencere başka bir pencereyle örtülüyken görüntü alabilen bir arka uç tarif ediyor. FM 2005 için önceki canlı incelemede güvenilir oyun görüntüsü pencere öne getirildikten sonra alındı. Bir önceki testte simge durumundaki pencere için araç görüntü alamayıp etkinleştirme istedi. Bu nedenle FM 2005'te örtülü pencere, simge durumu ve sürekli güncellenen karelerin her biri açık bir doğrulama kalemidir. Ekrana düşen başka pencere, siyah görüntü veya eski kare kabul edilmemelidir. Görüntü yolu yalnızca hedef pencereyi okuyabilen ve odağı değiştiren geri dönüş kapalı olan bir arka uçla ele alınabilir. [Microsoft pencere yakalama API'si](https://learn.microsoft.com/en-us/windows/win32/api/windows.graphics.capture.interop/nf-windows-graphics-capture-interop-igraphicscaptureiteminterop-createforwindow) · [Önceki uygulamalı inceleme](V093_FM2005_GERCEK_OYNANIS_INCELEMESI.md)
- **Önceden alınmış görüntülerin analizi.** Kullanıcının sağladığı veya önceki izinli incelemede alınan oyun kareleri incelenebilir. Bu yöntem canlı oyuna yeni karar göndermez ve kullanıcı masaüstüyle eşzamanlı kontrol gerektirmez.

## 2. Teknik olarak mümkün olabilecek fakat henüz doğrulanmamış yöntemler

| Yöntem | Ne sağlayabilir | FM 2005 için kanıt ve sınır |
|---|---|---|
| HWND hedefli Windows Graphics Capture | Oyun penceresinden kare akışı | Yakalama girdi sağlamaz. Kapalı, simge durumundaki ya da kare üretmeyi durduran oyun için yeni görüntü garantisi yok. Önceki araç gözlemi simge durumunda etkinleştirme gerektirdi. [Microsoft CreateForWindow](https://learn.microsoft.com/en-us/windows/win32/api/windows.graphics.capture.interop/nf-windows-graphics-capture-interop-igraphicscaptureiteminterop-createforwindow) |
| `PrintWindow` | Alternatif pencere görüntüsü | Hedef süreç çizime katılır ve çağrı eşzamanlıdır. Eski oyunun çizim yüzeyinin tam ve güncel dönmesi belirsiz. Kaynak görüntü başka bir pencere olursa ya da hedefin yanıtı gecikirse canlı kontrol için kullanılamaz. [Microsoft PrintWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-printwindow) |
| `PostMessage` ile pencereye özel giriş | Hedef HWND kuyruğuna fare veya tuş mesajı bırakabilir | Kuyruğa eklenmesi oyunun kabul ettiğini göstermez. Menü özel çizim, aktif pencere durumu veya gerçek tuş/fare durumu bekleyebilir. Sürükleme, modal pencere ve metin girişi ayrı sınanmalı. Belgelenen UIPI sınırları geçerli. Hiçbir mesaj gönderilmedi. [Microsoft PostMessage](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postmessagew) |
| UI Automation eylem desenleri | Uygulama erişilebilir öğe yayımlarsa ilgili düğmeyi koordinat veya global giriş olmadan çağırabilir | FM menülerinin kullanılabilir UIA öğeleri sunduğuna dair doğrulanmış envanter yok. Microsoft WinApp dokümantasyonu bazı UIA desenlerini ve giriş modlarını ayrı tutuyor. Kurulum taramasında `winapp` komut yolu üzerinde bulunmadı. Bir sarmalayıcının odaklama davranışı ayrıca doğrulanmalı. [Microsoft UI Automation CLI](https://learn.microsoft.com/en-us/windows/apps/dev-tools/winapp-cli/ui-automation) |
| FM'e özel otomasyon | Oyunun yayımlanmış bir arayüzü varsa doğrudan bir komut köprüsü | Gözden geçirilen kurulum belgeleri envanterinde canlı maç/menü API'si saptanmadı. Veri editörü belgesinin varlığı canlı kontrol kanıtı sayılmaz. Kaynak veya ikili dosya içeriği bu amaçla ayrıştırılmadı. |
| Kurulu araçla `SendInput` | Önceki incelemede doğrulanan etkileşimli oynanış | Girdiyi sistem akışına ekler. Önceki başarılı kullanımda oyun öne getirildi ve tıklamalar etkin pencerede yapıldı. Bu yol eşzamanlı bağımsız kontrol koşulunu karşılamıyor. [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput) |

**Doğrulama eşiği.** Uygulanabilirlik kararı için aynı oturumda FM 2005 odağı almadan üç koşul birlikte gözlenmeli. Hedefe ait güncel kareler gelmeli, ayrı bir izinli testte komut beklenen oyun durumunu değiştirmeli, kullanıcının ön plan penceresi ve imleci aynı kalmalı. Basit menü eylemi geçse bile maç duraklatma, modal ekran ve kadro değişimi ayrıca kanıt ister. Mevcut kanıt, bu oturumda böyle bir giriş denemesi yapmak için yeterli görülmedi.

## 3. Bağımsız çalışma için en düşük disk alanı ve ek yazılımlar

| Kapsam | En düşük ek alan / yazılım | Durum |
|---|---|---|
| Salt okunur süreç bilgisi ve mevcut kareleri inceleme | **0 MB ek kurulum.** Mevcut Windows ve mevcut inceleme aracı yeterli. | Süreç sorgusu doğrulandı. |
| Pencereye özel, bellekte görüntü alma | **0 MB ek kurulum mümkün.** Windows'un yerleşik API'si ve kurulu aracın uygun yakalama yolu kullanılabilir. Görüntü dosyaya yazılmadığında kalıcı medya alanı gerekmez. | Bu FM 2005 oturumunda arka plan görüntüsü doğrulanmadı. |
| Pencereye özel giriş ve doğrulama | Yerleşik mesaj/UIA API'leri ek paket gerektirmez, ancak onları güvenli biçimde çağıran ve odağı değiştirmeyen çalışan bir istemci gerekir. Mevcut istemciyle bağımsız uçtan uca yol kanıtlanmadığından **doğrulanmış asgari disk alanı veya ek yazılım listesi yok**. | Araç yüklenmedi. Paket ya da çalışma zamanı boyutu ölçülmedi. |

Sanal makine, ikinci Windows ve büyük indirme bu araştırmanın kapsamı dışında kaldı. **Nihai karar — Bu bilgisayarda mevcut koşullarla FM 2005'in bağımsız arka plan kontrolü doğrulanamıyor.** Pencereye özel görüntü alma teknik bir aday. Oyunun arka planda girdi kabul etmesi ve kullanıcı girişinden yalıtılması kanıtlanmadı.
