import os, sys, shutil
from concurrent.futures import ProcessPoolExecutor
import scenes
from b4f import FPS, mix, encode, D

def job(a):
    kind, ci, fi = a
    W, H = (1920, 1080) if kind == 'long' else (1080, 1920)
    name, dur, fn, _ = (scenes.LONG if kind == 'long' else scenes.SHORT)[ci]
    fn(fi / FPS, W, H).convert('RGB').save(D + 'f/%s_%02d/%04d.png' % (kind, ci, fi))

if __name__ == '__main__':
    kinds = sys.argv[1:] or ['long', 'short']; only = os.environ.get('ONLY')
    for kind in kinds:
        L = scenes.LONG if kind == 'long' else scenes.SHORT; out = D + 'out/' + kind + '/'; os.makedirs(out, exist_ok=True)
        idx = [i for i in range(len(L)) if not only or str(i) in only.split(',')]
        jobs = []
        for ci in idx:
            fd = D + 'f/%s_%02d' % (kind, ci); shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
            jobs += [(kind, ci, fi) for fi in range(int(L[ci][1] * FPS))]
        with ProcessPoolExecutor() as ex: list(ex.map(job, jobs, chunksize=8))
        for ci in idx:
            name, dur, fn, ev = L[ci]; wav = D + 'f/%s_%02d.wav' % (kind, ci)
            mix(ev, dur, wav); encode(D + 'f/%s_%02d' % (kind, ci), wav, out + name + '.mp4')
        print(kind, 'ok', len(idx))
