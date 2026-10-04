"""Склеивает epg/out/*.xml в guide.xml. Для каждого канала берётся ОДИН источник —
тот, что отдал больше всего передач. Запускать из корня клона iptv-org/epg."""
import glob, sys, collections
import xml.etree.ElementTree as ET

best = {}  # channel_id -> (count, [programmes], channel_element)
for path in sorted(glob.glob("out/*.xml")):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        print("пропуск битого файла:", path)
        continue
    progs = collections.defaultdict(list)
    for p in root.findall("programme"):
        progs[p.get("channel")].append(p)
    chans = {c.get("id"): c for c in root.findall("channel")}
    for cid, plist in progs.items():
        if cid not in best or len(plist) > best[cid][0]:
            best[cid] = (len(plist), plist, chans.get(cid))

tv = ET.Element("tv", {"generator-info-name": "iptv-epg"})
for cid, (n, plist, ch) in best.items():
    if ch is not None:
        tv.append(ch)
for cid, (n, plist, ch) in best.items():
    tv.extend(plist)
ET.indent(tv)
ET.ElementTree(tv).write("guide.xml", encoding="UTF-8", xml_declaration=True)
print("каналов:", len(best), "программ:", sum(v[0] for v in best.values()))
if not best:
    sys.exit(1)
