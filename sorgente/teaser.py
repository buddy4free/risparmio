import math, os, numpy as np, json, base64, io, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from concurrent.futures import ProcessPoolExecutor
W,H,FPS,DUR=1080,1920,30,24.0
Y=(255,201,10); WH=(255,255,255); BK=(0,0,0)
D=os.path.dirname(os.path.abspath(__file__))+'/'
ST='/home/user/risparmio/store/'
def F(n,s): return ImageFont.truetype(D+n+'.ttf',s)
ease=lambda t:1-(1-max(0,min(1,t)))**3
back=lambda t:(lambda x:1+2.70158*(x-1)**3+1.70158*(x-1)**2)(max(0,min(1,t)))
def txt(s,font,col):
    b=font.getbbox(s); im=Image.new('RGBA',(b[2]-b[0]+20,b[3]-b[1]+20),(0,0,0,0))
    ImageDraw.Draw(im).text((10-b[0],10-b[1]),s,font=font,fill=col); return im
def put(c,im,cx,cy,sc=1.0,a=1.0):
    if sc<=0.01 or a<=0: return
    if sc!=1: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.LANCZOS)
    if a<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*a)))
    c.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
L=json.load(open('/tmp/claude-0/-home-user/5d688e9e-4cef-51e8-b416-070f144b3467/scratchpad/logo.json'))
LOGO=Image.open(io.BytesIO(base64.b64decode(L['full']))).convert('RGBA')
ENSO=Image.open(io.BytesIO(base64.b64decode(L['enso']))).convert('RGBA')
def ring(c,cx,cy,r,w,prog,col=Y,a=255):
    d=ImageDraw.Draw(c); d.arc((cx-r,cy-r,cx+r,cy+r),-90,-90+360*prog,fill=col+(a,),width=w)
shots={k:Image.open(f).convert('RGBA') for k,f in [('add',D+'add.png'),('home',ST+'1-home.png'),('ese',ST+'4-ese.png'),('gym',ST+'6-palestra.png')]}
crops={'add':(0,0,1080,1110),'home':(0,370,1080,1745),'ese':(0,440,1080,1360),'gym':(0,390,1080,1730)}
def tfit(s,name,size,col,maxw=980):
    while size>40:
        im=txt(s,F(name,size),col)
        if im.width<=maxw: return im
        size-=6
    return im
def phone(c,key,t,label):
    im=shots[key].crop(crops[key]); pw=860; ph=int(im.height*pw/im.width); im=im.resize((pw,ph),Image.LANCZOS)
    fr=Image.new('RGBA',(pw+40,ph+40),(0,0,0,0)); d=ImageDraw.Draw(fr); d.rounded_rectangle((0,0,pw+39,ph+39),48,fill=(20,20,20,255),outline=Y+(255,),width=10)
    m=Image.new('L',(pw,ph),0); ImageDraw.Draw(m).rounded_rectangle((0,0,pw-1,ph-1),36,fill=255); fr.paste(im,(20,20),m)
    e=ease(t/0.35); sc=0.86+0.14*e+0.04*t; y=H/2+120+(1-e)*700
    put(c,fr,W/2,y,sc,min(1,t/0.2))
    put(c,tfit(label,'Anton',190,Y),W/2,330-(1-ease(t/0.3))*80,1,min(1,t/0.15))
