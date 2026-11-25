import json
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
NAMES=['shipping','challenger']
def unit(v):
    return v/np.linalg.norm(v,axis=-1,keepdims=True)

def slab(origin,ray,center,half):
    a=(center-half-origin)/ray
    b=(center+half-origin)/ray
    return np.minimum(a,b).max(axis=-1),np.maximum(a,b).min(axis=-1)

def geometry(s):
    eye=np.array(s['post_camera'])
    f=unit(np.array(s['target'])-eye)
    right=unit(np.cross(f,[0,0,1]))
    up=np.cross(right,f)
    x,y=np.meshgrid(np.arange(2,1280,4),np.arange(2,720,4))
    k=np.tan(np.deg2rad(37/2))/360
    ray=unit(f+(x[...,None]+.5-640)*k*right+(360-y[...,None]-.5)*k*up)
    t=-eye[2]/ray[:,:,2]
    floor=eye+t[...,None]*ray
    boxes=np.array(json.loads((HERE.parent/'archive.json').read_text()))
    visible=(floor[:,:,0]>=0)&(floor[:,:,0]<=24)&(floor[:,:,1]>=0)&(floor[:,:,1]<=16)
    for b in boxes[1:]:
        near,far=slab(eye,ray,b[:3],b[3:])
        visible &= ~((near>0)&(far>=near)&(near<t))
    return eye,ray,t,floor,visible,boxes

def regions(s,i,geom):
    eye,ray,t,floor,visible,boxes=geom
    c=np.array([s['start_x']+i*s['step_x'],s['center_y'],s['center_z']])
    h=np.array(s['plank_half'])
    near,far=slab(eye,ray,c,h)
    dx,dy=np.moveaxis(abs(floor[:,:,:2]-c[:2]),-1,0)
    vis=visible & ~((near>0)&(far>=near)&(near<t))
    roi=vis&(dx<=1.1)&(dy<=.85)
    edge=roi&(abs(dx-h[0])<=.1)&(dy<=.82)
    o=floor[edge]+[0,0,.0003]
    j=np.arange(1024)
    v=np.array([int(f'{n:010b}'[::-1],2) for n in j])/1024
    phi=2*np.pi*(v+.000137)
    u=(j+.5)/1024
    directions=np.stack([np.sqrt(u)*np.cos(phi),np.sqrt(u)*np.sin(phi),np.sqrt(1-u)],axis=-1)
    hit=np.zeros((len(o),1024),bool)
    for b in [*boxes[1:],np.r_[c,h]]:
        ids=np.flatnonzero(np.all(abs(o-b[:3])<=b[3:]+1.12,axis=1))
        for start in range(0,len(ids),64):
            ix=ids[start:start+64]
            a,z=slab(o[ix,None],directions,b[:3],b[3:])
            hit[ix]|=np.maximum(0,a)<=np.minimum(1.12,z)
    return roi,edge,1-hit.mean(axis=1)
def pixels(path):
    return np.array(Image.open(path).convert('RGB'))[2::4,2::4]/255.
def luma(rgb):
    return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4) @ [.2126,.7152,.0722]
def summarize(site,out,s,gpu,timings):
    geom=geometry(s)
    rows={n:[] for n in NAMES}
    old={}
    for i in range(1,s['post_frames']+1):
        roi,edge,truth=regions(s,i,geom)
        ref=luma(pixels(site/f'ref-{i}.png'))
        for n in NAMES:
            ao=pixels(site/f'{n}-ao-{i}.png')[:,:,0]
            err=luma(pixels(site/f'{n}-beauty-{i}.png'))-ref
            r={'frame':i,'edge_pixels':int(edge.sum()),'floor_pixels':int(roi.sum()),'contact':float(abs(ao[edge]-truth).mean()),'signed_contact':float((ao[edge]-truth).mean()),'recovery':float(abs(err[roi]).mean()),'flicker':None,'time':float(np.median([p[n][i-1] for p in timings]))}
            if i>1:
                prev,mask=old[n]
                r['flicker']=float(np.percentile(abs(err-prev)[mask&roi],95))
            old[n]=(err,roi)
            rows[n].append(r)
    worst=max(range(1,s['post_frames']+1),key=lambda i:max(rows[n][i-1]['contact'] for n in NAMES))
    summary={}
    for n,rs in rows.items():
        summary[n]={}
        for key in ['contact','signed_contact','flicker','recovery','time']:
            pairs=[(r[key],r['frame']) for r in rs if r[key] is not None]
            v,f=max(pairs)
            summary[n][key]={'mean':float(np.mean([a for a,_ in pairs])),'worst':v,'frame':f}
        summary[n]['recovered']=next((i+1 for i in range(len(rs)-2) if all(r['recovery']<=.005 for r in rs[i:i+3])),None)
    result={'gpu':gpu,'summary':summary,'worst_contact_frame':worst,'frames':rows,'timing_blocks_ms':timings}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    media(site,out,s,rows,worst,geom)
def media(site,out,s,rows,worst,geom):
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
    def label(canvas,xy,msg,color='#ffffff'):
        ImageDraw.Draw(canvas).text(xy,msg,font=font,fill=color)
    writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x540','-r','12','-i','-','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'comparison.mp4')],stdin=subprocess.PIPE)
    for i in range(1-s['pre_frames'],1+s['post_frames']):
        panel=Image.new('RGB',(1280,540),'#15191c')
        for col,n in enumerate(NAMES):
            x=640*col
            src=Image.open(site/f'{n}-beauty-{i}.png').convert('RGB')
            panel.paste(src.resize((640,360),Image.Resampling.LANCZOS),(x,38))
            label(panel,(x+12,8),['Shipping  ·  809e8e6','Challenger  ·  Gallery brightness guard'][col])
            if i>0:
                r=rows[n][i-1]
                label(panel,(x+12,405),f"Contact MAE  {r['contact']:.4f}     Luma MAE  {r['recovery']:.5f}")
            else:
                label(panel,(x+12,405),'Establishing view')
        phase=f'After cut  ·  frame {i:02d} / 24' if i>0 else 'Before cut'
        label(panel,(12,461),phase+'     |     Archive · 20 cm clearance · half-speed playback','#a8d8ee')
        if i==worst:
            label(panel,(12,501),'Worst moving-edge contact frame','#ffca89')
            panel.save(out/'worst-frame.png')
        writer.stdin.write(panel.tobytes())
    writer.stdin.close()
    if writer.wait(): raise RuntimeError('ffmpeg failed')
    _,edge,truth=regions(s,worst,geom)
    vis=np.full(edge.shape,40,dtype=np.uint8)
    panel=Image.new('RGB',(960,224),'#15191c')
    for k,n in enumerate([*NAMES,'reference']):
        v=vis.copy()
        a=truth if k==2 else pixels(site/f'{n}-ao-{worst}.png')[:,:,0][edge]
        v[edge]=np.round(255*a).astype(np.uint8)
        panel.paste(Image.fromarray(v).convert('RGB'),(k*320,36))
        label(panel,(k*320+8,7),n+' · edge visibility')
    panel.save(out/'worst-edge.png')
