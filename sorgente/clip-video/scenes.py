"""Le scene: ogni funzione disegna un fotogramma (t in secondi) per W x H. Valgono sia per 16:9 sia per 9:16."""
from b4f import *

def V(W, H): return H > W
_LC = {}
def logo_card(w):
    if w not in _LC:
        lg = img('logo-full'); h = int(w * lg.height / lg.width); lg = lg.resize((w, h), Image.LANCZOS)
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(w * .12), fill=255); lg.putalpha(m); _LC[w] = shadow(lg, 14, (0, 10), 110)
    return _LC[w]

# 1 · un elenco lungo, preciso… e muto (blu notte, glitch)
ROWS = [('Caffè e cornetto', '-1,30'), ('Supermercato', '-64,19'), ('Carburante', '-56,34'), ('Bar', '-2,34'), ('Abbonamento', '-13,99'), ('Pranzo fuori', '-23,74'),
        ('Farmacia', '-12,50'), ('Spesa', '-89,78'), ('Caffè', '-1,48'), ('Bollette luce', '-59,29'), ('Parcheggio', '-3,00'), ('Cena fuori', '-50,44'), ('Telefono', '-9,99'), ('Caffè', '-1,81')]
def s_elenco(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H)
    lw, lh = (int(W * .78), int(H * .52)) if v else (int(W * .36), int(H * .86))
    lx, ly = ((W - lw) // 2, int(H * .40)) if v else (int(W * .07), int(H * .07))
    lst = Image.new('RGBA', (lw, lh), (0, 0, 0, 0)); d = ImageDraw.Draw(lst); d.rounded_rectangle((0, 0, lw - 1, lh - 1), 26, fill=(245, 242, 232, 255))
    rh = 74 if v else 62; off = (t * 120) % (rh * len(ROWS))
    for i in range(-1, lh // rh + 3):
        k = (i + int(off // rh)) % len(ROWS); y = i * rh - off % rh + 20
        d.text((30, y), ROWS[k][0], font=F('comf', 30 if v else 26), fill=(60, 60, 60)); d.text((lw - 30, y), ROWS[k][1] + ' €', font=F('comf', 30 if v else 26), fill=(150, 90, 0), anchor='ra')
        d.line((30, y + rh - 14, lw - 30, y + rh - 14), fill=(220, 214, 200), width=2)
    m = Image.new('L', lst.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, lw - 1, lh - 1), 26, fill=255); lst.putalpha(m)
    fade = Image.new('L', lst.size, 255); fd = ImageDraw.Draw(fade)
    for y in range(80): fd.line((0, y, lw, y), fill=int(255 * y / 80)); fd.line((0, lh - 1 - y, lw, lh - 1 - y), fill=int(255 * y / 80))
    lst.putalpha(Image.composite(lst.getchannel('A'), Image.new('L', lst.size, 0), fade))
    put(c, shadow(lst), lx + lw / 2, ly + lh / 2 + (1 - ease(t / .6)) * 120, 1, ease(t / .5))
    tx, ty = (W / 2, H * .12) if v else (W * .72, H * .26)
    put(c, text('UN ELENCO.', F('anton', 150 if v else 150), WHITE), tx, ty, back((t - .4) / .35), clamp((t - .4) / .15))
    put(c, text('LUNGO, PRECISO…', F('anton', 92 if v else 96), WHITE), tx, ty + (150 if v else 160), back((t - 1.4) / .35), clamp((t - 1.4) / .15))
    m2 = text('…E MUTO.', F('anton', 190 if v else 200), AMBER)
    g = 0 if t < 2.6 else (1 - clamp((t - 2.6) / .5)) + (0.6 if 4.2 < t < 4.4 else 0)
    put(c, glitch(m2, g, int(t * 30)), tx, ty + (340 if v else 370), back((t - 2.6) / .3), clamp((t - 2.6) / .1))
    return c
EV_ELENCO = [(0.05, whoosh(1, .5), .7)] + [(0.3 + i * .5, tick(1800 + i * 60), .35) for i in range(4)] + [(.4, pop(600), .6), (1.4, pop(750), .6), (2.6, glitchs(4), 1), (2.62, hit(), .8), (4.2, glitchs(8), .7)]

# 2 · l'app che avrei voluto usare io (chiaro, mockup)
def s_app(t, W, H):
    c = bg_cream(W, H); v = V(W, H)
    ph = phone('home', 520 if v else 470)
    px, py = (W / 2, H * .62) if v else (W * .70, H * .56)
    put(c, ph, px, py + (1 - ease(t / .8)) * H * .6, 0.92 + 0.06 * ease(t / 3))
    lc = logo_card(190 if v else 210)
    lx, ly = (W * .27, H * .1) if v else (W * .30, H * .24)
    put(c, lc, lx, ly, back((t - .5) / .4), clamp((t - .5) / .2))
    tx0 = (W * .5, H * .26) if v else (lx, ly + lc.height / 2 + 70)
    if v: put(c, text('RISPARMIO', F('anton', 110), INK), W * .66, ly, back((t - .9) / .35), clamp((t - .9) / .15)); ty = H * .2
    else: put(c, text('RISPARMIO', F('anton', 110), INK), lx, tx0[1], back((t - .9) / .35), clamp((t - .9) / .15)); ty = tx0[1] + 110
    q = text("l'app che avrei voluto", F('lora', 60), (90, 70, 40)); q2 = text('usare io.', F('lora', 60), (90, 70, 40))
    qx = W / 2 if v else lx
    put(c, q, qx, ty, 1, clamp((t - 1.8) / .4)); put(c, q2, qx, ty + 76, 1, clamp((t - 2.2) / .4))
    if t > 3.0:
        u = ease((t - 3.0) / .5); d = ImageDraw.Draw(c); w = q2.width * u; d.line((qx - q2.width / 2, ty + 120, qx - q2.width / 2 + w, ty + 120), fill=AMBER + (255,), width=10)
    return c
EV_APP = [(.0, whoosh(2, .7), .8), (.5, pop(620), .6), (.9, hit(), .6), (1.8, pop(900), .35), (2.2, pop(1000), .35), (3.0, rise(.5), .5), (3.6, chime(), .6)]

# 3 · un movimento in pochi secondi (processo, camera che scorre)
STEPS = [('dial', '1 · TOCCHI +'), ('add-cat', '2 · CATEGORIA'), ('add-sub', '3 · DETTAGLIO'), ('add-amt', '4 · SALVA')]
def s_pochi(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H); pw = 480 if v else 380; gap = pw + (90 if v else 120)
    if v:
        cam = inout((t - .4) / 4.6) * gap * 3
        for i, (n, lab) in enumerate(STEPS):
            x = W / 2 + i * gap - cam
            if -pw < x < W + pw:
                put(c, phone(n, pw), x, H * .55, 1, 1)
                put(c, text(lab, F('anton', 76), AMBER), x, H * .17, 1, 1)
    else:
        cam = inout((t - .3) / 4.8) * gap * 1.6
        for i, (n, lab) in enumerate(STEPS):
            x = W * .22 + i * gap - cam
            put(c, phone(n, pw), x, H * .58, 1, clamp((t - i * .25) / .3))
            put(c, text(lab, F('anton', 54), AMBER), x, H * .1, 1, clamp((t - i * .25) / .3))
    sec = min(5, int(t * 1.05) + 1) if t > .2 else 0
    clock = text('⏱ ' if False else '', F('anton', 10), WHITE)
    tm = text('0' + str(sec) + ' SECONDI' if sec < 10 else str(sec), F('anton', 64 if v else 56), WHITE)
    put(c, card(tm.width + 60, tm.height + 30, NAVY, AMBER), W / 2 if v else W * .86, H * .9 if v else H * .9, 1, 1)
    put(c, tm, W / 2 if v else W * .86, H * .9 if v else H * .9)
    return c
EV_POCHI = [(.2, whoosh(3, .4), .6)] + [(0.3 + i * 1.25, pop(650 + i * 120), .7) for i in range(4)] + [(t2, tick(), .3) for t2 in (1, 2, 3, 4, 5)] + [(5.2, ding(), .5)]

# 4 · un rimborso non è un guadagno (schermo diviso)
def s_rimborso(t, W, H):
    v = V(W, H); c = Image.new('RGBA', (W, H), WHITE + (255,)); d = ImageDraw.Draw(c)
    if v: d.rectangle((0, 0, W, H / 2), fill=(253, 236, 236, 255)); d.rectangle((0, H / 2, W, H), fill=(232, 247, 238, 255))
    else: d.rectangle((0, 0, W / 2, H), fill=(253, 236, 236, 255)); d.rectangle((W / 2, 0, W, H), fill=(232, 247, 238, 255))
    put(c, fit('UN RIMBORSO NON È UN GUADAGNO', 'anton', 84 if not v else 76, INK, W - 80), W / 2, H * .07 if not v else H * .05, back(t / .35), clamp(t / .15))
    def side(cx, cy, title, col, rows, verdict, good, t0):
        put(c, text(title, F('anton', 64), col), cx, cy - 230, 1, clamp((t - t0) / .3))
        for i, (k, a, b2) in enumerate(rows):
            u = clamp((t - t0 - .4 - i * .45) / .4); yy = cy - 120 + i * 105
            put(c, text(k, F('comf', 40), (70, 70, 70)), cx - 300, yy, 1, u, 'l')
            val = a if t < t0 + 1.6 + i * .2 else b2
            put(c, text(val, F('anton', 60), col if val == b2 and a != b2 else INK), cx + 300, yy, 1, u, 'r')
        tag = rrect((480, 90), 45, (col + (255,))); ImageDraw.Draw(tag).text((240, 45), verdict, font=F('anton', 48), fill=WHITE, anchor='mm')
        put(c, tag, cx, cy + 230, back((t - t0 - 2.2) / .35), clamp((t - t0 - 2.2) / .1))
    if v:
        side(W / 2, H * .28, 'COME ENTRATA', RED, [('Entrate', '1.850 €', '1.875 €'), ('Uscite', '1.519 €', '1.519 €'), ('Risparmio', '18%', '19%')], 'ENTRATE GONFIATE', False, .5)
        side(W / 2, H * .74, 'COME RIMBORSO', GREEN, [('Entrate', '1.850 €', '1.850 €'), ('Uscite', '1.519 €', '1.494 €'), ('Risparmio', '18%', '19%')], 'SPESA RIDOTTA', True, 2.6)
    else:
        side(W * .25, H * .55, 'COME ENTRATA', RED, [('Entrate', '1.850 €', '1.875 €'), ('Uscite', '1.519 €', '1.519 €'), ('Risparmio', '18%', '19%')], 'ENTRATE GONFIATE', False, .5)
        side(W * .75, H * .55, 'COME RIMBORSO', GREEN, [('Entrate', '1.850 €', '1.850 €'), ('Uscite', '1.519 €', '1.494 €'), ('Risparmio', '18%', '19%')], 'SPESA RIDOTTA', True, 2.6)
    return c
EV_RIMB = [(0, hit(), .6), (.5, pop(500), .5), (2.1, tick(1500), .4), (2.7, buzz(), .7), (2.6, pop(800), .5), (4.2, tick(2500), .4), (4.8, chime(), .7)]

# 5 · cinque conti: quante monete in ogni portafoglio? (fumetto)
def s_conti(t, W, H):
    c = bg_comic(W, H); v = V(W, H); s = 230 if v else 220
    pos = [(W * .2, H * .58), (W * .5, H * .5), (W * .8, H * .58), (W * .32, H * .78), (W * .68, H * .78)] if v else [(W * .12, H * .55), (W * .31, H * .47), (W * .5, H * .55), (W * .69, H * .47), (W * .88, H * .55)]
    cols = [AMBER, (120, 190, 255), (255, 140, 120), (150, 220, 150), (210, 170, 255)]
    for i, (x, y) in enumerate(pos):
        u = back((t - .2 - i * .22) / .35); wob = math.sin(t * 5 + i) * 6 * clamp((t - 2) / .5)
        put(c, wallet(s, cols[i]), x, y + wob, u, clamp((t - .2 - i * .22) / .1))
        put(c, text('CONTO ' + str(i + 1), F('anton', 40), INK), x, y + s * .62, 1, clamp((t - .4 - i * .22) / .2))
        if t > 2.0 + i * .12: put(c, text('?', F('anton', 120), RED, 6, WHITE), x + s * .35, y - s * .5, back((t - 2 - i * .12) / .3), 1)
    bw, bh = (900, 250) if v else (1050, 230)
    b = bubble(bw, bh, 'bl'); bd = ImageDraw.Draw(b)
    bd.text((bw / 2, bh / 2 - 34), 'Quante monete ci sono', font=F('comf', 58 if v else 60), fill=INK, anchor='mm'); bd.text((bw / 2, bh / 2 + 40), 'in ogni portafoglio?', font=F('comf', 58 if v else 60), fill=INK, anchor='mm')
    put(c, b, W / 2, H * .17 if v else H * .2, back((t - 1.2) / .35), clamp((t - 1.2) / .1))
    if t > 3.6:
        st = text('NON MI DICE NULLA', F('anton', 120 if not v else 100), WHITE, 10, INK).rotate(-6, expand=True, resample=Image.BICUBIC)
        put(c, st, W / 2, H * .42 if v else H * .84, 2 - ease((t - 3.6) / .2), 1)
    return c
EV_CONTI = [(.2 + i * .22, pop(500 + i * 90), .6) for i in range(5)] + [(1.2, whoosh(5, .4), .6), (2.0, coin(), .5), (2.4, coin(), .4), (3.6, stamp(), 1)]

# 6 · quattro pilastri, quattro scopi (grafici)
PIL4 = [('LIQUIDITÀ', 'vivere ogni giorno', BLUE, .55), ('EMERGENZA', 'gli imprevisti', ORANGE, .75), ('OBIETTIVI', 'quello che vuoi', TEAL, .45), ('INVESTIMENTI', 'il tuo futuro', LILAC, .95)]
def s_pilastri(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H); d = ImageDraw.Draw(c)
    put(c, text('4 PILASTRI', F('anton', 130 if v else 120), WHITE), W / 2, H * .09 if v else H * .1, back(t / .35), clamp(t / .15))
    put(c, text('4 SCOPI', F('anton', 130 if v else 120), AMBER), W / 2, H * .17 if v else H * .23, back((t - .4) / .35), clamp((t - .4) / .15))
    base = H * .78 if v else H * .8; maxh = H * .42 if v else H * .42; bw = W * .17 if v else W * .13; xs = [W * (.14 + i * .24) for i in range(4)] if v else [W * (.23 + i * .18) for i in range(4)]
    d.line((W * .05, base, W * .95, base), fill=(200, 210, 230, 255), width=3)
    for i, (n, sub, col, h) in enumerate(PIL4):
        u = ease((t - .9 - i * .35) / .7); hh = maxh * h * u; x = xs[i]
        d.rounded_rectangle((x - bw / 2, base - hh, x + bw / 2, base), 14, fill=col + (255,))
        tgt = base - maxh * h * 1.0
        if u > .2:
            for xx in range(int(x - bw / 2 - 10), int(x + bw / 2 + 10), 18): d.line((xx, tgt - 16, xx + 9, tgt - 16), fill=WHITE + (200,), width=3)
        put(c, fit(n, 'anton', 52 if not v else 44, WHITE, int(bw + 70)), x, base + 45, 1, clamp((t - 1.1 - i * .35) / .3))
        put(c, fit(sub, 'comf', 30 if not v else 26, (200, 210, 235), int(bw + 90)), x, base + 95, 1, clamp((t - 1.3 - i * .35) / .3))
    return c
EV_PIL = [(0, hit(), .6), (.4, pop(700), .5)] + [(.9 + i * .35, rise(.5), .5) for i in range(4)] + [(3.0, chime(), .5)]

# 7 · una volta al mese correggi i saldi (chiaro pulito)
def s_saldo(t, W, H):
    c = bg_cream(W, H); v = V(W, H)
    cal = Image.new('RGBA', (360, 380), (0, 0, 0, 0)); cd = ImageDraw.Draw(cal)
    cd.rounded_rectangle((0, 20, 359, 379), 30, fill=WHITE, outline=INK, width=6); cd.rounded_rectangle((0, 20, 359, 120), 30, fill=RED); cd.rectangle((0, 90, 359, 120), fill=RED)
    for x in (90, 270): cd.rounded_rectangle((x - 12, 0, x + 12, 60), 10, fill=INK)
    cd.text((180, 72), 'OGNI MESE', font=F('anton', 44), fill=WHITE, anchor='mm'); cd.text((180, 250), '1', font=F('anton', 190), fill=INK, anchor='mm')
    cx, cy = (W * .3, H * .3) if v else (W * .2, H * .45)
    put(c, shadow(cal), cx, cy, back((t - .2) / .4), clamp((t - .2) / .15))
    put(c, phone('pillar-liq', 480 if v else 400, (0, 0, 1080, 1700)), W * .62 if v else W * .5, H * .66 if v else H * .55, 1 - .05 * (1 - ease((t - .5) / .6)), clamp((t - .5) / .3))
    tx, ty = (W * .5, H * .08) if v else (W * .8, H * .32)
    put(c, fit('CORREGGI IL SALDO', 'anton', 88, INK, int(W * .9 if v else W * .36)), tx, ty, back((t - 1.2) / .35), clamp((t - 1.2) / .15))
    put(c, text('con quello vero della banca', F('lora', 48 if not v else 46), (90, 70, 40)), tx, ty + 90, 1, clamp((t - 1.8) / .4))
    if t > 3.2:
        put(c, check(200, GREEN, (t - 3.2) / .6), tx if not v else W * .25, ty + 280 if not v else H * .6, back((t - 3.2) / .3), 1)
        put(c, text('APP IN PARI', F('anton', 72), GREEN), tx if not v else W * .25, ty + 440 if not v else H * .6 + 160, 1, clamp((t - 3.7) / .3))
    return c
EV_SALDO = [(.2, pop(600), .6), (.5, whoosh(6, .4), .5), (1.2, pop(800), .5), (3.2, ding(1568), .6), (3.75, chime(), .5)]

# 8 · un budget deciso prima è una gabbia (fumetto)
def s_gabbia(t, W, H):
    c = bg_comic(W, H); v = V(W, H); d = ImageDraw.Draw(c)
    cx, cy = (W / 2, H * .5) if v else (W * .35, H * .55); gw, gh = (600, 700) if v else (520, 600)
    u = ease((t - .2) / .5); top = cy - gh / 2 - (1 - u) * H
    put(c, text('€', F('anton', 300), AMBER, 10, INK), cx, cy + 40, back((t) / .4), clamp(t / .1))
    d.arc((cx - gw / 2, top - 120, cx + gw / 2, top + 120), 180, 360, fill=INK, width=14)
    for i in range(7): x = cx - gw / 2 + i * gw / 6; d.line((x, top, x, top + gh), fill=INK, width=12)
    d.line((cx - gw / 2 - 20, top + gh, cx + gw / 2 + 20, top + gh), fill=INK, width=20); d.line((cx - gw / 2, top + 30, cx + gw / 2, top + 30), fill=INK, width=10)
    nx, ny = (W / 2, H * .14) if v else (W * .74, H * .32)
    note = Image.new('RGBA', (560, 300), (0, 0, 0, 0)); nd = ImageDraw.Draw(note); nd.rectangle((0, 0, 559, 299), fill=(255, 238, 140), outline=INK, width=6)
    nd.text((280, 90), 'BUDGET RISTORANTE', font=F('anton', 54), fill=INK, anchor='mm'); nd.text((280, 190), '200 € al mese', font=F('comf', 52), fill=INK, anchor='mm')
    put(c, note.rotate(4, expand=True, resample=Image.BICUBIC), nx, ny, back((t - 1.0) / .35), clamp((t - 1.0) / .1))
    if t > 2.4: put(c, text('SALTATO', F('anton', 120), RED, 8, WHITE).rotate(-14, expand=True, resample=Image.BICUBIC), nx, ny, 2.2 - 1.2 * ease((t - 2.4) / .18), 1)
    if t > 3.6:
        b = bubble(880, 210, 'br'); ImageDraw.Draw(b).text((440, 105), 'Una gabbia. E poi i sensi di colpa.', font=F('comf', 40), fill=INK, anchor='mm')
        put(c, b, W / 2 if v else W * .7, H * .86 if v else H * .74, back((t - 3.6) / .35), 1)
    return c
EV_GABBIA = [(0, pop(400), .5), (.25, clang(), .8), (1.0, whoosh(7, .35), .5), (2.4, stamp(), 1), (3.6, pop(900), .5)]

# 9 · registri, guardi i fatti, decidi dopo (processo, camera)
P3 = [('1', 'REGISTRI', 'ogni movimento, al centesimo'), ('2', 'GUARDI I FATTI', 'dove vanno davvero i soldi'), ('3', 'DECIDI DOPO', 'cosa cambiare, e perché')]
def s_dopo(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H); d = ImageDraw.Draw(c)
    if v:
        for i, (n, a, b2) in enumerate(P3):
            y = H * (.2 + i * .3); u = back((t - .3 - i * 1.1) / .4)
            cc = card(int(W * .8), 330, NAVY2, AMBER); cdd = ImageDraw.Draw(cc); cdd.ellipse((40, 95, 180, 235), fill=AMBER); cdd.text((110, 165), n, font=F('anton', 90), fill=NAVY, anchor='mm')
            cdd.text((220, 120), a, font=F('anton', 76), fill=WHITE); cdd.text((222, 220), b2, font=F('comf', 34), fill=(200, 210, 235))
            put(c, cc, W / 2, y, u, clamp((t - .3 - i * 1.1) / .1))
            if i < 2 and t > .8 + i * 1.1: d.line((W / 2, y + 170, W / 2, y + 170 + (H * .3 - 340) * ease((t - .8 - i * 1.1) / .4)), fill=AMBER + (255,), width=10)
    else:
        cam = inout((t - .5) / 4.5) * W * .35
        for i, (n, a, b2) in enumerate(P3):
            x = W * (.25 + i * .38) - cam; u = back((t - .3 - i * 1.1) / .4)
            cc = card(600, 420, NAVY2, AMBER); cdd = ImageDraw.Draw(cc); cdd.ellipse((240, 30, 360, 150), fill=AMBER); cdd.text((300, 90), n, font=F('anton', 80), fill=NAVY, anchor='mm')
            cdd.text((300, 230), a, font=F('anton', 72), fill=WHITE, anchor='mm'); cdd.text((300, 320), b2, font=F('comf', 32), fill=(200, 210, 235), anchor='mm')
            put(c, cc, x, H * .55, u, clamp((t - .3 - i * 1.1) / .1))
            if i < 2 and t > .8 + i * 1.1:
                x0 = x + 310; x1 = x0 + (W * .38 - 620) * ease((t - .8 - i * 1.1) / .4); d.line((x0, H * .55, x1, H * .55), fill=AMBER + (255,), width=10)
        put(c, text('NIENTE BUDGET', F('anton', 90), AMBER), W / 2, H * .13, back((t - 4.2) / .35), clamp((t - 4.2) / .1))
    return c
EV_DOPO = [(.3 + i * 1.1, pop(600 + i * 150), .7) for i in range(3)] + [(.8, whoosh(9, .4), .4), (1.9, whoosh(10, .4), .4), (4.2, hit(), .7)]

# 10 · categorie → sottocategorie → movimenti (mockup)
AN3 = [('an1', 'CATEGORIE'), ('an2', 'SOTTOCATEGORIE'), ('an3', 'MOVIMENTI')]
def s_analisi(t, W, H):
    c = bg_cream(W, H); v = V(W, H)
    put(c, text('ANALISI', F('anton', 120 if not v else 130), INK), W / 2 if v else W * .16, H * .07 if v else H * .5, back(t / .35), clamp(t / .15))
    if not v: put(c, text('dal totale al singolo caffè', F('lora', 40), (90, 70, 40)), W * .16, H * .5 + 90, 1, clamp((t - .5) / .4))
    for i, (n, lab) in enumerate(AN3):
        t0 = .4 + i * 1.3; u = ease((t - t0) / .5)
        if v: x, y, w = W * (.3 + i * .2), H * (.4 + i * .09), 440
        else: x, y, w = W * (.42 + i * .2), H * (.53 + i * .03), 380
        put(c, phone(n, w), x, y + (1 - u) * 300, 1, clamp((t - t0) / .25))
        put(c, text(lab, F('anton', 46), AMBER, 6, INK), x, y - (w * 1.05 if v else w * 1.0), 1, clamp((t - t0 - .3) / .3))
    if t > 4.6:
        b = bubble(720, 170, 'bl'); ImageDraw.Draw(b).text((360, 85), 'Ecco dove scappano i soldi', font=F('comf', 40), fill=INK, anchor='mm')
        put(c, b, W * .5 if v else W * .17, H * .9 if v else H * .2, back((t - 4.6) / .35), 1)
    return c
EV_AN = [(0, pop(500), .5)] + [(.4 + i * 1.3, whoosh(11 + i, .35), .6) for i in range(3)] + [(.7 + i * 1.3, tick(2000 + i * 300), .4) for i in range(3)] + [(4.6, ding(), .5)]

# 11 · un'analisi, non un elenco (schermo diviso)
def s_pdf(t, W, H):
    v = V(W, H); c = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(c)
    A = (0, 0, W, H / 2) if v else (0, 0, W / 2, H); B = (0, H / 2, W, H) if v else (W / 2, 0, W, H)
    d.rectangle(A, fill=(225, 225, 225, 255)); d.rectangle(B, fill=NAVY + (255,))
    ax, ay = (A[0] + A[2]) / 2, (A[1] + A[3]) / 2; bx, by = (B[0] + B[2]) / 2, (B[1] + B[3]) / 2
    put(c, text('ELENCO', F('anton', 90), (110, 110, 110)), ax, A[1] + 90, 1, clamp(t / .3))
    lst = Image.new('RGBA', (560, 560 if not v else 520), (255, 255, 255, 255)); ld = ImageDraw.Draw(lst)
    for i in range(12): yy = 30 + i * 44; ld.rectangle((30, yy, 330, yy + 16), fill=(205, 205, 205)); ld.rectangle((420, yy, 530, yy + 16), fill=(205, 205, 205))
    put(c, lst, ax, ay + 40, 1, clamp((t - .2) / .3))
    if t > 1.2: put(c, text('quello che hai già', F('lora', 44), (100, 100, 100)), ax, A[3] - 70, 1, clamp((t - 1.2) / .4))
    put(c, text('ANALISI', F('anton', 90), AMBER), bx, B[1] + 90, 1, clamp((t - 1.6) / .3))
    pg = img('pdf-1'); pw = 600 if not v else 640; pg = pg.resize((pw, int(pg.height * pw / pg.width)), Image.LANCZOS)
    vis = int(pw * (1.32 if not v else 1.08)); sc = int((pg.height - vis) * inout((t - 2.2) / 3.5)); crop = pg.crop((0, sc, pw, sc + vis))
    put(c, shadow(crop), bx, by + 60, 0.9 + 0.1 * ease((t - 1.8) / .5), clamp((t - 1.8) / .3))
    return c
EV_PDF = [(0, pop(400), .4), (1.2, buzz(), .3), (1.6, hit(), .6), (1.8, whoosh(14, .5), .5), (3.5, tick(), .3), (4.4, tick(), .3), (5.1, chime(), .5)]

# 12 · la mini analisi in numeri (grafici)
def donut_img(s, segs, prog):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); tot = sum(v2 for _, v2 in segs); a0 = -90; lim = -90 + 360 * prog
    for col, v2 in segs:
        a1 = a0 + v2 / tot * 360
        if a0 < lim: d.pieslice((0, 0, s - 1, s - 1), a0, min(a1, lim), fill=col)
        a0 = a1
    d.ellipse((s * .22, s * .22, s * .78, s * .78), fill=NAVY); return im
def s_numeri(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H)
    dx, dy, ds = (W / 2, H * .27, 560) if v else (W * .27, H * .52, 600)
    put(c, donut_img(ds, [(BLUE, 66), (AMBER, 12), (GREEN, 22)], ease((t - .2) / 1.2)), dx, dy, back(t / .4), clamp(t / .15))
    n = int(22 * ease((t - .3) / 1.1)); put(c, text(str(n) + '%', F('anton', 120), WHITE), dx, dy - 20); put(c, text('risparmiato', F('comf', 36), (200, 210, 235)), dx, dy + 70)
    items = [('MESE CON PIÙ RISPARMIO', 'Agosto', GREEN), ('VOCE IN CRESCITA', 'Bar e caffè', RED), ('FONDO DI EMERGENZA', '1,5 mesi', AMBER)]
    for i, (a, b2, col) in enumerate(items):
        t0 = 1.6 + i * .8; u = back((t - t0) / .35)
        cw = int(W * .84) if v else 820; cc = card(cw, 190, NAVY2, col); cd = ImageDraw.Draw(cc)
        cd.text((40, 40), a, font=F('comf', 34), fill=(200, 210, 235)); cd.text((40, 92), b2, font=F('anton', 72), fill=WHITE)
        x, y = (W / 2, H * (.55 + i * .13)) if v else (W * .7, H * (.27 + i * .23))
        put(c, cc, x, y, u, clamp((t - t0) / .1))
    return c
EV_NUM = [(0, hit(), .5), (.2, rise(1.1), .5)] + [(1.6 + i * .8, pop(700 + i * 120), .7) for i in range(3)] + [(4.2, chime(), .5)]

# 13 · e se…? la data si avvicina (mockup)
def s_ese(t, W, H):
    c = bg_cream(W, H); v = V(W, H)
    put(c, text('E se…?', F('lora', 140 if not v else 150), INK), W / 2 if v else W * .2, H * .08 if v else H * .2, back(t / .35), clamp(t / .15))
    sw = clamp((t - 2.2) / .5)
    px, py, pw = (W * .5, H * .52, 560) if v else (W * .5, H * .55, 440)
    put(c, phone('whatif0', pw, (0, 0, 1080, 1700)), px, py, 1, (1 - sw) * clamp((t - .3) / .3))
    if sw > 0: put(c, phone('whatif1', pw, (0, 0, 1080, 1700)), px, py, 1, sw)
    dx, dy = (W / 2, H * .9) if v else (W * .82, H * .45)
    lab = 'APRILE 2028' if t < 2.4 else 'GIUGNO 2027'; col = INK if t < 2.4 else GREEN
    flip = 1 - abs(math.sin(clamp((t - 2.2) / .4) * math.pi)) * .9 if 2.2 < t < 2.6 else 1
    put(c, text('ARRIVI A', F('comf', 40), (90, 90, 90)), dx, dy - 100, 1, clamp((t - .6) / .3))
    put(c, text(lab, F('anton', 100), col), dx, dy, flip, clamp((t - .6) / .3))
    if t > 3.0:
        tag = rrect((360, 90), 45, GREEN + (255,)); ImageDraw.Draw(tag).text((180, 45), '10 MESI PRIMA', font=F('anton', 50), fill=WHITE, anchor='mm')
        put(c, tag, dx, dy + 110, back((t - 3.0) / .3), 1)
    if t > 3.8 and not v: put(c, text('colazione a casa, metà delle volte', F('lora', 40), (90, 70, 40)), W * .2, H * .2 + 120, 1, clamp((t - 3.8) / .4))
    return c
EV_ESE = [(0, pop(500), .5), (.3, whoosh(15, .4), .5), (2.2, whoosh(16, .3), .6), (2.4, pop(1100), .6), (3.0, chime(), .7)]

# 14 · la palestra: 21 tappe (blu notte, card)
def s_palestra(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H); d = ImageDraw.Draw(c)
    n = int(21 * ease((t - .5) / 2.6))
    pts = []
    for i in range(21):
        if v: row, col = divmod(i, 3); x = W * (.25 + (col if row % 2 == 0 else 2 - col) * .25); y = H * (.25 + row * .085)
        else: row, col = divmod(i, 7); x = W * (.12 + (col if row % 2 == 0 else 6 - col) * .085); y = H * (.35 + row * .22)
        pts.append((x, y))
    for i in range(20): d.line((pts[i], pts[i + 1]), fill=(AMBER if i + 1 < n else GRID) + (255,), width=8)
    for i, (x, y) in enumerate(pts):
        on = i < n; r = 34 if not v else 38
        d.ellipse((x - r, y - r, x + r, y + r), fill=(AMBER if on else NAVY2) + (255,), outline=AMBER + (255,), width=4)
        d.text((x, y), str(i + 1), font=F('anton', 34), fill=NAVY if on else WHITE, anchor='mm')
    put(c, text(str(max(n, 0)) + ' TAPPE', F('anton', 120), WHITE), W / 2 if v else W * .3, H * .1 if v else H * .14, 1, clamp(t / .3))
    if not v: put(c, phone('gym', 360, (0, 0, 1080, 1500)), W * .86, H * .55, 1, clamp((t - 1.0) / .4))
    tags = ['letture brevi', 'azioni concrete', 'sfide', 'respirazione guidata']
    for i, s2 in enumerate(tags):
        t0 = 3.3 + i * .35; tg = text(s2, F('comf', 38), NAVY); bb = rrect((tg.width + 50, tg.height + 30), 30, AMBER + (255,)); bb.alpha_composite(tg, (25, 15))
        x, y = (W * (.3 if i % 2 == 0 else .7), H * (.88 + (i // 2) * .055)) if v else (W * (.12 + i * .17), H * .9)
        put(c, bb, x, y, back((t - t0) / .3), clamp((t - t0) / .1))
    return c
EV_PAL = [(0, hit(), .5)] + [(.5 + i * .13, tick(1500 + i * 40), .25) for i in range(21)] + [(3.3 + i * .35, pop(800 + i * 100), .6) for i in range(4)]

# 15 · gratis, e i dati restano tuoi (chiaro pulito)
def s_gratis(t, W, H):
    c = bg_cream(W, H); v = V(W, H)
    put(c, phone('lock', 480 if v else 400, (0, 0, 1080, 1700)), W * .5 if v else W * .27, H * .38 if v else H * .55, 1, clamp(t / .4))
    put(c, padlock(200), W * .8 if v else W * .45, H * .14 if v else H * .25, back((t - .5) / .35), 1)
    lines = [('GRATIS', INK), ('NIENTE PUBBLICITÀ', INK), ('I DATI RESTANO SUL TUO TELEFONO', AMBER)]
    for i, (s2, col) in enumerate(lines):
        t0 = 1.2 + i * .7; x, y = (W / 2, H * (.72 + i * .085)) if v else (W * .72, H * (.32 + i * .17))
        put(c, fit(s2, 'anton', 92, col if col != AMBER else (200, 120, 0), int(W * .9 if v else W * .5)), x, y, back((t - t0) / .35), clamp((t - t0) / .1))
        put(c, check(70, GREEN, (t - t0 - .2) / .4), x - (fit(s2, 'anton', 92, INK, int(W * .9 if v else W * .5)).width / 2 + 60), y, 1, clamp((t - t0 - .1) / .2))
    if t > 3.6: put(c, text('niente trading, niente consigli di investimento', F('lora', 40 if not v else 36), (90, 70, 40)), W / 2 if v else W * .72, H * .97 if v else H * .84, 1, clamp((t - 3.6) / .4))
    return c
EV_GRATIS = [(0, whoosh(17, .5), .5), (.5, clang(), .4)] + [(1.2 + i * .7, pop(700 + i * 120), .7) for i in range(3)] + [(1.5 + i * .7, ding(1568 + i * 200), .35) for i in range(3)]

# 16 · scrivimi TEST (blu notte, finale)
def s_test(t, W, H):
    c = bg_navy(W, H, t); v = V(W, H)
    lc = logo_card(200 if v else 150)
    put(c, lc, W / 2 if v else W * .12, H * .13 if v else H * .5, ease(t / .4), clamp(t / .3))
    put(c, text('HAI ANDROID?', F('anton', 110), WHITE), W / 2, H * .3 if v else H * .16, back((t - .4) / .35), clamp((t - .4) / .1))
    put(c, text('SCRIVIMI', F('anton', 120), WHITE), W / 2, H * .41 if v else H * .36, back((t - .9) / .35), clamp((t - .9) / .1))
    p = 1 + 0.05 * math.sin((t - 1.6) * 2 * math.pi) if t > 1.6 else back((t - 1.3) / .3)
    bx = rrect((640, 230), 60, AMBER2 + (255,)); ImageDraw.Draw(bx).text((320, 115), 'TEST', font=F('anton', 170), fill=NAVY, anchor='mm')
    put(c, bx, W / 2, H * .56 if v else H * .6, p if t > 1.3 else 0, 1)
    put(c, text('e dammi i tuoi suggerimenti', F('lora', 56), (220, 225, 240)), W / 2, H * .7 if v else H * .84, 1, clamp((t - 2.6) / .4))
    return c
EV_TEST = [(0, whoosh(18, .5), .5), (.4, pop(600), .6), (.9, hit(), .7), (1.3, pop(1000), .6), (2.6, chime(), .7)]

LONG = [('01_elenco_lungo_preciso_muto', 5.8, s_elenco, EV_ELENCO), ('02_app_che_avrei_voluto', 5.6, s_app, EV_APP), ('03_movimento_in_pochi_secondi', 6.2, s_pochi, EV_POCHI),
        ('04_rimborso_non_guadagno', 6.4, s_rimborso, EV_RIMB), ('05_fumetto_cinque_conti', 6.0, s_conti, EV_CONTI), ('06_quattro_pilastri', 5.8, s_pilastri, EV_PIL),
        ('07_correggi_il_saldo', 5.6, s_saldo, EV_SALDO), ('08_fumetto_budget_gabbia', 6.0, s_gabbia, EV_GABBIA), ('09_registri_guardi_decidi', 6.2, s_dopo, EV_DOPO),
        ('10_analisi_categorie_movimenti', 6.0, s_analisi, EV_AN), ('11_analisi_non_elenco', 6.4, s_pdf, EV_PDF), ('12_mini_analisi_numeri', 5.8, s_numeri, EV_NUM),
        ('13_e_se_arrivi_prima', 5.8, s_ese, EV_ESE), ('14_palestra_21_tappe', 5.8, s_palestra, EV_PAL), ('15_gratis_dati_tuoi', 5.8, s_gratis, EV_GRATIS), ('16_scrivimi_test', 5.6, s_test, EV_TEST)]
SHORT = [('01_elenco_muto', 5.8, s_elenco, EV_ELENCO), ('02_quattro_pilastri', 5.8, s_pilastri, EV_PIL), ('03_budget_gabbia', 6.0, s_gabbia, EV_GABBIA),
         ('04_analisi_non_elenco', 6.4, s_pdf, EV_PDF), ('05_palestra_21_tappe', 5.8, s_palestra, EV_PAL), ('06_scrivimi_test', 5.6, s_test, EV_TEST)]