def frame(i):
    t=i/FPS; c=Image.new('RGBA',(W,H),BK+(255,))
    if t<2.4:
        ring(c,W/2,H/2,500,24,ease(t/1.0),Y,110)
        put(c,txt('HO CREATO',F('Anton',170),WH),W/2,H/2-130,back((t-0.15)/0.3),min(1,(t-0.15)/0.1))
        put(c,txt("UN'APP",F('Anton',280),Y),W/2,H/2+110,back((t-0.6)/0.3)*(1+0.05*max(0,1-(t-0.6)/0.2)),min(1,(t-0.6)/0.08))
    elif t<5.2:
        u=t-2.4
        if u<0.08: c=Image.new('RGBA',(W,H),(255,255,255,255))
        put(c,tfit('PER GESTIRE','Anton',150,WH),W/2,H/2-430,ease(u/0.25),min(1,u/0.15))
        s1=t-2.8; put(c,tfit('ENTRATE E USCITE…','Anton',140,WH),W/2,H/2-260,ease(s1/0.25) if s1>0 else 0,min(1,s1/0.15) if s1>0 else 0)
        s2=t-3.6; put(c,tfit('…E MOLTO','Anton',250,Y),W/2,H/2+40,(2.0-1.0*ease(s2/0.18)) if s2>=0 else 0,min(1,s2/0.1) if s2>=0 else 0)
        s3=t-3.85; put(c,tfit('DI PIÙ.','Anton',300,Y),W/2,H/2+330,(2.0-1.0*ease(s3/0.18)) if s3>=0 else 0,min(1,s3/0.1) if s3>=0 else 0)
    elif t<10.8:
        u=t-5.2; k=min(3,int(u/1.4)); phone(c,['add','home','ese','gym'][k],u-1.4*k,['SEGNA','CONTROLLA','SOGNA','ALLENATI'][k])
    elif t<14.0:
        u=t-10.8
        if u<0.06: c=Image.new('RGBA',(W,H),(255,255,255,255))
        put(c,txt('NIENTE TRADING,',F('Anton',122),WH),W/2,H/2-560,back(u/0.3),min(1,u/0.12))
        s1=u-0.45; put(c,txt('NIENTE CONSIGLI',F('Anton',122),WH),W/2,H/2-405,back(s1/0.3) if s1>0 else 0,min(1,s1/0.12) if s1>0 else 0)
        s1=u-0.6; put(c,txt('DI INVESTIMENTO.',F('Anton',122),WH),W/2,H/2-250,back(s1/0.3) if s1>0 else 0,min(1,s1/0.12) if s1>0 else 0)
        s2=u-1.05; put(c,tfit('Solo i tuoi soldi','Figtree',92,WH),W/2,H/2-30,1,min(1,s2/0.2) if s2>0 else 0)
        put(c,tfit('di tutti i giorni,','Figtree',92,WH),W/2,H/2+90,1,min(1,(s2-0.15)/0.2) if s2>0.15 else 0)
        s3=u-1.6; put(c,tfit('SOTTO CONTROLLO.','Anton',190,Y),W/2,H/2+340,(1.8-0.8*ease(s3/0.2)) if s3>=0 else 0,min(1,s3/0.1) if s3>=0 else 0)
    elif t<16.8:
        u=t-14.0; n=0 if u<0.2 else min(20,int(1+(u-0.2)/1.2*20)) if u<1.4 else 20
        put(c,txt('CERCO',F('Anton',150),WH),W/2,H/2-430,ease(u/0.25),1)
        put(c,txt(str(n),F('Anton',560),Y),W/2,H/2-60,1+0.05*(1-((u-0.2)*16)%1) if 0.2<u<1.4 else (back((u-1.4)/0.25)*0.1+1 if u<1.65 else 1.1),1)
        s=u-1.6; put(c,txt('TESTER',F('Anton',220),WH),W/2,H/2+330,back(s/0.3) if s>0 else 0,1)
        s=u-1.9; put(c,txt('con Android',F('PermanentMarker',90),Y),W/2,H/2+520,1,min(1,s/0.2) if s>0 else 0)
    elif t<20.2:
        u=t-16.8
        put(c,txt('COSA CI GUADAGNI',F('Anton',130),Y),W/2,H/2-520,ease(u/0.25),min(1,u/0.15))
        items=[('La provi','prima di tutti'),('Le tue idee','diventano funzioni'),('Gratis,','per sempre')]
        for j,(l1,l2) in enumerate(items):
            s=u-0.35-0.6*j
            if s<=0: continue
            y=H/2-230+j*290; x0=150
            it=Image.new('RGBA',(900,250),(0,0,0,0)); d=ImageDraw.Draw(it)
            d.ellipse((0,40,150,190),fill=Y+(255,)); d.line([(38,118),(66,148),(114,86)],fill=BK+(255,),width=16,joint='curve')
            d.text((185,30),l1,font=F('Anton',100),fill=WH+(255,)); d.text((185,140),l2,font=F('Figtree',62),fill=(225,225,220,255))
            put(c,it,W/2+20+(1-ease(s/0.3))*300,y,1,min(1,s/0.2))
    else:
        u=t-20.2; lg=LOGO.resize((380,int(380*LOGO.height/LOGO.width)),Image.LANCZOS)
        put(c,lg,W/2,H/2-520,ease(u/0.35),min(1,u/0.25))
        put(c,txt('SCRIVIMI',F('Anton',170),WH),W/2,H/2-60,back((u-0.2)/0.3),1 if u>0.2 else 0)
        p=1+0.05*math.sin((u-0.6)*2*math.pi*1.0) if u>0.6 else back((u-0.4)/0.3)
        box=Image.new('RGBA',(760,330),(0,0,0,0)); d=ImageDraw.Draw(box); d.rounded_rectangle((0,0,759,329),56,fill=Y+(255,))
        tt=txt('TEST',F('Anton',250),BK); box.alpha_composite(tt,((760-tt.width)//2,(330-tt.height)//2))
        put(c,box,W/2,H/2+250,p if u>0.4 else 0,1)
        put(c,txt('in direct  ↓',F('Figtree',72),WH),W/2,H/2+520,1,min(1,(u-0.9)/0.3) if u>0.9 else 0)
    c.convert('RGB').save(D+'f/%04d.png'%i)
# ---------- audio ----------
SR=44100
def env(n,a,dcy): x=np.arange(n)/SR; return np.minimum(1,x/a)*np.exp(-x/dcy)
def noise(n,seed): return np.random.default_rng(seed).uniform(-1,1,n)
def lp(x,k):
    y=np.zeros_like(x); s=0.0
    for i in range(len(x)): s+=k[i]*(x[i]-s) if hasattr(k,'__len__') else k*(x[i]-s); y[i]=s
    return y
def whoosh(seed=1,d=0.45):
    n=int(d*SR); k=np.linspace(0.02,0.35,n)**1.5; x=lp(noise(n,seed),k); e=np.sin(np.linspace(0,math.pi,n))**2; return x*e*2.2
def hit(): n=int(0.5*SR); x=np.arange(n)/SR; f=55+90*np.exp(-x*30); return np.sin(2*math.pi*np.cumsum(f)/SR)*env(n,0.002,0.16)+noise(n,3)*env(n,0.001,0.02)*0.5
def pop(f0=700): n=int(0.14*SR); x=np.arange(n)/SR; f=f0+f0*0.8*x/0.14; return np.sin(2*math.pi*np.cumsum(f)/SR)*env(n,0.003,0.05)*0.8
def tick(): n=int(0.05*SR); return (np.sin(2*math.pi*2200*np.arange(n)/SR)*0.6+noise(n,9)*0.3)*env(n,0.0005,0.012)
def chime():
    n=int(1.6*SR); x=np.arange(n)/SR; return sum(np.sin(2*math.pi*f*x)*np.exp(-x*(2+i)) for i,f in enumerate([1046.5,1318.5,1568,2093]))*0.35*np.minimum(1,x/0.005)
def music():
    n=int(DUR*SR); x=np.arange(n)/SR; m=np.zeros(n); beat=60/112
    chords=[(57,60,64),(53,57,60),(48,52,55),(55,59,62)]
    hz=lambda k:440*2**((k-69)/12)
    for b in range(int(DUR/beat)+1):
        s=int(b*beat*SR)
        if s>=n: break
        kk=min(n-s,int(0.35*SR)); xx=np.arange(kk)/SR; f=48+80*np.exp(-xx*25); m[s:s+kk]+=np.sin(2*math.pi*np.cumsum(f)/SR)*np.exp(-xx*9)*0.9
        hs=int((b+0.5)*beat*SR); hk=min(n-hs,int(0.04*SR))
        if hk>0: m[hs:hs+hk]+=noise(hk,b)*np.exp(-np.arange(hk)/SR*120)*0.18
        ch=chords[(b//4)%4]; bk=min(n-s,int(beat*SR))
        xb=np.arange(bk)/SR; m[s:s+bk]+=np.sin(2*math.pi*hz(ch[0]-12)*xb)*np.exp(-xb*3)*0.35
        for j in range(2):
            a=s+int(j*beat/2*SR); ak=min(n-a,int(0.22*SR))
            if ak>0: xa=np.arange(ak)/SR; m[a:a+ak]+=np.sin(2*math.pi*hz(ch[(b*2+j)%3]+12)*xa)*np.exp(-xa*14)*0.16
    pad=sum(np.sin(2*math.pi*hz(k)*x) for k in (57,64))*0.05
    m+=pad; m*=np.minimum(1,x/0.4)*np.minimum(1,(DUR-x)/1.2)
    return m
def mix():
    n=int(DUR*SR); out=np.zeros(n); mu=music(); duck=np.ones(n)
    O=5.2
    ev=[(0.1,whoosh(1),.8),(0.6,hit(),1),(2.4,whoosh(2,.35),.8),(2.5,pop(600),.6),(2.85,pop(750),.5),(3.6,hit(),1),(3.85,pop(900),.5),
        (5.15,whoosh(3),.8),(6.55,whoosh(4),.8),(7.95,whoosh(5),.8),(9.35,whoosh(9),.8),
        (10.75,whoosh(10,.3),.7),(10.85,pop(650),.6),(11.3,pop(650),.6),(11.85,pop(820),.4),(12.4,hit(),1)]
    ev+=[(9.0+O+k*0.06,tick(),.6) for k in range(20)]+[(10.2+O,hit(),1),(10.7+O,pop(1000),.5),(11.6+O,whoosh(8,.3),.7)]
    ev+=[(11.95+O+0.6*j,pop(700+150*j),.8) for j in range(3)]+[(15.0+O,whoosh(7),.7),(15.4+O,chime(),.8)]
    for t0,s,g in ev:
        a=int(t0*SR); b=min(n,a+len(s)); out[a:b]+=s[:b-a]*g
        if g>=.9: d=int(0.25*SR); e=min(n,a+d); duck[a:e]=np.minimum(duck[a:e],0.45+0.55*np.linspace(0,1,e-a))
    mu=mu/np.abs(mu).max()*10**(-15/20); out=out/np.abs(out).max()*10**(-7/20)
    y=out+(mu*duck if os.environ.get('MUSIC','1')=='1' else 0); y=y/max(1,np.abs(y).max()/0.95)
    import wave; w=wave.open(D+'audio.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y*32767).astype('<i2').tobytes()); w.close()
if __name__=='__main__':
    if not os.path.exists(D+'f/%04d.png'%(int(DUR*FPS)-1)):
        with ProcessPoolExecutor() as ex: list(ex.map(frame,range(int(DUR*FPS))))
    mix()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',D+'f/%04d.png','-i',D+'audio.wav','-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',os.environ.get('OUT','/home/user/risparmio/store/teaser-tester.mp4')],check=True)
    print('ok')
