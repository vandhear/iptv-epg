"""Склеивает epg/out/*.xml в один XMLTV. Запускать из корня клона iptv-org/epg."""
import glob, sys
import xml.etree.ElementTree as ET

channels, programmes, seen = {}, [], set()
for path in sorted(glob.glob("out/*.xml")):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        print("пропуск битого файла:", path)
        continue
    for ch in root.findall("channel"):
        channels.setdefault(ch.get("id"), ch)
    for p in root.findall("programme"):
        key = (p.get("channel"), p.get("start"))
        if key not in seen:
            seen.add(key)
            programmes.append(p)

tv = ET.Element("tv", {"generator-info-name": "iptv-epg"})
tv.extend(channels.values())
tv.extend(programmes)
ET.indent(tv)
ET.ElementTree(tv).write("guide.xml", encoding="UTF-8", xml_declaration=True)
print("каналов:", len(channels), "программ:", len(programmes))
if not programmes:
    sys.exit(1)
