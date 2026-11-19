# Shorts 3D Studio (0 TL beta)

**Önceki kötü, robotik sesli örnek kaldırıldı.** Yeni sistem gerçek 3D geometri ve hareketli kamera kullanır (VTK); Türkçe nöral ses için Edge TTS kullanır. Video 720x1280 dikey, altyazılı MP4 olarak üretilir.

### Önce videoyu kontrol et

GitHub > **Actions** > **3D Shorts on schedule (preview first)** > **Run workflow**. Çalışma tamamlanınca **Artifacts** bölümünden `3D-Shorts-Preview` videosunu indir. Kod güncellendiğinde de otomatik önizleme üretilir.

### YouTube'a her gün otomatik gizli yükleme

**Varsayılan olarak yükleme kapalıdır.** Kanal sahibinin bir defa YouTube OAuth `youtube.upload` izni verip GitHub > Settings > Secrets and variables > Actions > Secrets bölümüne şu üç gizli anahtarı eklemesi gerekir: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`. Tokenları sohbet mesajına veya depoya koyma. Ardından aynı ekrandan **Variables** kısmına `ENABLE_UPLOAD=true` ekle.

19:17 Türkiye saati civarında zamanlanmış işler videoyu **private/gizli** olarak yüklemeye çalışır. Manuel çalışmalar yalnızca önizleme üretir. Her video için otomatik kaliteli yapay zekâ hikâye üretimi henüz entegre edilmemiştir; deneme metinleri üçlü döngüde tekrarlanır. Bu nedenle yayına sürekli geçmeden önce hikâye sistemini de tamamlamak gerekir.

### Gerçekçi sınırlar

Görseller stilize basit 3D animasyondur, stüdyo kalitesinde fotogerçekçi video değildir. Edge TTS, resmi ücretli bir hizmet garantisi olmayan çevrimiçi istemcidir; bozulursa video yüklemek yerine iş durur. Kusursuz ses ve her gün sorunsuz yükleme garanti edilemez. Ücretsiz GitHub Actions standart koşulları herkese açık depolar için geçerlidir. İçeriklerin YouTube politikalarına uygunluğunu ve kalitesini yayın öncesi denetle.

Official docs: https://docs.github.com/en/actions/concepts/billing-and-usage | https://developers.google.com/youtube/v3/guides/auth/installed-apps