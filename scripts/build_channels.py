"""Собирает custom.channels.xml из tvg-id плейлиста rus.m3u.

Запускать из корня клона iptv-org/epg.
"""
import re, glob, urllib.request
import xml.etree.ElementTree as ET

M3U = "https://iptv-org.github.io/iptv/languages/rus.m3u"
text = urllib.request.urlopen(M3U).read().decode("utf-8")
playlist_ids = set(re.findall(r'tvg-id="([^"]+)"', text))
print("ID в плейлисте:", len(playlist_ids))


def base(i):  # "Channel.ru@SD" -> "Channel.ru"
    return i.split("@")[0]


by_base = {base(i): i for i in playlist_ids}
found = {}  # playlist_id -> элемент <channel>

for path in sorted(glob.glob("sites/**/*.channels.xml", recursive=True)):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for ch in root.iter("channel"):
        xid = ch.get("xmltv_id", "")
        pid = xid if xid in playlist_ids else by_base.get(base(xid))
        if pid and pid not in found:  # берём первый найденный источник
            ch.set("xmltv_id", pid)
            found[pid] = ch

out = ET.Element("channels")
for ch in found.values():
    out.append(ch)
ET.indent(out)
ET.ElementTree(out).write("custom.channels.xml", encoding="UTF-8", xml_declaration=True)
print("Найдено EPG для каналов:", len(found), "из", len(playlist_ids))

# по одному файлу на сайт: падение одного источника не ломает остальные
import os, collections
os.makedirs("per_site", exist_ok=True)
groups = collections.defaultdict(list)
for ch in found.values():
    groups[ch.get("site")].append(ch)
for site, chs in groups.items():
    r = ET.Element("channels")
    r.extend(chs)
    ET.indent(r)
    ET.ElementTree(r).write(f"per_site/{site}.channels.xml", encoding="UTF-8", xml_declaration=True)
print("Сайтов-источников:", len(groups))
