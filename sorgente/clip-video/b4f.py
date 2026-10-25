"""Clip Buddy4Free Risparmio: motore comune (disegno, suoni, render)."""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__)) + '/'
FPS, SR = 30, 44100
NAVY, NAVY2, GRID = (11, 21, 48), (19, 34, 74), (34, 54, 104)
AMBER, AMBER2 = (255, 176, 32), (255, 201, 10)
CREAM, INK, WHITE = (247, 243, 234), (17, 17, 17), (255, 255, 255)
RED, GREEN, BLUE, ORANGE, TEAL, LILAC = (229, 72, 77), (34, 164, 93), (57, 135, 229), (217, 89, 38), (25, 158, 112), (144, 133, 233)
MUTED = (150, 160, 185)

_F = {}
def F(name, size):
    k = (name, size)
    if k not in _F: _F[k] = ImageFont.truetype(D + 'fonts/' + {'anton': 'Anton', 'comf': 'Comfortaa', 'lora': 'LoraItalic', 'lorab': 'LoraBold'}[name] + '.ttf', size)
    return _F[k]

_IMG = {}
def img(name):
    if name not in _IMG: _IMG[name] = Image.open(D + 'shots/' + name + '.png').convert('RGBA')
    return _IMG[name]

clamp = lambda x: max(0.0, min(1.0, x))
ease = lambda t: 1 - (1 - clamp(t)) ** 3
inout = lambda t: (lambda x: 3 * x * x - 2 * x * x * x)(clamp(t))
def back(t):
    x = clamp(t) - 1
    return 1 + 2.70158 * x ** 3 + 1.70158 * x ** 2

def text(s, font, col, stroke=0, scol=None):
    b = font.getbbox(s, stroke_width=stroke); im = Image.new('RGBA', (b[2] - b[0] + 8, b[3] - b[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - b[0], 4 - b[1]), s, font=font, fill=col + (255,) if len(col) == 3 else col, stroke_width=stroke, stroke_fill=scol)
    return im

def fit(s, name, size, col, maxw, **kw):
    while size > 20:
        im = text(s, F(name, size), col, **kw)
        if im.width <= maxw: return im
        size -= 4
    return im

def put(c, im, cx, cy, sc=1.0, a=1.0, anchor='c'):
    if sc <= 0.01 or a <= 0.01: return
    if abs(sc - 1) > 0.001: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    x = cx - im.width / 2 if anchor[0] == 'c' else cx if anchor[0] == 'l' else cx - im.width
    c.alpha_composite(im, (int(x), int(cy - im.height / 2)))

def rrect(size, r, fill, outline=None, w=0):
    im = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=fill, outline=outline, width=w); return im

def shadow(im, r=18, off=(0, 14), a=150):
    s = Image.new('RGBA', (im.width + r * 4, im.height + r * 4), (0, 0, 0, 0)); m = im.getchannel('A').point(lambda v: a if v else 0)
    s.paste((0, 0, 0, 255), (r * 2 + off[0], r * 2 + off[1]), m); s = s.filter(ImageFilter.GaussianBlur(r)); s.alpha_composite(im, (r * 2, r * 2)); return s

_PH = {}
def phone(name, w, crop=None, frame=AMBER2):
    k = (name, w, crop, frame)
    if k not in _PH:
        sc = img(name)
        if crop: sc = sc.crop(crop)
        h = int(sc.height * (w - 28) / sc.width); sc = sc.resize((w - 28, h), Image.LANCZOS)
        body = rrect((w, h + 28), 46, (14, 14, 14, 255), frame + (255,), 7)
        m = Image.new('L', sc.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sc.width - 1, sc.height - 1), 34, fill=255); body.paste(sc, (14, 14), m)
        _PH[k] = shadow(body)
    return _PH[k]

# ---------- sfondi ----------
def bg_navy(W, H, t, grid=True):
    c = Image.new('RGBA', (W, H), NAVY + (255,)); d = ImageDraw.Draw(c)
    for i in range(0, H, 6): pass
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    # luce radiale
    for r in range(6):
        rr = int(max(W, H) * (0.75 - r * 0.1)); gd.ellipse((W * 0.65 - rr, H * 0.25 - rr, W * 0.65 + rr, H * 0.25 + rr), fill=NAVY2 + (40,))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    if grid:
        off = (t * 18) % 80; d = ImageDraw.Draw(c)
        for x in range(-80, W + 80, 80): d.line((x + off, 0, x + off, H), fill=GRID + (90,), width=1)
        for y in range(-80, H + 80, 80): d.line((0, y + off * 0.5, W, y + off * 0.5), fill=GRID + (90,), width=1)
    return c

