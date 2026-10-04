# iptv-epg

Автогенерация EPG (XMLTV) для `rus.m3u` из iptv-org, публикация через GitHub Pages.

## Запуск
1. Создайте репозиторий на GitHub и запушьте эти файлы в `main`.
2. Settings → Pages → Source: **GitHub Actions**.
3. Actions → update-epg → **Run workflow** (дальше по расписанию раз в сутки).
4. Гайд будет по адресу `https://<user>.github.io/<repo>/guide.xml` (или `guide.xml.gz`).
5. В Televizo: плейлист `https://iptv-org.github.io/iptv/languages/rus.m3u`, источник EPG — URL выше.
