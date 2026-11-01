import sys
S=sys.argv[1]
base=open('consejos-ia/index.html',encoding='utf-8').read().split('\n')
L=lambda a,b:'\n'.join(base[a-1:b])
util=L(72,93)
prim=L(194,320)
three=L(450,523)
rep=[('rgba(34,211,238,','rgba(61,139,255,')]
def fix(s):
    for a,b in rep: s=s.replace(a,b)
    return s
prim=fix(prim); three=fix(three)
sc=open(f'{S}/_scenes.js',encoding='utf-8').read()
sc=sc  # sin parches específicos
sc=sc.replace("g.add(shell,fill,cap);return{g,shell,fill,cap,","g.add(shell,fill,cap);return{g,shell,fill,cap,capm,")
sc=sc.replace(" const top=3.3-6.6*.2*.72,st=path([new THREE.Vector3(0,top,0),new THREE.Vector3(.5,top+1.6,-.2),new THREE.Vector3(-.3,top+4,0),new THREE.Vector3(.2,top+8,0)].map((v,i,a)=>v),0xf9a8d4,.8);"," const top=3.3-6.6*.2*.72;")
sc=sc.replace("const kn=eo(p(HNOMBRE.a+(t-HNOMBRE.a),HNOMBRE.a,HNOMBRE.a+.35))","const kn=eo(p(t,HNOMBRE.a,HNOMBRE.a+.35))")
out='\n'.join([open(f'{S}/00_html.html',encoding='utf-8').read(),open(f'{S}/01_cfg.js',encoding='utf-8').read(),'',util,open(f'{S}/02_timeline.js',encoding='utf-8').read(),prim,'',three,sc,open(f'{S}/04_tail.js',encoding='utf-8').read()])
open('ignite-studio/index.html','w',encoding='utf-8').write(out)
print(len(out))
