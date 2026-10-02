import base64, json, math, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public' / 'assets' / 'orbit-beacon.gltf'
chunks, views, accessors, meshes, nodes = [], [], [], [], []

def pack(fmt, values): return struct.pack('<' + fmt * len(values), *values)
def add_view(data, target):
    offset = sum(len(c) for c in chunks)
    pad = (-offset) % 4
    if pad: chunks.append(b'\0' * pad); offset += pad
    chunks.append(data); views.append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':target}); return len(views)-1
def add_accessor(view, component, count, kind, mins=None, maxs=None):
    a={'bufferView':view,'componentType':component,'count':count,'type':kind}
    if mins is not None: a['min']=mins; a['max']=maxs
    accessors.append(a); return len(accessors)-1
def add_mesh(name, verts, norms, inds, material, translation=(0,0,0), rotation=None, scale=None):
    flat=[x for v in verts for x in v]; nflat=[x for n in norms for x in n]
    pv=add_view(pack('f',flat),34962); nv=add_view(pack('f',nflat),34962); iv=add_view(pack('H',inds),34963)
    mins=[min(v[i] for v in verts) for i in range(3)]; maxs=[max(v[i] for v in verts) for i in range(3)]
    pa=add_accessor(pv,5126,len(verts),'VEC3',mins,maxs); na=add_accessor(nv,5126,len(norms),'VEC3'); ia=add_accessor(iv,5123,len(inds),'SCALAR')
    meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa,'NORMAL':na},'indices':ia,'material':material}]})
    node={'name':name,'mesh':len(meshes)-1,'translation':list(translation)}
    if rotation: node['rotation']=list(rotation)
    if scale: node['scale']=list(scale)
    nodes.append(node)

def box(sx,sy,sz):
    p=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    faces=[(0,1,2,3,(0,0,-1)),(5,4,7,6,(0,0,1)),(4,0,3,7,(-1,0,0)),(1,5,6,2,(1,0,0)),(3,2,6,7,(0,1,0)),(4,5,1,0,(0,-1,0))]
    v=[]; n=[]; idx=[]
    for f in faces:
        st=len(v); v += [p[i] for i in f[:4]]; n += [f[4]]*4; idx += [st,st+1,st+2,st,st+2,st+3]
    return v,n,idx

def cylinder(r,h,segments=24):
    v=[]; n=[]; idx=[]
    for i in range(segments):
        a=2*math.pi*i/segments; v.extend([(r*math.cos(a),-h,r*math.sin(a)),(r*math.cos(a),h,r*math.sin(a))]); n.extend([(math.cos(a),0,math.sin(a))]*2)
    for i in range(segments):
        j=(i+1)%segments; idx += [2*i,2*j,2*i+1,2*j,2*j+1,2*i+1]
    for y,ny in [(-h,-1),(h,1)]:
        c=len(v); v.append((0,y,0)); n.append((0,ny,0)); ring=[]
        for i in range(segments):
            a=2*math.pi*i/segments; ring.append(len(v)); v.append((r*math.cos(a),y,r*math.sin(a))); n.append((0,ny,0))
        for i in range(segments):
            j=(i+1)%segments; idx += [c,ring[j],ring[i]] if ny<0 else [c,ring[i],ring[j]]
    return v,n,idx

def torus(R,r,major=40,minor=8):
    v=[]; n=[]; idx=[]
    for i in range(major):
        a=2*math.pi*i/major
        for j in range(minor):
            b=2*math.pi*j/minor; nx=math.cos(a)*math.cos(b); ny=math.sin(b); nz=math.sin(a)*math.cos(b)
            v.append(((R+r*math.cos(b))*math.cos(a),r*math.sin(b),(R+r*math.cos(b))*math.sin(a))); n.append((nx,ny,nz))
    for i in range(major):
        for j in range(minor):
            a=i*minor+j; b=((i+1)%major)*minor+j; c=((i+1)%major)*minor+(j+1)%minor; d=i*minor+(j+1)%minor; idx += [a,b,d,b,c,d]
    return v,n,idx

def octa(r=0.8):
    v=[(0,r,0),(r,0,0),(0,0,r),(-r,0,0),(0,0,-r),(0,-r,0)]
    faces=[(0,1,2),(0,2,3),(0,3,4),(0,4,1),(5,2,1),(5,3,2),(5,4,3),(5,1,4)]
    verts=[]; norms=[]; inds=[]
    for f in faces:
        a,b,c=[v[i] for i in f]; ux,uy,uz=[b[i]-a[i] for i in range(3)]; vx,vy,vz=[c[i]-a[i] for i in range(3)]; nn=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx); l=math.sqrt(sum(x*x for x in nn)); nn=tuple(x/l for x in nn); s=len(verts); verts += [a,b,c]; norms += [nn]*3; inds += [s,s+1,s+2]
    return verts,norms,inds

materials=[
 {'name':'Midnight metal','pbrMetallicRoughness':{'baseColorFactor':[.025,.05,.07,1],'metallicFactor':.9,'roughnessFactor':.23}},
 {'name':'Ceramic shell','pbrMetallicRoughness':{'baseColorFactor':[.68,.78,.79,1],'metallicFactor':.35,'roughnessFactor':.25}},
 {'name':'Cyan energy','pbrMetallicRoughness':{'baseColorFactor':[0,.8,1,1],'metallicFactor':.2,'roughnessFactor':.15},'emissiveFactor':[0,.85,1]},
 {'name':'Copper accent','pbrMetallicRoughness':{'baseColorFactor':[.95,.28,.1,1],'metallicFactor':.75,'roughnessFactor':.26}},
 {'name':'Dark rubber','pbrMetallicRoughness':{'baseColorFactor':[.04,.045,.05,1],'metallicFactor':.1,'roughnessFactor':.8}}
]
add_mesh('Pedestal',*cylinder(1.0,.22,32),0,translation=(0,-1.25,0))
add_mesh('Pedestal Collar',*cylinder(.72,.18,32),3,translation=(0,-.91,0))
add_mesh('Signal Mast',*cylinder(.13,.72,20),1,translation=(0,-.2,0))
add_mesh('Energy Core',*octa(.78),2,translation=(0,.82,0),rotation=(0,.382683,0,.92388))
add_mesh('Orbit Ring A',*torus(1.15,.045),1,translation=(0,.82,0))
add_mesh('Orbit Ring B',*torus(1.35,.04),3,translation=(0,.82,0),rotation=(.382683,0,0,.92388))
add_mesh('Orbit Ring C',*torus(1.55,.035),1,translation=(0,.82,0),rotation=(0,0,.5,.866025))
for x,z in [(-.72,-.72),(.72,-.72),(-.72,.72),(.72,.72)]: add_mesh('Anchor',*box(.11,.42,.11),4,translation=(x,-.62,z))

blob=b''.join(chunks); encoded=base64.b64encode(blob).decode()
doc={'asset':{'version':'2.0','generator':'Original Orbit Beacon generator'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':materials,'buffers':[{'byteLength':len(blob),'uri':'data:application/octet-stream;base64,'+encoded}],'bufferViews':views,'accessors':accessors}
OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,separators=(',',':')))
print(OUT, OUT.stat().st_size)
