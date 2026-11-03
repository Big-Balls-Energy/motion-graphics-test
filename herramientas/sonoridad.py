"""Mide qué tan sonora (no susurrada) es una toma de voz: % de cuadros con voz periódica y correlación media.
Uso: python3 herramientas/sonoridad.py toma1.mp3 [toma2.mp3 ...]   (frase normal ≥ 55 %; debajo de 45 % suena a susurro)"""
import sys, subprocess, numpy as np
SR=16000
def load(p):
    d=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(SR),'-f','s16le','-'],capture_output=True).stdout
    return np.frombuffer(d,'<i2').astype(float)/32768
for p in sys.argv[1:]:
    x=load(p);fl=int(.04*SR);hp=int(.01*SR);rms=[];cor=[]
    for i in range(0,len(x)-fl,hp):
        f=x[i:i+fl]-x[i:i+fl].mean();e=np.sqrt((f**2).mean());rms.append(e)
        ac=np.correlate(f,f,'full')[fl-1:];ac/=ac[0]+1e-12;cor.append(ac[SR//400:SR//75].max())
    rms=np.array(rms);cor=np.array(cor);sp=rms>rms.max()*.1
    c=cor[sp];print(f"{p.split('/')[-1]:10s} voz {np.mean(c>.6)*100:5.1f}%  corr {np.median(c):.2f}  dur {len(x)/SR:.2f}")
