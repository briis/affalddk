"""Parser for the affaldonline.dk tømningskalender PDF.

AffaldOnlinePdfAPI in interface.py fetches the PDF; everything about the
PDF's internal structure lives here, so the whole PDF handling can be
removed in one place if affaldonline ever serves the calendar as data.
"""
import datetime as dt
import re
import zlib

PDF_MONTHS = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
              "august", "september", "oktober", "november", "december"]
PDF_WEEKDAYS = ["man", "tir", "ons", "tor", "fre", "lør", "søn"]
PDF_STREAM = re.compile(rb"<<([^<>]*?)>>\s*stream\r?\n(.*?)endstream", re.S)
PDF_TEXT = re.compile(r"BT ([\d.]+) ([\d.]+) Td \((.*)\) Tj ET")
PDF_ICON = re.compile(r"[\d.]+ 0 0 [\d.]+ ([\d.]+) ([\d.]+) cm /(I\d+) Do")
PDF_ROW_TOLERANCE = 4  # pt; icons sit ~1.25 pt below their row's baseline
PDF_ICON_GROUP_GAP = 14  # pt; icons within one legend entry sit ~12.76 pt apart


def parse_affaldonline_pdf(pdf, year):
    """Parse an affaldonline.dk showToemCal.php PDF into {date: {fraction, ...}}.

    The fraction of a pickup is only shown as icon images next to the date.
    The legend at the bottom puts the same icons next to the fraction name,
    so icon name -> fraction is read from the legend, pairing each icon with
    the nearest label to its right on the same baseline. Adjacent legend
    icons sharing a label form a group; a date row decodes greedily from the
    longest group it fully contains, so an icon can mean different things
    alone and inside a group (Sorø's pap icon). Icons used next to a date
    but absent from the legend, and date rows that end up without a
    fraction, are reported as missing instead of silently dropped.
    """
    ops = []
    for m in PDF_STREAM.finditer(pdf):
        if b"/FlateDecode" not in m.group(1) or b"/Subtype" in m.group(1):
            continue
        try:
            content = zlib.decompress(m.group(2)).decode("latin1")
        except zlib.error:
            continue
        for line in content.splitlines():
            if text := PDF_TEXT.search(line):
                ops.append(("T", float(text[1]), float(text[2]), text[3].strip()))
            elif icon := PDF_ICON.search(line):
                ops.append(("I", float(icon[1]), float(icon[2]), icon[3]))

    # Legend pairing: day numbers, weekday names and empty strings are not
    # labels, so a label between two icons cannot steal the mapping and the
    # pairing does not depend on the order of the PDF ops.
    icons = [(x, y, value) for kind, x, y, value in ops if kind == "I"]
    labels = [(x, y, value) for kind, x, y, value in ops if kind == "T" and value
              and value.lower() not in PDF_WEEKDAYS and not value.isdigit()]
    icon_label = {}
    for x, y, icon in icons:
        right = [(lx - x, ly, label) for lx, ly, label in labels
                 if lx > x and abs(ly - y) < PDF_ROW_TOLERANCE]
        if right:
            icon_label[(icon, x, y)] = min(right, key=lambda c: (c[0], c[1]))[2]

    # Adjacent legend icons with the same label form one group (e.g. the
    # pap icon means "Pap/papir" next to a partner icon, "Pap" alone).
    legend_groups = []
    for (icon, x, y), label in sorted(icon_label.items(), key=lambda i: (i[0][2], i[0][1])):
        if legend_groups and legend_groups[-1][0] == (y, label) \
                and x - legend_groups[-1][1][-1][1] < PDF_ICON_GROUP_GAP:
            legend_groups[-1][1].append((icon, x))
        else:
            legend_groups.append(((y, label), [(icon, x)]))
    groups = sorted(((frozenset(icon for icon, _x in members), label)
                     for (_, label), members in legend_groups),
                    key=lambda g: (-len(g[0]), g[1]))

    headers, current, weekday = [], None, None
    row_icons, warned_icons, result = {}, set(), {}
    for kind, x, y, value in ops:
        if kind == "T" and value.lower() in PDF_MONTHS:
            headers = [h for h in headers if abs(h[1] - y) < 1]
            headers.append((x, y, PDF_MONTHS.index(value.lower()) + 1))
        elif kind == "T" and value.lower() in PDF_WEEKDAYS:
            weekday = PDF_WEEKDAYS.index(value.lower())
        elif kind == "T" and value.isdigit() and headers and weekday is not None:
            month = min(headers, key=lambda h: abs(h[0] - x))[2]
            date = dt.date(year, month, int(value))
            if date.weekday() != weekday:
                raise ValueError(f"Weekday mismatch for {date} in affaldonline PDF")
            current, weekday = (date, y), None
            row_icons[date] = []
        elif kind == "I" and current and abs(current[1] - y) < PDF_ROW_TOLERANCE:
            row_icons[current[0]].append(value)

    for date, row in sorted(row_icons.items()):
        remaining, fractions = set(row), set()
        for group_icons, label in groups:
            if group_icons <= remaining:
                remaining -= group_icons
                fractions.add(label)
        for icon in sorted(remaining):
            if icon not in warned_icons:
                warned_icons.add(icon)
                print(f"missing: icon {icon} is not defined by the affaldonline legend")
        if fractions:
            result[date] = fractions
        else:
            print(f"missing: no fraction found for {date} in the affaldonline PDF")
    return result
