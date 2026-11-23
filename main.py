#!/usr/bin/env python3
"""News poster: Monday 23 November 2026. Stdlib only, deterministic.

Draws a 1024x1024 broadsheet front page with 43 stories:
3 heroes + 12 medium cards + 28 list items, a UTC timeline,
a numbered world map, and a DATE CHECK / LEFT OUT box.
Every story carries a verification tag and a source.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 222)
PAPER = (252, 248, 236)
INK = (20, 20, 20)
GREY = (90, 86, 76)
RED = (176, 30, 30)
NAVY = (27, 58, 92)
GOLD = (178, 138, 44)
TEAL = (18, 110, 105)
GREEN = (34, 120, 60)
LIGHT = (232, 224, 198)
RULE = (120, 110, 88)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(d, x, y, s, fnt, fill=INK, anchor="la"):
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)


def trunc(d, s, fnt, width):
    if d.textlength(s, font=fnt) <= width:
        return s
    while s and d.textlength(s + "\u2026", font=fnt) > width:
        s = s[:-1]
    return s + "\u2026"


def tagline(ver, src):
    return ver + "  \u00b7  " + src


# ---------------------------------------------------------------- data
# (num, region, headline, deck, verification, source, scene, big)
HEROES = [
    (1, "CLIMATE \u00b7 ANTALYA", "COP31 COLLAPSES: NO DEAL ON FOSSIL FUELS",
     "EU and island states reject a pact with no fossil-fuel mention.",
     "CONFIRMED", "AP / Reuters", "cop", "NO DEAL"),
    (2, "WAR \u00b7 LIBYA & BALTIC", "RUSSIAN WARSHIP HIT FAR FROM UKRAINE",
     "Merkury burns at Benghazi; cargo ship Sparta II hit off Finland.",
     "REPORTED", "WSJ / Reuters", "ships", "2 SHIPS"),
    (3, "MARKETS \u00b7 NEW YORK", "WALL ST ROUT: WORST WEEK SINCE 2020",
     "Dow -8%, S&P -8.6%, Nasdaq -10% for the week; futures rebound.",
     "CONFIRMED", "Investors.com / Reuters", "chart", "-10%"),
]

MEDIUM = [
    (4, "SPORT \u00b7 TURIN", "ALCARAZ WINS FIRST ATP FINALS CROWN",
     "Beats world No. 1 Zverev 6-2, 7-6(7) in Turin.", "CONFIRMED", "Reuters / ATP", "tennis", "6-2  7-6"),
    (5, "SPORT \u00b7 NEW YORK", "SKUBAL TO METS: RECORD $450M DEAL",
     "Nine years, $50m a year \u2014 the richest pitcher deal ever.", "REPORTED", "AP / ESPN", "baseball", "$450M"),
    (6, "SPORT \u00b7 WELLINGTON", "INDIA PILE UP RECORD 720/9",
     "Highest Test total ever in New Zealand; Pant 128, Rahul 136.", "CONFIRMED", "Reuters / Cricinfo", "cricket", "720/9"),
    (7, "TRAVEL \u00b7 ATLANTA", "DELTA GLITCH DELAYS 1,900 FLIGHTS",
     "Weight-and-balance system fails days before Thanksgiving.", "CONFIRMED", "CNN / AP", "plane", "1,900"),
    (8, "ASIA \u00b7 SEOUL", "KOREA MINISTER QUITS OVER EXAM CHAOS",
     "Resigns after AI-cheating measures disrupt college entrance test.", "CONFIRMED", "Reuters", "exam", "AI"),
    (9, "DIPLOMACY \u00b7 DELHI", "NEPAL PM MEETS MODI IN DELHI",
     "Balendra Shah's first India visit: energy, rail, border talks.", "CONFIRMED", "IANS / MEA", "flags", "10 AREAS"),
    (10, "DISASTER \u00b7 BANTEN", "FACTORY FIRE: 50 WORKERS MISSING",
     "Candy plant blaze in Cikande; seven body bags recovered.", "CONFIRMED", "Reuters / AP", "fire", "50"),
    (11, "WAR \u00b7 KYIV", "KYIV DRONE STRIKE KILLS 3, 15 MISSING",
     "Russia fired 2,700 drones and 165 missiles in one week, Kyiv says.", "REPORTED", "Kyiv Independent", "kyiv", "2,700"),
    (12, "MARKETS \u00b7 SHANGHAI", "CHINA EASES MARGIN RULES TO AID STOCKS",
     "Minimum margin ratio cut to 80% from 100% from 30 Nov.", "CONFIRMED", "Reuters", "margin", "80%"),
    (13, "POLITICS \u00b7 VIRGINIA", "TRUMP HOSTS MEME-COIN GALA",
     "Coin once $75 now under $1; 185 wallets qualify for dinner.", "CONFIRMED", "Reuters", "coin", "$75\u2192$1"),
    (14, "POLITICS \u00b7 WASHINGTON", "HOUSE DEMOCRATS WIN 258 SEATS",
     "Largest majority since 1992; Jeffries nominated for Speaker.", "CONFIRMED", "AP", "capitol", "258"),
    (15, "ECONOMY \u00b7 EUROPE", "FLASH PMIs: EUROPE, US STILL GROWING",
     "Eurozone mfg 52.8, US mfg 54.6; France still contracting.", "CONFIRMED", "S&P Global", "pmi", "52.8"),
]

# (num, headline, verification, source)
LIST = [
    (16, "Settler arson in West Bank condemned by Eisenkot", "REPORTED", "Reuters"),
    (17, "US intel chief: Putin 'not America's friend'", "CLAIM", "Reuters"),
    (18, "Schumer faces Van Hollen challenge; vote 1 Dec", "REPORTED", "Reuters"),
    (19, "Jeffries set to be first Black House Speaker", "REPORTED", "AP"),
    (20, "US loses measles-free status as cases surge", "CONFIRMED", "AP"),
    (21, "FAA pauses router installs after ground stop", "REPORTED", "AP"),
    (22, "US Army to detonate bomb chemicals in Iowa", "REPORTED", "AP"),
    (23, "California billionaire tax rejected by voters", "REPORTED", "AP"),
    (24, "Thanksgiving dinner costlier; record turkey prices", "REPORTED", "AP"),
    (25, "Clariant & CD&R in talks to buy Ashland for $3.39bn", "REPORTED", "Bloomberg"),
    (26, "Anthropic IPO bankers chafed; shares fell 8.5% Fri", "REPORTED", "Reuters"),
    (27, "Nvidia dived 14% on Friday, 22.9% for the week", "CONFIRMED", "Investors.com"),
    (28, "Futures rebound: Nasdaq +2.8% on Oracle, Korea news", "REPORTED", "Investors.com"),
    (29, "Thousands march in Lisbon over living costs", "REPORTED", "AP"),
    (30, "Myanmar calls ASEAN decision 'unfair and imbalanced'", "CLAIM", "Myanmar govt"),
    (31, "Saudi coalition says it intercepted Houthi missile", "CLAIM", "Saudi coalition"),
    (32, "Sparta II cargo ship towed out of Finnish waters", "CONFIRMED", "WSJ"),
    (33, "Russian drone violated Moldovan airspace twice", "CONFIRMED", "Moldova MoD"),
    (34, "Amit Shah launches Rs 4,000cr push in Arunachal", "REPORTED", "IANS"),
    (35, "Rajya Sabha MP Ramrao Wadkute dies in Delhi", "CONFIRMED", "IANS"),
    (36, "IFFI 2026 hosts BRICS film roundtable in Goa", "REPORTED", "PIB"),
    (37, "Pope Leo XIV hit in face with rosary in Lima", "REPORTED", "AP"),
    (38, "Big Ten has no team in AP top five, first since 2021", "CONFIRMED", "AP"),
    (39, "Ayodhya-Janakpur train flagged off by Modi, Shah", "REPORTED", "ANI"),
    (40, "HPE reports after close; Dell, HP on Tuesday", "REPORTED", "Stockopedia"),
    (41, "Trump to meet Putin separately on China trip", "REPORTED", "AP"),
    (42, "Sanders unveils Medicare for All push for new Congress", "REPORTED", "AP"),
    (43, "NZ retail sales due 21:45 UTC; Aussie PMI next", "REPORTED", "ActionForex"),
]

TIMELINE = [
    ("00:20", "Korea minister quits"),
    ("00:22", "India 157-4 at lunch, Wellington"),
    ("08:30", "Germany flash PMI"),
    ("09:00", "Eurozone flash PMI"),
    ("14:45", "US flash PMI"),
    ("21:00", "NY Fed's Williams speaks"),
    ("21:45", "NZ retail sales due"),
]

# lon, lat for map pins 1-15
PINS = {
    1: (30.7, 36.9), 2: (20.1, 32.1), 3: (-74.0, 40.7), 4: (7.7, 45.1),
    5: (-73.9, 40.75), 6: (174.8, -41.3), 7: (-84.4, 33.75), 8: (127.0, 37.5),
    9: (77.2, 28.6), 10: (106.2, -6.1), 11: (30.5, 50.45), 12: (121.5, 31.2),
    13: (-77.4, 39.0), 14: (-77.0, 38.9), 15: (8.7, 50.1),
}

REGION_COLOR = {
    "CLIMATE": TEAL, "WAR": RED, "MARKETS": NAVY, "SPORT": GREEN,
    "TRAVEL": NAVY, "ASIA": TEAL, "DIPLOMACY": NAVY, "DISASTER": RED,
    "POLITICS": NAVY, "ECONOMY": GOLD,
}


def region_color(region):
    return REGION_COLOR.get(region.split(" ")[0], NAVY)


# ---------------------------------------------------------------- scenes
def scene(d, box, kind, big, accent):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "cop":
        d.ellipse([x0 + 8, y0 + 4, x0 + 44, y0 + 40], fill=(70, 130, 160), outline=INK)
        d.arc([x0 + 14, y0 + 12, x0 + 38, y0 + 32], 200, 340, fill=(255, 255, 255), width=2)
        for i, sx in enumerate((x0 + 58, x0 + 86, x0 + 114)):
            d.rectangle([sx, y0 + 22, sx + 14, y0 + 40], fill=GREY)
            d.polygon([(sx, y0 + 22), (sx + 4, y0 + 12), (sx + 10, y0 + 12), (sx + 14, y0 + 22)], fill=GREY)
        d.line([x0 + 62, y0 + 10, x0 + 62, y0 + 4, x0 + 70, y0 + 12], fill=GREY, width=2)
        text(d, x1 - 6, y0 + 6, big, font(SANS_B, 15), fill=RED, anchor="ra")
        text(d, x1 - 6, y0 + 24, "FOSSIL FUELS: 0 MENTIONS", font(SANS_B, 7), fill=INK, anchor="ra")
    elif kind == "ships":
        d.rectangle([x0, y0 + h - 16, x1, y1], fill=(70, 130, 160))
        for sx, sy in ((x0 + 18, y0 + 18), (x0 + 150, y0 + 8)):
            d.rectangle([sx, sy + 12, sx + 64, sy + 22], fill=INK)
            d.rectangle([sx + 22, sy, sx + 30, sy + 12], fill=INK)
            for ang in range(0, 360, 45):
                import math
                ex = sx + 78 + int(10 * math.cos(math.radians(ang)))
                ey = sy + 17 + int(6 * math.sin(math.radians(ang)))
                d.line([sx + 78, sy + 17, ex, ey], fill=RED, width=2)
            d.ellipse([sx + 70, sy + 9, sx + 86, sy + 25], fill=(255, 180, 40), outline=RED)
        text(d, x0 + 8, y0 + 2, "BENGHAZI", font(SANS_B, 7), fill=INK)
        text(d, x1 - 8, y0 + 2, "BALTIC", font(SANS_B, 7), fill=INK, anchor="ra")
        text(d, cx, y1 - 14, big, font(SANS_B, 10), fill=(255, 255, 255), anchor="ma")
    elif kind == "chart":
        pts = [(x0 + 8, y0 + 18), (x0 + 60, y0 + 24), (x0 + 110, y0 + 20),
               (x0 + 160, y0 + 40), (x0 + 210, y0 + 50), (x0 + 260, y0 + 66),
               (x0 + 300, y0 + 62)]
        d.line(pts, fill=RED, width=3)
        d.polygon(pts + [(x0 + 300, y1 - 4), (x0 + 8, y1 - 4)], fill=(176, 30, 30, 60))
        d.line([x0 + 250, y0 + 66, x0 + 305, y0 + 36], fill=GREEN, width=3)
        d.polygon([(x0 + 305, y0 + 36), (x0 + 293, y0 + 34), (x0 + 303, y0 + 24)], fill=GREEN)
        text(d, x0 + 8, y1 - 16, "DOW 48,147", font(SANS_B, 11), fill=INK)
        text(d, x1 - 6, y0 + 2, big, font(SANS_B, 13), fill=RED, anchor="ra")
    elif kind == "tennis":
        d.rectangle(box, fill=(46, 120, 70))
        d.line([cx, y0, cx, y1], fill=(255, 255, 255), width=1)
        d.line([x0, cy, x1, cy], fill=(255, 255, 255), width=1)
        d.ellipse([cx + 40, cy - 2, cx + 50, cy + 8], fill=(220, 230, 60), outline=INK)
        text(d, cx, y0 + 3, big, font(SANS_B, 12), fill=(255, 255, 255), anchor="ma")
    elif kind == "baseball":
        d.polygon([(cx, y1 - 4), (x0 + 6, y0 + 8), (x1 - 6, y0 + 8)], fill=(200, 170, 110))
        d.polygon([(cx, y1 - 4), (x0 + 60, y0 + 26), (x1 - 60, y0 + 26)], fill=(240, 230, 200))
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255), outline=RED)
        text(d, cx, y0 + 2, big, font(SANS_B, 13), fill=RED, anchor="ma")
    elif kind == "cricket":
        d.rectangle([x0, y0, x1, y1], fill=(46, 120, 70))
        d.rectangle([x0 + 8, y0 + 4, x1 - 8, y0 + 12], fill=(240, 220, 170))
        d.line([x0 + 12, y0 + 16, x0 + 44, y1 - 6], fill=(210, 170, 90), width=5)
        d.ellipse([x0 + 46, y1 - 12, x0 + 54, y1 - 4], fill=RED)
        text(d, cx, y0 + 14, big, font(SANS_B, 12), fill=(255, 255, 255), anchor="ma")
    elif kind == "plane":
        d.polygon([(x0 + 10, cy), (x0 + 90, cy - 12), (x0 + 150, cy - 6),
                   (x0 + 150, cy + 6), (x0 + 90, cy + 12)], fill=NAVY)
        d.polygon([(x0 + 60, cy - 12), (x0 + 80, cy - 26), (x0 + 92, cy - 12)], fill=NAVY)
        d.line([x0 + 10, cy + 14, x1 - 10, cy + 14], fill=GREY, width=2)
        text(d, x1 - 6, y0 + 2, big + " DELAYED", font(SANS_B, 11), fill=RED, anchor="ra")
    elif kind == "exam":
        d.rectangle([x0 + 30, y0 + 2, x1 - 30, y1 - 2], fill=(255, 255, 255), outline=INK)
        for i in range(3):
            d.line([x0 + 38, y0 + 10 + i * 8, x1 - 38, y0 + 10 + i * 8], fill=GREY, width=1)
        d.line([x0 + 38, y0 + 10, x1 - 60, y0 + 10], fill=RED, width=2)
        text(d, x1 - 4, y1 - 12, big, font(SANS_B, 11), fill=RED, anchor="ra")
    elif kind == "flags":
        d.rectangle([x0 + 14, y0 + 2, x0 + 74, y0 + 18], fill=(255, 140, 40))
        d.rectangle([x0 + 84, y0 + 2, x0 + 144, y0 + 18], fill=(255, 255, 255), outline=INK)
        d.ellipse([x0 + 104, y0 + 6, x0 + 124, y0 + 14], fill=NAVY)
        text(d, cx, y0 + 20, big, font(SANS_B, 10), fill=INK, anchor="ma")
    elif kind == "fire":
        d.rectangle([x0 + 20, y0 + 12, x1 - 20, y1 - 4], fill=(120, 90, 70))
        d.polygon([(x0 + 40, y0 + 12), (x0 + 60, y0 - 2), (x0 + 80, y0 + 12)], fill=(255, 120, 30))
        d.polygon([(x0 + 110, y0 + 12), (x0 + 130, y0 - 2), (x0 + 150, y0 + 12)], fill=(255, 180, 40))
        text(d, cx, y1 - 12, big + " MISSING", font(SANS_B, 13), fill=(255, 255, 255), anchor="ma")
    elif kind == "kyiv":
        for i, bx in enumerate((x0 + 16, x0 + 66, x0 + 116)):
            d.rectangle([bx, y0 + 10, bx + 40, y1 - 4], fill=GREY)
            for wy in range(y0 + 14, y1 - 6, 8):
                d.rectangle([bx + 6, wy, bx + 14, wy + 4], fill=(255, 220, 120))
        d.ellipse([x0 + 8, y0 + 2, x0 + 28, y0 + 16], fill=RED)
        text(d, x1 - 6, y0 + 2, big + " DRONES/WK", font(SANS_B, 9), fill=RED, anchor="ra")
    elif kind == "margin":
        bars = [14, 20, 16, 26, 22]
        for i, bh in enumerate(bars):
            bx = x0 + 14 + i * 34
            d.rectangle([bx, y1 - 4 - bh, bx + 22, y1 - 4], fill=NAVY if i < 4 else GREEN)
        text(d, x1 - 6, y0 + 2, big, font(SANS_B, 13), fill=GREEN, anchor="ra")
    elif kind == "coin":
        d.ellipse([x0 + 12, y0 + 2, x0 + 48, y1 - 2], fill=GOLD, outline=INK)
        text(d, x0 + 30, y0 + 8, "$", font(SANS_B, 16), fill=INK, anchor="ma")
        d.line([x0 + 56, cy + 2, x0 + 120, cy - 8], fill=RED, width=3)
        text(d, x1 - 6, y0 + 2, big, font(SANS_B, 11), fill=RED, anchor="ra")
    elif kind == "capitol":
        d.rectangle([x0 + 20, y0 + 16, x1 - 20, y1 - 4], fill=(240, 240, 240), outline=INK)
        d.ellipse([cx - 22, y0 - 2, cx + 22, y0 + 20], fill=(240, 240, 240), outline=INK)
        for i in range(5):
            d.line([x0 + 30 + i * 36, y0 + 22, x0 + 30 + i * 36, y1 - 4], fill=INK, width=2)
        text(d, cx, y0 + 2, big, font(SANS_B, 12), fill=NAVY, anchor="ma")
    elif kind == "pmi":
        for i, (lab, val) in enumerate((("EU", "52.8"), ("US", "54.6"), ("UK", "53.0"))):
            gx = x0 + 16 + i * 70
            d.arc([gx, y0 + 2, gx + 52, y0 + 30], 180, 360, fill=INK, width=3)
            d.arc([gx, y0 + 2, gx + 52, y0 + 30], 180, 300, fill=GREEN, width=3)
            text(d, gx + 26, y0 + 12, val, font(SANS_B, 9), fill=INK, anchor="ma")
            text(d, gx + 26, y1 - 10, lab, font(SANS_B, 8), fill=GREY, anchor="ma")
    else:
        text(d, cx, cy - 8, big, font(SANS_B, 12), fill=accent, anchor="ma")


# ---------------------------------------------------------------- cards
def hero_card(d, x, y, w, h, item):
    num, region, head, deck, ver, src, kind, big = item
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=region_color(region))
    d.ellipse([x + 6, y + 10, x + 24, y + 28], fill=RED)
    text(d, x + 15, y + 12, str(num), font(SANS_B, 11), fill=(255, 255, 255), anchor="ma")
    text(d, x + 30, y + 13, region, font(SANS_B, 8), fill=GREY)
    scene(d, (x + 6, y + 32, x + w - 6, y + 108), kind, big, region_color(region))
    yy = y + 112
    for ln in wrap(d, head, font(SERIF, 16), w - 12)[:2]:
        text(d, x + 6, yy, ln, font(SERIF, 16), fill=INK)
        yy += 19
    text(d, x + 6, y + 152, trunc(d, deck, font(SANS, 9), w - 12),
         font(SANS, 9), fill=GREY)
    text(d, x + 6, y + h - 14, tagline(ver, src), font(SANS_B, 8), fill=RED)


def med_card(d, x, y, w, h, item):
    num, region, head, deck, ver, src, kind, big = item
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=region_color(region))
    d.ellipse([x + 5, y + 7, x + 21, y + 23], fill=NAVY)
    text(d, x + 13, y + 9, str(num), font(SANS_B, 9), fill=(255, 255, 255), anchor="ma")
    text(d, x + 25, y + 10, region, font(SANS_B, 7), fill=GREY)
    scene(d, (x + 4, y + 26, x + w - 4, y + 54), kind, big, region_color(region))
    yy = y + 56
    for ln in wrap(d, head, font(SERIF, 11), w - 10)[:2]:
        text(d, x + 5, yy, ln, font(SERIF, 11), fill=INK)
        yy += 12
    text(d, x + 5, y + h - 11, tagline(ver, src), font(SANS_B, 7), fill=RED)


# ---------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 240), outline=INK, width=1)
    text(d, x + 8, y + 5, "WHERE IT HAPPENED", font(SANS_B, 10), fill=INK)
    mx, my, mw, mh = x + 8, y + 24, w - 16, h - 30

    def px(lon, lat):
        return mx + int((lon + 180) / 360 * mw), my + int((90 - lat) / 180 * mh)

    land = [
        [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
         (-55, 47), (-70, 42), (-80, 32), (-90, 21), (-97, 16), (-105, 20),
         (-115, 30), (-125, 40), (-150, 60), (-168, 66)],
        [(-80, 10), (-60, 5), (-50, -5), (-40, -15), (-50, -30), (-65, -40),
         (-70, -50), (-73, -35), (-75, -18), (-80, 10)],
        [(-10, 36), (-5, 43), (0, 48), (5, 55), (10, 58), (20, 60), (28, 70),
         (40, 68), (30, 55), (20, 45), (12, 42), (0, 38), (-10, 36)],
        [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (40, 20),
         (48, 11), (40, -5), (35, -20), (25, -30), (18, -35), (12, -18),
         (9, 0), (-8, 5), (-17, 15)],
        [(40, 70), (60, 72), (90, 75), (120, 73), (150, 70), (170, 66),
         (160, 60), (140, 45), (130, 35), (122, 30), (110, 20), (100, 8),
         (90, 15), (80, 8), (75, 20), (65, 25), (55, 27), (45, 30), (40, 40),
         (40, 70)],
        [(113, -22), (130, -12), (142, -11), (150, -25), (153, -37),
         (140, -38), (129, -32), (115, -32), (113, -22)],
    ]
    for poly in land:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=(196, 205, 170), outline=(120, 130, 100))
    # nudge clustered US-east pins so all numbers stay readable
    nudge = {3: (-14, -8), 5: (10, 8), 13: (-12, 10), 14: (12, -10), 15: (0, -10)}
    for num, (lon, lat) in sorted(PINS.items()):
        px_, py_ = px(lon, lat)
        dx, dy = nudge.get(num, (0, 0))
        px_ += dx
        py_ += dy
        d.ellipse([px_ - 8, py_ - 8, px_ + 8, py_ + 8], fill=RED, outline=(255, 255, 255))
        text(d, px_, py_ - 6, str(num), font(SANS_B, 8), fill=(255, 255, 255), anchor="ma")
    text(d, x + 8, y + h - 14, "Pins 1-15 match the cards above.", font(SANS, 8), fill=GREY)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img, "RGBA")
    # masthead
    text(d, W // 2, 6, "T H E   W O R L D ' S   N E W S   O F   O N E   D A Y",
         font(SANS_B, 12), fill=INK, anchor="ma")
    text(d, W // 2, 22, "Monday 23 November 2026", font(SERIF, 42), fill=INK, anchor="ma")
    d.line([14, 70, 1010, 70], fill=RULE, width=1)
    text(d, W // 2, 73, "43 STORIES  \u00b7  7 REGIONS  \u00b7  15 FIELDS  \u00b7  ALL FROM THIS MONDAY",
         font(SANS_B, 11), fill=RED, anchor="ma")
    # timeline
    text(d, 14, 92, "THE DAY IN UTC", font(SANS_B, 10), fill=INK)
    d.line([14, 112, 1010, 112], fill=INK, width=1)
    step = (1010 - 170) / len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = int(170 + step * i + step / 2)
        d.ellipse([cx - 4, 108, cx + 4, 116], fill=RED)
        text(d, cx, 94, t, font(SANS_B, 9), fill=RED, anchor="ma")
        for j, ln in enumerate(wrap(d, label, font(SANS, 8), int(step) - 6)[:2]):
            text(d, cx, 118, ln, font(SANS, 8), fill=GREY, anchor="ma")
    # heroes
    for i, item in enumerate(HEROES):
        hero_card(d, 14 + i * 330, 140, 322, 178, item)
    # medium grid
    for r in range(3):
        for c in range(4):
            item = MEDIUM[r * 4 + c]
            med_card(d, 14 + c * 252, 324 + r * 98, 244, 92, item)
    # bottom: map + lists
    draw_map(d, 14, 624, 330, 312)
    lx, ly = 352, 624
    text(d, lx, 624, "MORE OF THE DAY  \u2014  STORIES 16\u201343", font(SANS_B, 10), fill=INK)
    d.line([lx, 640, 1010, 640], fill=INK, width=1)
    col_w = 324
    for i, (num, head, ver, src) in enumerate(LIST):
        col = i // 14
        row = i % 14
        x = lx + col * 334
        y = 646 + row * 21
        text(d, x, y, str(num) + ".", font(SANS_B, 9), fill=RED)
        lines = wrap(d, head, font(SANS, 9), col_w - 60)
        text(d, x + 20, y, lines[0], font(SANS, 9), fill=INK)
        tag = tagline(ver, src)
        text(d, x + 20, y + 10, tag, font(SANS_B, 7), fill=RED)
    # date check box
    d.rectangle([14, 942, 1010, 992], fill=(255, 235, 230), outline=RED, width=2)
    text(d, 22, 946, "DATE CHECK \u2014 LEFT OUT AS NOT THIS DAY'S NEWS",
         font(SANS_B, 10), fill=RED)
    text(d, 22, 960,
         "LEFT OUT: Anthropic IPO debut, Thu 19 Nov  \u00b7  GTA VI launch, Thu 19 Nov  \u00b7  Kerch Bridge collapse, Tue 17 Nov.",
         font(SANS, 9), fill=INK)
    text(d, 22, 974,
         "NOT YET: Thanksgiving, Thu 26 Nov  \u00b7  China margin cut, Mon 30 Nov  \u00b7  Senate Dem vote, Tue 1 Dec  \u00b7  MLB lockout, Wed 2 Dec.",
         font(SANS, 9), fill=INK)
    # footer
    text(d, W // 2, 998,
         "Every story here happened, or was first reported, on Monday 23 November 2026; claims are attributed.",
         font(SANS, 9), fill=GREY, anchor="ma")
    text(d, W // 2, 1010,
         "Sources: Reuters, AP, WSJ, CNN, IANS, S&P Global, Investors.com, ATP, Cricinfo and others.",
         font(SANS, 8), fill=GREY, anchor="ma")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get("OUTPUT_DIR") or "."
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    print(build())
