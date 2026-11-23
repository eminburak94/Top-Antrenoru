# Windows Desktop Control hata teşhisi

**Sonuç — ÇÖZÜLEMEDİ.** Her iki masaüstü aracı da pencere envanterinden önce başarısız oldu. Aynı hata, grafik arayüz ve Node kullanmayan varsayılan sandbox kabuğunda da oluştu. Ortak başarısızlık noktası başlatıcının güvenlik ortamı oluşturma adımıdır. Bu adımın hangi girdiyle başarısız olduğu doğrulanamadı.

## 1. Ortam ve kullanılan araçlar

| Alan | Ölçüm |
|---|---|
| Windows | Windows 11 Home, sürüm `10.0.26200`, derleme `26200`, x64. |
| Kullanıcı oturumu | Salt okunur tanı kabuğu ve Explorer oturum 1'de. `UserInteractive=True`. WTS istemci protokolü `0`, yerel konsol. Bu ölçüm başarısız araç çekirdeğinin kendi oturumunu belirlemez. [Microsoft WTS oturum bilgisi](https://learn.microsoft.com/en-us/windows/win32/api/wtsapi32/ne-wtsapi32-wts_info_class) |
| Codex yürütme bağlamı | Windows üzerinde yönetilen workspace-write profili. Varsayılan sandbox kabuğu çalışmadı. Açıkça araç onayına sunulan salt okunur sorgular PowerShell `7.6.9` altında, yükseltilmemiş Windows belirteciyle çalıştı. |
| Çalışma dizini ve kökler | Kabuk proje çalışma alanından başlatıldı. İkinci yetkili çalışma alanı da varsayılan sandbox hatasını verdi. Tanı kabuğunda çalışma dizini, geçici dizin ve sistem Node yolu `C:\` altında ve erişilebilir. Başarısız çekirdeğin iç çalışma dizini ve sandbox sürücü eşlemeleri okunamadı. |
| Windows Computer Use | Kurulu paket `26.1117.41037`, `node_repl` ve `@oai/sky` giriş noktası. Beceri ve yönerge dosyaları mevcut. Belgelenen Windows Graphics Capture, UI Automation ve SendInput yetenekleri bu oturumda çalışırken doğrulanamadı. |
| Birleşik masaüstü aracı | `mcp__cua_repl`, pencere/uygulama envanteri için `cua.getState()`. Sayısal araç sürümü yayımlanan arayüzde görülmedi. Windows yüzeyi envanteri alınamadı. |
| Node | Kabukta bulunan sistem Node.js `v24.22.3`, x64, sürüm sorgusuna yanıt verdi. Araçların kendi çekirdek sürümü, bağımlılıkları ve etkin Windows izinleri, çekirdek kod çalıştırmadığı için doğrulanamadı. |

## 2. Hatanın yeniden üretimi

| Deneme | Sonuç |
|---|---|
| Basit `node_repl` hücresi, GUI paketi içe aktarılmadan | Çekirdek çıkış kodu `1`, `stdout_eof`, MXC güvenlik ortamı hatası. |
| Geçici REPL sıfırlamasından sonra basit metin çıktısı | Aynı hata. Oturum sıfırlaması sorunu gidermedi. |
| Birleşik araç ile `cua.getState()` | Pencere envanterinden önce aynı MXC hata satırı. |
| Varsayılan sandbox kabuğunda sabit metin yazdırma | Komut çalışmadan çıkış kodu `1` ve aynı MXC hatası. |
| Aynı kabuk deneyi ikinci izinli çalışma dizininde | Aynı hata. İlk proje dizinine özgü bir sonuç görülmedi. |

## 3. Hata günlükleri ve teknik kanıtlar

```text
MXC launcher: failed to create the process security environment:
CreateProcessSecurityEnvironment failed (HRESULT = 0x8007000F)
```

Araç çıktısında hatayı `stdout_eof` ve çekirdeğin çıkışı izledi. Windows'un `0x8007` türü hata kodunda düşük bölüm `0x000F`, Win32 `ERROR_INVALID_DRIVE` değerine karşılık gelir. Kod sürücüyle ilgili bir hata sınıfı gösteriyor. Hangi sürücünün veya hangi başlatma girdisinin buna neden olduğu günlükte yer almıyor. Çalışma dizini, depolama kökü ve sandbox süreç ortamı eşlemesi ayrı inceleme konuları. [Microsoft HRESULT açıklaması](https://learn.microsoft.com/en-us/windows/win32/com/error-handling-strategies) · [Win32 hata kodları](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-)

CodeIntegrity ve AppLocker EXE/DLL operasyon günlükleri etkin. Yaklaşık son 20 dakika ve kanal başına en fazla 120 olayla sınırlı sorguda araç adlarıyla eşleşen olay sayısı iki kanal için de sıfırdı. Bu tarama bir politika engelinin bulunmadığını kanıtlamaz. Ayrıntılı MXC başlatıcı izi, başarısız alt sürecin efektif çalışma dizini, yol girdisi veya güvenlik belirteci bu denemelerin çıktısında yoktu. Rapor yalnızca gerekli hata satırını ve deney sonuçlarını içerir.

## 4. Olası nedenler ve elenen hipotezler

| Hipotez | Destekleyen / sınırlayan kanıt | Güvenli doğrulama yöntemi ve sonuç |
|---|---|---|
| Ortak başlatma/güvenlik ortamı hatası | İki araç ve sade sandbox kabuğu aynı işlev adında ve kodda durdu. Onaylı tanı kabuğu çalıştı. | GUI bağımlılığı olmayan denemelerle **doğrulandı**. Ortak başarısızlık aşaması saptandı, kök girdi saptanmadı. |
| Belirli sürücü veya çalışma dizini eşlemesi | Win32 kodu sürücü sınıfına işaret ediyor. Görülebilen `C:\` kökü ve yollar erişilebilir, iki çalışma dizini aynı hatayı verdi. | Sağlayıcıdan güvenli iç tanı ile başarısız yol/eşleme türünü doğrulamak gerekir. **DOĞRULANAMADI.** |
| Oturum uyumsuzluğu | Tanı kabuğu ve Explorer aynı yerel konsol oturumunda. Çekirdek kendi oturumunu bildiremeden kapandı. | Başarılı başlatmadan sonra araç ve hedef süreç oturumu karşılaştırılabilir. Tanı kabuğu ile Explorer arasında uyumsuzluk görülmedi. Araç için **DOĞRULANAMADI.** |
| Görüntü veya girdi yetkisi | Ekran ve girdi çağrılarından önce hata var. | Başlangıç düzeldikten sonra seçili Not Defteri penceresinde görüntü, odak ve girdi ayrı sınanmalı. Gözlenen ilk hata olarak elendi. Daha sonraki yetkiler **DOĞRULANAMADI.** |
| Node veya paket bağımlılığı | Sistem Node yanıt verdi. Sade kabuk da başarısız oldu, GUI paketi yüklenmeden REPL öldü. | Araç sürümünü kendi çekirdeğinden kontrol etmek başlatma gerektiriyor. Node'a veya GUI paketine özgü hata ortak semptomu açıklamıyor. Araç çalışma zamanı **DOĞRULANAMADI.** |
| Bozuk veya uyumsuz kurulum | Paket ve yönerge dosyaları var. Varlık, bütünlük ve uyumluluk kanıtı sağlamıyor. | Sağlayıcının resmi bütünlük veya sürüm raporu gerekir. **DOĞRULANAMADI.** |
| Windows güvenlik politikası | Kısıtlı kanallarda eşleşme yok. Başlatıcı, güvenlik ortamı oluşturulurken hata veriyor. | Sağlayıcı ve Windows olayları zaman damgasıyla karşılaştırılmalı. Politika değiştirmek teşhis için gerekmedi. **DOĞRULANAMADI.** |
| Araç sağlayıcısının başlatma kusuru | Bağımsız giriş noktaları aynı MXC hata imzasını veriyor. | Sağlayıcının çağrı izi, kullanılan eşleme ve dönen altsistem hatası gerekir. Bir sağlayıcı kusuru olduğu **DOĞRULANAMADI.** |

## 5. Uygulanan güvenli işlemler

Salt okunur sistem, oturum, yol, sürüm ve olay sorguları yapıldı. REPL'in geçici durumu bir kez sıfırlandı. Yalın başlatma iki ayrı düzenekte sınandı. Onaylı kabuk yalnızca tanı ve rapor teslimi için kullanıldı. Bu kabuk üzerinden ayrı GUI otomasyonu kurulmadı. Windows ayarı, izin, güvenlik ilkesi, kayıt defteri veya kurulu paket değiştirilmedi ve uygulamalar zorla kapatılmadı.

## 6. Not Defteri doğrulama sonuçları

| Adım | Sonuç |
|---|---|
| 1. Aracı başlat | **Başarısız** · güvenlik ortamı oluşturulamadı. |
| 2. Pencereleri/ekranları listele | **Başarısız** · envanter isteği çekirdek açılışında durdu. |
| 3. Not Defteri penceresini tespit et | **Uygulanmadı** · hedeflenebilir pencere envanteri yok. |
| 4. Ekran görüntüsü al | **Uygulanmadı.** |
| 5. Görüntüde pencereyi doğrula | **Uygulanmadı.** |
| 6. Onayla odaklan | **Uygulanmadı.** |
| 7. Geçici metin yaz | **Uygulanmadı.** |
| 8. Metni ekranda doğrula | **Uygulanmadı.** |
| 9. Kaydetmeden bitir | **Uygulanmadı** · test belgesi açılmadı. |

## 7. Çözülemeyen engeller

Çekirdeğin güvenlik ortamı oluşturamaması nedeniyle doğrudan Windows görüntüsü ve girdi yeteneği kullanılamıyor. Resmî Microsoft WinApp UI, görünür hedef üzerinde görüntü ve girdi seçenekleri belgeliyor. `winapp` bu tanı kabuğunun komut yolunda bulunmadı, kurulum ve bu oturumdaki araç erişimi doğrulanamadı. Kullanıcı ekran görüntüsü paylaşırsa görüntü incelenebilir, ancak bu yerel fare/klavye kontrolünü doğrulamaz. [Microsoft WinApp UI otomasyonu](https://learn.microsoft.com/en-us/windows/apps/dev-tools/winapp-cli/ui-automation)

## 8. Kullanıcıdan gereken işlemler

Güvenli kullanıcı testi için, açık işlerini kaydettikten sonra Codex masaüstü uygulamasını normal kullanıcı olarak yeniden aç. Sonra Not Defteri'nde boş bir belge açıp test için odak ve geçici metin girişine izin ver. Bu yeniden açma henüz uygulanmadı ve kesin onarım olarak değerlendirilmemeli. Yalın başlatma aynı hatayı verirse destek ekibine derleme, paket sürümü, `HRESULT` satırı ve sade sandbox komutunda da tekrarlandığı bilgisi iletilebilir. Özellikle `CreateProcessSecurityEnvironment` çağrısına ulaşan sürücü eşlemesini veya çalışma dizini girdisini belirleyen güvenli tanı istenmeli.

## 9. Football Manager incelemesine dönülebilir mi?

**Hayır.** Önce Not Defteri'nde görüntü ve izinli giriş doğrulanmalı, ardından yeni oyun inceleme talimatı beklenmeli. Bu görevde Football Manager başlatılmadı, kapatılmadı veya incelenmedi.
