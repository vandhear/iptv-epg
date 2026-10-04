"""Добивает каналы без программы из сторонних XMLTV (iptvx.one, epg.pw) по названию.
Запускать из корня клона iptv-org/epg после merge_guides.py. Дополняет guide.xml."""
import re, gzip, sys, urllib.request, collections
import xml.etree.ElementTree as ET

M3U = "https://iptv-org.github.io/iptv/languages/rus.m3u"
SOURCES = [  # порядок = приоритет
    "https://iptvx.one/EPG",
    "https://epg.pw/xmltv/epg_RU.xml.gz",
]


def norm(s):
    s = re.sub(r"\(.*?\)|\[.*?\]", "", (s or "").lower())
    s = re.sub(r"\b(hd|fhd|uhd|sd|tv|канал|телеканал|international|россия)\b", "", s)
    return re.sub(r"[^a-zа-я0-9]", "", s)


text = urllib.request.urlopen(M3U).read().decode("utf-8")
names = {i: n.strip() for i, n in re.findall(r'#EXTINF[^\n]*tvg-id="([^"]+)"[^\n]*,(.*)', text)}

guide = ET.parse("guide.xml").getroot()
have = {p.get("channel") for p in guide.findall("programme")}
by_norm = collections.defaultdict(list)  # норм. имя -> id плейлиста без программы
for i, n in names.items():
    if i not in have and norm(n):
        by_norm[norm(n)].append(i)
print("без программы:", sum(len(v) for v in by_norm.values()))

for url in SOURCES:
    todo = {k: v for k, v in by_norm.items() if any(i not in have for i in v)}
    if not todo:
        break
    print("источник:", url)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = gzip.GzipFile(fileobj=urllib.request.urlopen(req, timeout=300))
        ext2pl = {}  # id во внешнем xmltv -> id плейлиста
        added = 0
        for ev, e in ET.iterparse(raw, events=("end",)):
            if e.tag == "channel":
                for dn in e.findall("display-name"):
                    for pid in todo.get(norm(dn.text), ()):
                        if pid not in have:
                            ext2pl[e.get("id")] = pid
                e.clear()
            elif e.tag == "programme":
                pid = ext2pl.get(e.get("channel"))
                if pid:
                    e.set("channel", pid)
                    guide.append(e)
                    added += 1
                else:
                    e.clear()
        have |= set(ext2pl.values())
        print("  добавлено программ:", added, "каналов:", len(set(ext2pl.values())))
    except Exception as ex:  # источник недоступен — не страшно
        print("  источник пропущен:", ex)

# каналы для новых id
known = {c.get("id") for c in guide.findall("channel")}
for pid in have:
    if pid not in known:
        c = ET.SubElement(guide, "channel", {"id": pid})
        ET.SubElement(c, "display-name").text = names.get(pid, pid)
# <channel> должны идти до <programme>
chs = [x for x in guide if x.tag == "channel"]
prs = [x for x in guide if x.tag == "programme"]
guide[:] = chs + prs
ET.indent(guide)
ET.ElementTree(guide).write("guide.xml", encoding="UTF-8", xml_declaration=True)
print("итого каналов с программой:", len(have))
