import json,sys
TL=json.load(open(sys.argv[1]))
def ts(x):return f"{int(x//60):02d}:{x%60:05.2f}"
def srt(x):ms=int(round(x*1000));return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
out=["# Guion limpio — Gary Vee: de la tienda de vinos a VaynerMedia (caso de éxito)","",
"Video: `gary-vee-sin-voz.mp4 / gary-vee-con-voz.mp4` · 1080×1920 · 30 fps · 75 s · música hip-hop/electrónica 98 BPM, 15 % con texto / 19 % sin texto (más cálida en la empatía).","",
"**Cómo leer:** di cada línea cuando aparezca en pantalla. Las líneas *(pausa)* son silencio: la escena solo se mueve. "
"Las líneas **[SOLA EN PANTALLA]** son cifras o la palabra clave sin subtítulo: dilas con fuerza mientras están solas.",""]
srt_rows=[];n=0
items=[('sub',s) for s in TL['subs']]+[('card',c) for c in TL.get('holds',[])]
items.sort(key=lambda x:x[1]['a'])
for sc in TL['scenes']:
    out+=[f"## {ts(sc['a'])} – {ts(sc['b'])} · {sc['name']}","",f"_Visual: {sc['vis']}_","","| Entra | Sale | Leer | ritmo |","|---|---|---|---|"]
    rows=[]
    for kind,s in items:
        if not(sc['a']<=s['a']<sc['b']):continue
        d=s['b']-s['a'];w=len(s['text'].split())
        if kind=='sub':rows.append((s['a'],f"| {ts(s['a'])} | {ts(s['b'])} | {s['text']} | {w} pal · {d:.1f} s · {w/d:.1f} pal/s |"))
        else:rows.append((s['a'],f"| {ts(s['a'])} | {ts(s['b'])} | **[SOLA EN PANTALLA] {s['text']}** | sola {d:.1f} s |"))
        n+=1;srt_rows.append(f"{n}\n{srt(s['a'])} --> {srt(s['b'])}\n{s['text']}\n")
    for a,b in sc.get('pauses',[[sc['b']-0.5,sc['b']]] if sc['id']!='cta' else []):rows.append((a,f"| {ts(a)} | {ts(b)} | *(pausa)* | — |"))
    rows.sort(key=lambda r:r[0]);out+=[r for _,r in rows];out.append("")
out+=["## Texto corrido (para practicar)",""]
out.append(" ".join(s['text'] for _,s in items));out.append("")
open('guion-con-tiempos.md','w').write("\n".join(out));open('subtitulos.srt','w').write("\n".join(srt_rows))
bad=[s for s in TL['subs'] if (s['b']-s['a'])<1.5-1e-6 or len(s['text'].split())/(s['b']-s['a'])>2.3+1e-6]
badc=[c['text'] for c in TL.get('holds',[]) if (c['b']-c['a'])<(3 if c['text']=='ATENCIÓN' or c['text'].startswith('«') else 2)-1e-6]
print('bloques',len(TL['subs']),'fuera de regla:',[(s['text'],round(s['b']-s['a'],2)) for s in bad],'cifras cortas:',badc)