def bg_cream(W, H):
    c = Image.new('RGBA', (W, H), CREAM + (255,)); d = ImageDraw.Draw(c)
    for y in range(0, H, 4): d.line((0, y, W, y), fill=(240, 235, 224, 255) if (y // 4) % 2 else CREAM + (255,))
    return c

def bg_comic(W, H):
    c = Image.new('RGBA', (W, H), WHITE + (255,)); d = ImageDraw.Draw(c)
    for y in range(0, H, 26):
        for x in range((y // 26 % 2) * 13, W, 26): d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(236, 236, 240, 255))
    return c

def glitch(im, amt, seed=0):
    if amt <= 0: return im
    r, g, b, a = im.split(); rng = np.random.default_rng(seed); dx = int(amt * 14)
    r = r.transform(r.size, Image.AFFINE, (1, 0, dx, 0, 1, 0)); b = b.transform(b.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0))
    out = Image.merge('RGBA', (r, g, b, a))
    arr = np.array(out)
    for _ in range(int(amt * 6)):
        y0 = int(rng.integers(0, arr.shape[0] - 10)); hh = int(rng.integers(4, 18)); sh = int(rng.integers(-30, 30) * amt)
        arr[y0:y0 + hh] = np.roll(arr[y0:y0 + hh], sh, axis=1)
    return Image.fromarray(arr)

def bubble(w, h, tail='bl', fill=WHITE, out=INK):
    im = Image.new('RGBA', (w + 60, h + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tx = 60 if tail[1] == 'l' else w - 40
    d.polygon([(tx, h - 10), (tx + 50, h - 10), (tx - 10 if tail[1] == 'l' else tx + 80, h + 60)], fill=out)
    d.rounded_rectangle((0, 0, w, h), 40, fill=fill, outline=out, width=8)
    d.polygon([(tx + 8, h - 14), (tx + 42, h - 14), (tx - 2 if tail[1] == 'l' else tx + 66, h + 42)], fill=fill)
    return im

def card(w, h, fill=NAVY2, out=AMBER, r=26, wd=4):
    return rrect((w, h), r, fill + (255,), out + (255,) if out else None, wd if out else 0)

# ---------- icone disegnate ----------
def wallet(s, col=AMBER):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(6, s // 18)
    d.rounded_rectangle((s * .08, s * .25, s * .92, s * .85), s * .1, fill=col, outline=INK, width=w)
    d.rounded_rectangle((s * .55, s * .45, s * .98, s * .65), s * .06, fill=(255, 230, 160), outline=INK, width=w)
    d.ellipse((s * .66, s * .51, s * .74, s * .59), fill=INK)
    d.rounded_rectangle((s * .16, s * .12, s * .7, s * .3), s * .05, fill=(255, 255, 255), outline=INK, width=w)
    return im

def check(s, col=GREEN, prog=1.0):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.ellipse((0, 0, s - 1, s - 1), fill=col)
    pts = [(s * .26, s * .52), (s * .43, s * .69), (s * .75, s * .34)]
    if prog > 0:
        a = clamp(prog * 2); b2 = clamp(prog * 2 - 1)
        p1 = (pts[0][0] + (pts[1][0] - pts[0][0]) * a, pts[0][1] + (pts[1][1] - pts[0][1]) * a); d.line([pts[0], p1], fill=WHITE, width=max(4, s // 10))
        if b2 > 0: p2 = (pts[1][0] + (pts[2][0] - pts[1][0]) * b2, pts[1][1] + (pts[2][1] - pts[1][1]) * b2); d.line([pts[1], p2], fill=WHITE, width=max(4, s // 10))
    return im

def padlock(s, col=AMBER):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(6, s // 14)
    d.arc((s * .25, s * .05, s * .75, s * .6), 180, 360, fill=INK, width=w); d.line((s * .25, s * .33, s * .25, s * .45), fill=INK, width=w); d.line((s * .75, s * .33, s * .75, s * .45), fill=INK, width=w)
    d.rounded_rectangle((s * .12, s * .42, s * .88, s * .95), s * .08, fill=col, outline=INK, width=w); d.ellipse((s * .44, s * .58, s * .56, s * .7), fill=INK); d.rectangle((s * .48, s * .66, s * .52, s * .8), fill=INK)
    return im

# ---------- suoni ----------
def _env(n, a, dcy): x = np.arange(n) / SR; return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / dcy)
def _noise(n, seed): return np.random.default_rng(seed).uniform(-1, 1, n)
def _lp(x, k):
    y = np.zeros_like(x); s = 0.0
    kk = k if hasattr(k, '__len__') else np.full(len(x), k)
    for i in range(len(x)): s += kk[i] * (x[i] - s); y[i] = s
    return y
def whoosh(seed=1, d=0.45): n = int(d * SR); k = np.linspace(0.02, 0.32, n) ** 1.5; return _lp(_noise(n, seed), k) * np.sin(np.linspace(0, math.pi, n)) ** 2 * 2.0
def hit(): n = int(0.45 * SR); x = np.arange(n) / SR; f = 55 + 80 * np.exp(-x * 30); return np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.15) + _noise(n, 3) * _env(n, 0.001, 0.015) * 0.4
def pop(f0=700): n = int(0.13 * SR); x = np.arange(n) / SR; f = f0 + f0 * 0.7 * x / 0.13; return np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(n, 0.003, 0.045) * 0.8
def tick(f=2200): n = int(0.05 * SR); return (np.sin(2 * math.pi * f * np.arange(n) / SR) * 0.6 + _noise(n, 9) * 0.25) * _env(n, 0.0005, 0.012)
def chime(): n = int(1.4 * SR); x = np.arange(n) / SR; return sum(np.sin(2 * math.pi * f * x) * np.exp(-x * (2.4 + i)) for i, f in enumerate([1046.5, 1318.5, 1568, 2093])) * 0.3 * np.minimum(1, x / 0.005)
def ding(f=1318.5): n = int(0.8 * SR); x = np.arange(n) / SR; return (np.sin(2 * math.pi * f * x) + 0.4 * np.sin(2 * math.pi * f * 2 * x)) * np.exp(-x * 5) * 0.5
def buzz(): n = int(0.35 * SR); x = np.arange(n) / SR; return np.sign(np.sin(2 * math.pi * 110 * x)) * 0.25 * _env(n, 0.005, 0.12) + _noise(n, 5) * 0.15 * _env(n, 0.002, 0.08)
def glitchs(seed=4): n = int(0.3 * SR); g = _noise(n, seed) * (np.random.default_rng(seed).uniform(0, 1, n // 400 + 1).repeat(400)[:n] > 0.5); return g * 0.45 * _env(n, 0.001, 0.2)
def stamp(): n = int(0.35 * SR); x = np.arange(n) / SR; return np.sin(2 * math.pi * 90 * x) * _env(n, 0.001, 0.06) + _noise(n, 7) * _env(n, 0.0005, 0.03) * 0.8
def rise(d=0.6): n = int(d * SR); x = np.arange(n) / SR; f = 300 + 900 * (x / d) ** 2; return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.sin(np.linspace(0, math.pi, n)) * 0.35
def coin(): return np.concatenate([ding(1975) * 0.6, np.zeros(10)])[: int(0.5 * SR)] + np.pad(ding(2637) * 0.5, (int(0.06 * SR), 0))[: int(0.5 * SR)]
def clang(): n = int(0.9 * SR); x = np.arange(n) / SR; return sum(np.sin(2 * math.pi * f * x) * np.exp(-x * (4 + i * 2)) for i, f in enumerate([220, 347, 563, 901])) * 0.35 + _noise(n, 2) * _env(n, 0.0005, 0.02) * 0.4

def mix(events, dur, path):
    n = int(dur * SR); out = np.zeros(n)
    for t0, s, g in events:
        a = int(t0 * SR); b = min(n, a + len(s))
        if a < n: out[a:b] += s[:b - a] * g
    pk = np.abs(out).max() or 1; out = out / pk * 10 ** (-7 / 20)
    fade = int(0.04 * SR); out[-fade:] *= np.linspace(1, 0, fade)
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes()); w.close()

def encode(frames_dir, wav, out):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', frames_dir + '/%04d.png', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], check=True)
