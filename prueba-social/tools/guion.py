import json,sys
TL=json.load(open(sys.argv[1]))
def ts(x):return f"{int(x//60):02d}:{x%60:05.2f}"
def srt(x):ms=int(round(x*1000));return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
VIS={'hook':'Dos restaurantes: uno vacío (gris) y otro lleno con fila. Zoom al lleno. Murmullo de gente.',
'giro':'«LA COMIDA» se tacha en naranja → entra «PRUEBA SOCIAL» con brillo; personitas en cascada (pop).',
'exp':'Puerta de baño de hotel con toalla → se reduce y aparecen el letrero A (hoja verde) y el B (personas).',
'res':'Barras: A sube a 35 % (cifra sola 2 s) · B sube a 44 % (cifra sola 2 s) · aparece «+9 puntos».',
'why':'Personita con «?» ante dos caminos → un grupo toma la derecha → la sigue → check verde.',
'where':'Carrusel: contador hasta «+10,000 clientes» (cifra sola 2 s) → listón «MÁS VENDIDO» → 5 estrellas.',
'app':'«SOMOS LOS MEJORES» se tacha → muro de reseñas y fotos de clientes que se llena.',
'cta':'Logo + @Atlas_Path + contador de seguidores + botón SEGUIR con clic → regresa al restaurante lleno (loop).'}
out=["# Guion limpio — «La prueba social» (versión SIN VOZ)","",
"Video: `prueba-social-sin-voz.mp4` · 1080×1920 · 30 fps · 60 s · música 12 % con texto / 18 % sin texto.","",
"**Cómo leer:** di cada línea cuando aparezca en pantalla. Las líneas *(pausa)* son silencio: la escena solo se mueve. "
"Las líneas **[CIFRA]** son la cifra sola en pantalla, sin subtítulo: puedes decirla en voz alta o dejarla respirar.",""]
md_rows=[];srt_rows=[];n=0
items=[('sub',s) for s in TL['subs']]+[('hold',h) for h in TL['holds']]
items.sort(key=lambda x:x[1]['a'])
for sc in TL['scenes']:
    out+=[f"## {ts(sc['a'])} – {ts(sc['b'])} · {sc['name']}","",f"_Visual: {VIS[sc['id']]}_","","| Entra | Sale | Leer | ritmo |","|---|---|---|---|"]
    for kind,s in items:
        if not(sc['a']<=s['a']<sc['b']):continue
        d=s['b']-s['a']
        if kind=='sub':
            w=len(s['text'].split());out.append(f"| {ts(s['a'])} | {ts(s['b'])} | {s['text']} | {w} pal · {d:.1f} s · {w/d:.1f} pal/s |")
            n+=1;srt_rows.append(f"{n}\n{srt(s['a'])} --> {srt(s['b'])}\n{s['text']}\n")
        else:out.append(f"| {ts(s['a'])} | {ts(s['b'])} | **[CIFRA] {s['text']}** | sola {d:.1f} s |")
    if sc['id']!='cta':out.append(f"| {ts(sc['b']-0.5)} | {ts(sc['b'])} | *(pausa)* | — |")
    out.append("")
out+=["## Texto corrido (para practicar)",""]
para=[]
for kind,s in items:para.append(s['text'] if kind=='sub' else f"**{s['text']}**")
out.append(" ".join(para));out.append("")
open('guion-con-tiempos.md','w').write("\n".join(out));open('subtitulos.srt','w').write("\n".join(srt_rows))
bad=[s for s in TL['subs'] if (s['b']-s['a'])<1.5-1e-6 or len(s['text'].split())/(s['b']-s['a'])>2.3+1e-6]
print('bloques',len(TL['subs']),'fuera de regla:',[(s['text'],round(s['b']-s['a'],2)) for s in bad])
