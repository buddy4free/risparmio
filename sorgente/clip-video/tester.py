"""Reel verticali (Instagram / TikTok) per la ricerca dei tester: solo testo a schermo ed effetti sonori."""
import os, sys, shutil
from concurrent.futures import ProcessPoolExecutor
from scenes import *
from b4f import mix, encode

W, H = 1080, 1920
BROWN = (90, 70, 40)

def title(c, s, y, t, t0, size=130, col=WHITE, maxw=980, **kw):
    put(c, fit(s, 'anton', size, col, maxw, **kw), W / 2, y, back((t - t0) / .35), clamp((t - t0) / .1))

def pill(s, fg=NAVY, bgc=AMBER2, size=46, font='anton'):
    tx = text(s, F(font, size), fg); b = rrect((tx.width + 70, tx.height + 40), (tx.height + 40) // 2, bgc + (255,)); b.alpha_composite(tx, (35, 20)); return b

# ---------- pezzi comuni ----------
def a_creato(t):  # blu notte: "ho creato un'app" + telefono
    c = bg_navy(W, H, t)
    put(c, logo_card(220), W / 2, H * .1, back(t / .4), clamp(t / .2))
    title(c, 'HO CREATO', H * .22, t, .3, 150)
    title(c, "UN'APP.", H * .32, t, .7, 190, AMBER)
    put(c, phone('home', 560), W / 2, H * .72 + (1 - ease((t - .9) / .7)) * H * .5, 1, clamp((t - .9) / .2))
    return c
EV_CREATO = [(0, whoosh(31, .5), .6), (.3, pop(620), .6), (.7, hit(), .8), (.9, whoosh(32, .6), .5)]

def a_aiuto(t):  # chiaro: "mi serve il tuo aiuto" + 20 posti tester
    c = bg_cream(W, H)
    title(c, 'MI SERVE', H * .12, t, .1, 140, INK)
    title(c, 'IL TUO AIUTO', H * .21, t, .4, 140, (200, 120, 0))
    put(c, text('cerco', F('lora', 64), BROWN), W / 2, H * .32, 1, clamp((t - 1.0) / .3))
    title(c, '20 TESTER ANDROID', H * .39, t, 1.2, 120, INK)
    d = ImageDraw.Draw(c); r = 54
    for i in range(20):
        t0 = 1.8 + i * .07; u = back((t - t0) / .3)
        if u <= 0: continue
        x = W * .5 + (i % 5 - 2) * 180; y = H * .52 + (i // 5) * 175; rr = r * u
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 255, 255), outline=INK + (255,), width=6)
        if u > .6:  # sagoma
            d.ellipse((x - 15 * u, y - 30 * u, x + 15 * u, y), fill=(200, 200, 200, 255)); d.pieslice((x - 30 * u, y + 2, x + 30 * u, y + 56 * u), 180, 360, fill=(200, 200, 200, 255))
    if t > 3.6: put(c, text('il prossimo posto è tuo?', F('lora', 60), BROWN), W / 2, H * .92, 1, clamp((t - 3.6) / .4))
    return c
EV_AIUTO = [(.1, pop(560), .6), (.4, pop(700), .6), (1.2, hit(), .6)] + [(1.8 + i * .07, tick(1500 + i * 45), .3) for i in range(20)] + [(3.6, ding(1175), .4)]

