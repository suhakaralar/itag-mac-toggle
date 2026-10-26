# iTAG Mac Toggle

**Tek Bluetooth düğmesiyle macOS ekranlarını kilitle/uyut, ikinci basışta uyandır.**
RSSI/mesafe eşiği yok; doğrudan BLE düğme bildirimini dinler.

[English README](README.en.md) · [MIT Lisansı](LICENSE)

> **Durum:** Topluluk önizlemesi. Temel yöntem gerçek bir Mac Studio + iTAG cihazında
> denenmiştir; bu genel kullanıma uyarlanmış sürüm her macOS ve iTAG modelinde
> doğrulanmış değildir.

## Nasıl çalışır?

| Basış | İşlem |
|---|---|
| 1. kısa basış | `pmset displaysleepnow`: monitörleri uyut |
| 2. kısa basış | `caffeinate -u -t 2`: monitörleri uyandır; isteğe bağlı bir macOS Kestirmesi çalıştır |
| 3. kısa basış | Aynı döngü yeniden başlar |

Mac'in **Kilit Ekranı** ayarından, ekran kapatıldıktan sonra **hemen parola isteme**
seçeneği açık olmalıdır. Bu nedenle birinci basışta macOS oturumu kilitlenir.

**Önemli:** Ekranı uyandırmak oturum kilidini kaldırmaz. Kilitli ekranda otomatik
oturum açma yalnızca kullanıcı tarafından ayrıca yapılandırılmış ve test edilmiş
bir kestirmeyle mümkündür. Proje parola toplamaz, saklamaz veya kimlik doğrulamayı
kendi başına atlatmaz.

## Gereksinimler

- macOS ve çalışan Bluetooth LE (BLE) alıcısı
- `FFE0` servisi ve bildirim gönderen `FFE1` karakteristiğine sahip **uyumlu** bir iTAG
- Homebrew (kurulum aracı, Python 3.13 ve `bleak` kurar)
- Kullanıcı oturumunun açılmış olması (ilk oturum açma ekranında çalışmaz)

Bu proje tüm `iTAG` etiketlerinin aynı protokolü kullandığını garanti etmez.
Bir örnek cihazda kısa basış bildirimi `FFE1 = 0x01` olarak gözlemlenmiştir.

## Kolay kurulum

1. Depoyu indirin ya da klonlayın.
2. Terminal'de depo klasörünü açın.
3. Kurulumu başlatın:

   ```bash
   bash scripts/install.sh
   ```

4. Şu dosyayı düzenleyin:

   ```text
   ~/Library/Application Support/itag-mac-toggle/config.json
   ```

   İlk deneme için `device_name` genellikle `iTAG` bırakılabilir.
   Birden fazla iTAG varsa `device_id` değerini `--scan` ile bulunan Mac'e özgü
   Bluetooth UUID'siyle doldurun. `wake_shortcut` boş kalırsa yalnız ekran uyanır.
   Mac'te zaten çalışan bir Kestirmeniz varsa yalnızca adını yazın, örneğin
   `"wake_shortcut": "Mac Giriş"`.

5. Test edin (**ekran kilitlemez**):

   ```bash
   "$HOME/Library/Application Support/itag-mac-toggle/.venv/bin/python" \
     "$HOME/Library/Application Support/itag-mac-toggle/itag.py" --test
   ```

6. Test başarılı olursa `Ctrl+C` ile durdurup gerçek işlemleri deneyin:

   ```bash
   "$HOME/Library/Application Support/itag-mac-toggle/.venv/bin/python" \
     "$HOME/Library/Application Support/itag-mac-toggle/itag.py" --active
   ```

7. Terminal açık kalmadan otomatik başlatmak için önce manuel dinleyiciyi
   `Ctrl+C` ile durdurup depo klasöründe:

   ```bash
   bash scripts/install-service.sh
   ```

   Servis macOS kullanıcı oturumu açıldığında çalışır; arka planda tekrar bağlanmayı
   dener ve beklenmedik kapanmada launchd tarafından yeniden başlatılır.

**Uyarı:** Mevcut başka bir iTAG dinleyicisi veya ProximityLock aynı cihaza
bağlıysa kapatın. Aynı anda iki dinleyici çalıştırmayın.

## Kullanım ve yönetim

```bash
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --scan
"$APP/.venv/bin/python" "$APP/itag.py" --test
tail -f "$HOME/Library/Logs/itag-mac-toggle.log"
launchctl print "gui/$(id -u)/org.itag-mac-toggle.agent"
```

Sıradaki eylem `state.json` içinde saklanır. Bilgisayarı başka yoldan
kilitleyip açarsanız düğme sırası fiziksel ekran durumundan farklı olabilir.
**Otomatik servisi durdurduktan sonra** yeniden `LOCK` ile başlatmak için:

```bash
launchctl bootout "gui/$(id -u)/org.itag-mac-toggle.agent"
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --reset-state
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/org.itag-mac-toggle.agent.plist"
```

Otomatik başlamayı kaldırmak için depo klasöründe:

```bash
bash scripts/uninstall-service.sh
```

Bu komut uygulama dosyalarını veya kişisel `config.json` dosyanızı silmez.

## Sınırlamalar ve güvenlik

- **Mac'in tamamı uykuya geçerse** Python BLE dinleyicisi çalışamaz; uyanma için
  ayrıca desteklenen bir uyandırma yöntemi gerekir. Yalnızca monitör uykusunda
  test edilmiştir.
- Monitörleri uyandırma isteği `caffeinate` ile gönderilir; tüm monitör
  ve macOS sürümlerinde garanti edilmez.
- İkinci basış fiziksel duruma bakarak değil, saklanan `LOCK/WAKE` sırasıyla çalışır.
  Başka bir yolla kilitleme/açma sıralamayı bozabilir.
- Düğmeye basan herhangi biri ilişkilendirilen kestirmeyi tetikleyebilir.
  Parola giren kestirmeler ek risk yaratır. Güvenlik ihtiyacınıza göre ayarlayın.
- Bluetooth cihazı taklit edilebilir; bu tasarım güvenli kimlik doğrulama değildir.
- macOS, Terminal veya arka plan Python sürecine Bluetooth izni isteyebilir.
  **Sistem Ayarları → Gizlilik ve Güvenlik → Bluetooth** bölümünü kontrol edin.
- `config.json`, sanal ortam ve durum dosyaları `.gitignore` ile hariç tutulur.
  **Şifreleri, SSH anahtarlarını ve özel kestirme içeriklerini depoya eklemeyin.**
- Homebrew kurulum betiği yerel `Application Support` dizinine dosyaları kopyalar,
  mevcut `config.json` dosyasını korur.

## Geliştirme

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q itag.py
bash -n scripts/*.sh
```

Bunlar kodun temel mantığını denetler; gerçek BLE cihazı ve macOS uyumluluğunun
yerini tutmaz. Katkı için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

Temel Bluetooth altyapısı: [Bleak](https://github.com/hbldh/bleak).
## Sorun giderme ve güvenlik

- [Detaylı sorun giderme rehberi](docs/TROUBLESHOOTING.md)
- [Güvenlik modeli ve sorumlu bildirim](SECURITY.md)
- [Sürüm notları](CHANGELOG.md)