def a_giorni(t):  # fumetto: 14 giorni, calendario che si spunta
    c = bg_comic(W, H)
    b = bubble(860, 230, 'bl'); bd = ImageDraw.Draw(b)
    bd.text((430, 80), 'La tieni sul telefono', font=F('comf', 56), fill=INK, anchor='mm'); bd.text((430, 160), 'per 14 giorni.', font=F('comf', 56), fill=INK, anchor='mm')
    put(c, b, W / 2, H * .13, back((t - .1) / .35), clamp((t - .1) / .1))
    cw, ch = 860, 700; cal = rrect((cw, ch), 40, WHITE + (255,), INK + (255,), 8); cd = ImageDraw.Draw(cal)
    cd.rounded_rectangle((0, 0, cw - 1, 120), 40, fill=RED + (255,)); cd.rectangle((0, 60, cw - 1, 120), fill=RED + (255,)); cd.line((0, 120, cw, 120), fill=INK, width=8)
    cd.text((cw / 2, 62), '14 GIORNI', font=F('anton', 76), fill=WHITE, anchor='mm')
    n = int(clamp((t - 1.0) / 2.4) * 14 + .0001)
    for i in range(14):
        x = 70 + (i % 7) * 120 + 0; y = 200 + (i // 7) * 230
        cd.rounded_rectangle((x - 50, y - 50, x + 50, y + 50 + 60), 18, outline=INK, width=5, fill=(250, 250, 250))
        cd.text((x, y + 5), str(i + 1), font=F('anton', 56), fill=INK, anchor='mm')
        if i < n: cd.line((x - 34, y - 20, x - 6, y + 30), fill=GREEN, width=12); cd.line((x - 6, y + 30, x + 40, y - 40), fill=GREEN, width=12)
    put(c, shadow(cal), W / 2, H * .52, back((t - .5) / .4), clamp((t - .5) / .2))
    if t > 3.6:
        st = text('ANCHE SOLO PER SEGNARE', F('anton', 78), WHITE, 8, INK).rotate(-4, expand=True, resample=Image.BICUBIC)
        st2 = text('QUALCHE SPESA', F('anton', 96), AMBER, 8, INK).rotate(-4, expand=True, resample=Image.BICUBIC)
        put(c, st, W / 2, H * .83, 2 - ease((t - 3.6) / .2), 1); put(c, st2, W / 2, H * .9, 2 - ease((t - 3.9) / .2), clamp((t - 3.9) / .05))
    return c
EV_GIORNI = [(.1, whoosh(33, .4), .6), (.5, pop(500), .5)] + [(1.0 + i * 2.4 / 14, pop(900 + i * 40), .35) for i in range(14)] + [(3.6, stamp(), .9), (3.9, stamp(), .7)]

def a_cta(t):  # blu notte: hai android? scrivimi TEST
    c = bg_navy(W, H, t)
    put(c, logo_card(210), W / 2, H * .11, ease(t / .4), clamp(t / .3))
    title(c, 'HAI ANDROID?', H * .27, t, .3, 130)
    title(c, 'SCRIVIMI', H * .38, t, .8, 140)
    p = 1 + 0.05 * math.sin((t - 1.5) * 2 * math.pi) if t > 1.5 else back((t - 1.2) / .3)
    bx = rrect((700, 250), 70, AMBER2 + (255,)); ImageDraw.Draw(bx).text((350, 125), 'TEST', font=F('anton', 190), fill=NAVY, anchor='mm')
    put(c, bx, W / 2, H * .53, p if t > 1.2 else 0, 1)
    put(c, text('in direct  ↓', F('comf', 60), (220, 225, 240)), W / 2, H * .65, 1, clamp((t - 2.0) / .3))
    put(c, text('Buddy4Free Risparmio · gratis, senza pubblicità', F('lora', 44), (200, 205, 225)), W / 2, H * .9, 1, clamp((t - 2.6) / .4))
    return c
EV_CTA = [(0, whoosh(34, .5), .5), (.3, pop(600), .6), (.8, hit(), .7), (1.2, pop(1000), .6), (2.0, ding(1318), .4), (2.6, chime(), .7)]

# ---------- reel 2: cosa ci guadagni ----------
def b_prima(t):  # chiaro: provala prima di tutti, telefoni a ventaglio
    c = bg_cream(W, H)
    title(c, 'PROVALA', H * .1, t, .1, 150, INK)
    title(c, 'PRIMA DI TUTTI', H * .19, t, .45, 130, (200, 120, 0))
    for k, (nm, dx, rot, t0) in enumerate([('stats', -300, 9, .9), ('pillars', 300, -9, 1.1), ('home', 0, 0, 1.3)]):
        ph = phone(nm, 470).rotate(rot, expand=True, resample=Image.BICUBIC)
        put(c, ph, W / 2 + dx * ease((t - t0) / .6), H * .62 + (1 - ease((t - t0) / .6)) * 900 + abs(dx) * .12, 1, clamp((t - t0) / .2))
    if t > 3.0: put(c, pill('PRIMA DEL PLAY STORE', WHITE, INK, 50), W / 2, H * .93, back((t - 3.0) / .35), 1)
    return c
EV_PRIMA = [(.1, pop(600), .6), (.45, hit(), .6), (.9, whoosh(41, .4), .5), (1.1, whoosh(42, .4), .5), (1.3, whoosh(43, .4), .6), (3.0, pop(1100), .6)]

IDEE = [('"Dove ricontrollo i ricorrenti?"', 'rec', 'RICORRENTI'), ('"Le categorie in elenco?"', 'add-list', 'ELENCO O GRIGLIA'), ('"Riordinare è scomodo"', 'cats-ord', 'TRASCINA E SPOSTA')]
def b_idee(t):  # blu notte: le tue idee diventano funzioni (idee vere dei primi test)
    c = bg_navy(W, H, t)
    title(c, 'LE TUE IDEE', H * .08, t, .05, 130)
    title(c, 'DIVENTANO FUNZIONI', H * .16, t, .35, 110, AMBER)
    k = min(2, int(max(0, t - .9) / 1.65)); lt = t - .9 - k * 1.65
    q, shot, lab = IDEE[k]
    bb = card(940, 150, (245, 242, 232), None, 40); ImageDraw.Draw(bb).text((470, 75), q, font=F('lora', 52), fill=INK, anchor='mm')
    put(c, bb, W / 2, H * .27, back(lt / .3), clamp(lt / .1))
    put(c, text('↓', F('anton', 90), AMBER), W / 2, H * .35, 1, clamp((lt - .3) / .15))
    put(c, phone(shot, 520), W / 2, H * .66 + (1 - ease((lt - .35) / .45)) * 300, 1, clamp((lt - .35) / .2))
    put(c, pill(lab, NAVY, AMBER2, 54), W / 2, H * .43, back((lt - .6) / .3), 1)
    return c
EV_IDEE = [(.05, pop(600), .6), (.35, hit(), .7)] + sum([[(.9 + k * 1.65, whoosh(44 + k, .35), .5), (1.25 + k * 1.65, pop(800), .5), (1.5 + k * 1.65, ding(1568), .35)] for k in range(3)], [])

def b_gratis(t):  # chiaro: gratis per sempre, tre spunte
    c = bg_cream(W, H)
    put(c, padlock(220), W / 2, H * .13, back(t / .35), 1)
    title(c, 'GRATIS.', H * .27, t, .3, 170, INK)
    title(c, 'PER SEMPRE.', H * .36, t, .7, 150, (200, 120, 0))
    for i, s2 in enumerate(['NIENTE PUBBLICITÀ', 'NIENTE ABBONAMENTI', 'I DATI RESTANO SUL TUO TELEFONO']):
        t0 = 1.4 + i * .6; y = H * (.52 + i * .1); im = fit(s2, 'anton', 76, INK, 820)
        put(c, check(80, GREEN, (t - t0 - .15) / .35), W / 2 - im.width / 2 - 70, y, 1, clamp((t - t0) / .15))
        put(c, im, W / 2 + 40, y, back((t - t0) / .35), clamp((t - t0) / .1))
    if t > 3.4: put(c, text('niente trading, niente consigli di investimento', F('lora', 44), BROWN), W / 2, H * .9, 1, clamp((t - 3.4) / .4))
    return c
EV_GRATIS2 = [(0, clang(), .4), (.3, hit(), .7), (.7, pop(800), .6)] + [(1.4 + i * .6, pop(700 + i * 120), .6) for i in range(3)] + [(1.6 + i * .6, ding(1568 + i * 200), .35) for i in range(3)]

# ---------- reel 3: come funziona in 3 passi ----------
def c_titolo(t):  # blu notte con glitch
    c = bg_navy(W, H, t)
    title(c, 'VUOI FARE', H * .3, t, .1, 140)
    title(c, 'IL TESTER?', H * .4, t, .45, 170, AMBER)
    g = (1 - clamp((t - 1.0) / .4)) if t > 1.0 else 0
    m = text('3 PASSI', F('anton', 230), WHITE)
    put(c, glitch(m, g, int(t * 30)), W / 2, H * .58, back((t - 1.0) / .3), clamp((t - 1.0) / .1))
    if t > 1.8: put(c, text('e ci vuole un minuto', F('lora', 60), (220, 225, 240)), W / 2, H * .7, 1, clamp((t - 1.8) / .4))
    return c
EV_TIT = [(.1, pop(600), .6), (.45, hit(), .8), (1.0, glitchs(5), 1), (1.02, hit(), .6), (1.8, ding(1175), .35)]

def dm(s, me=True, w=760):
    b = rrect((w, 130), 50, (AMBER2 if me else (235, 235, 240)) + (255,)); ImageDraw.Draw(b).text((w / 2, 65), s, font=F('comf', 50), fill=NAVY if me else INK, anchor='mm'); return b
def c_passi(t):  # chiaro, la camera scorre giù tra i tre passi
    c = bg_cream(W, H)
    cam = 0
    def Y(y): return y - cam
    steps = [('1', 'SCRIVIMI TEST', .2), ('2', 'MANDAMI LA TUA GMAIL', 2.0), ('3', 'INSTALLA E TIENILA 14 GIORNI', 4.0)]
    for i, (n, lab, t0) in enumerate(steps):
        y0 = 360 + i * 560
        circ = Image.new('RGBA', (150, 150), (0, 0, 0, 0)); ImageDraw.Draw(circ).ellipse((0, 0, 149, 149), fill=AMBER + (255,)); ImageDraw.Draw(circ).text((75, 78), n, font=F('anton', 96), fill=NAVY, anchor='mm')
        put(c, circ, 140, Y(y0), back((t - t0) / .35), 1)
        put(c, fit(lab, 'anton', 84, INK, 760), 250, Y(y0), 1, clamp((t - t0 - .1) / .2), 'l')
        if i < 2: ImageDraw.Draw(c).line((140, Y(y0 + 90), 140, Y(y0 + 470)), fill=(220, 200, 160, 255), width=8)
    # 1 · messaggio diretto
    put(c, dm('TEST'), W * .58, Y(530), back((t - .6) / .3), 1)
    put(c, dm('Grazie!! Mi mandi la tua Gmail?', False, 860), W * .52, Y(700), back((t - 1.1) / .3), 1)
    # 2 · la gmail (oscurata)
    put(c, dm('••••••••@gmail.com'), W * .58, Y(1090), back((t - 2.5) / .3), 1)
    put(c, text('la uso solo per il test, poi la cancello', F('lora', 44), BROWN), W * .55, Y(1230), 1, clamp((t - 2.9) / .3))
    # 3 · il pulsante del Play Store
    bt = rrect((620, 120), 30, (1, 135, 95, 255)); ImageDraw.Draw(bt).text((310, 60), 'Diventa un tester', font=F('comf', 50), fill=WHITE, anchor='mm')
    p = 1 + .04 * math.sin((t - 4.8) * 6) if t > 4.8 else back((t - 4.4) / .3)
    put(c, bt, W * .55, Y(1660), p if t > 4.4 else 0, 1)
    put(c, text('poi "Scarica" e la tieni sul telefono', F('lora', 44), BROWN), W * .55, Y(1790), 1, clamp((t - 5.0) / .3))
    return c
EV_PASSI = [(.2, pop(650), .6), (.6, pop(1100), .6), (1.1, pop(800), .5), (1.6, tick(1800), .3), (2.0, pop(650), .6), (2.5, pop(1100), .6), (3.6, tick(1900), .3), (4.0, pop(650), .6), (4.4, ding(1318), .5), (5.0, chime(), .5)]

# ---------- montaggio ----------
def seq(parts):
    starts = []; t0 = 0
    for p in parts: starts.append(t0); t0 += p[1]
    def fn(t):
        for (f, d, _), s in zip(parts, starts):
            if t < s + d: return f(t - s)
        return parts[-1][0](parts[-1][1])
    ev = [(s + e[0], e[1], e[2]) for (f, d, evs), s in zip(parts, starts) for e in evs]
    return fn, t0, ev

REELS = {
    'reel_1_mi_serve_il_tuo_aiuto': [(a_creato, 3.0, EV_CREATO), (a_aiuto, 4.6, EV_AIUTO), (a_giorni, 4.8, EV_GIORNI), (a_cta, 3.6, EV_CTA)],
    'reel_2_cosa_ci_guadagni': [(b_prima, 3.8, EV_PRIMA), (b_idee, 5.9, EV_IDEE), (b_gratis, 4.4, EV_GRATIS2), (a_cta, 3.6, EV_CTA)],
    'reel_3_tester_in_3_passi': [(c_titolo, 2.8, EV_TIT), (c_passi, 6.2, EV_PASSI), (a_cta, 3.6, EV_CTA)],
}
NAMES = list(REELS)

def job(a):
    k, fi = a; fn, dur, ev = seq(REELS[NAMES[k]])
    fn(fi / FPS).convert('RGB').save(D + 'f/reel_%d/%04d.png' % (k, fi))

if __name__ == '__main__':
    only = sys.argv[1:]; out = D + 'out/tester/'; os.makedirs(out, exist_ok=True); jobs = []; idx = [k for k in range(len(NAMES)) if not only or str(k) in only]
    for k in idx:
        fd = D + 'f/reel_%d' % k; shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
        jobs += [(k, fi) for fi in range(int(seq(REELS[NAMES[k]])[1] * FPS))]
    with ProcessPoolExecutor() as ex: list(ex.map(job, jobs, chunksize=8))
    for k in idx:
        fn, dur, ev = seq(REELS[NAMES[k]]); wav = D + 'f/reel_%d.wav' % k
        mix(ev, dur, wav); encode(D + 'f/reel_%d' % k, wav, out + NAMES[k] + '.mp4'); print(NAMES[k], round(dur, 1), 's')
