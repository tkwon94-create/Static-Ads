#!/usr/bin/env python3
"""Gold-standard Laventra statics: generate the ad LAYOUT with the product area
reserved as a magenta placeholder, then composite your REAL product PNG into that
zone pixel-perfect — so no model ever redraws the tube or its label.

Runs anywhere images can be downloaded (i.e. NOT the locked web sandbox — your own
machine, or any unrestricted environment). Needs Pillow: pip install pillow

Setup:
  export HF_API_KEY=...          # your Higgsfield key id
  export HF_API_SECRET=...       # your Higgsfield secret
  # product photo: a clean straight-on tube on white (or transparent) background
  python3 gold_standard_ads.py --product laventra_user_tube.png --out out/ \
         --model nano-banana        # or: seedream
  # optional: --only 16,14,20  to (re)do specific ads

What it does per ad:
  1. Submits the layout prompt to Higgsfield with a "leave a solid #FF00FF magenta
     placeholder where the product goes, draw NO product" instruction.
  2. Polls, downloads the finished layout.
  3. Finds the magenta placeholder's bounding box.
  4. Scales your real product PNG to fit that box (preserving aspect), removes a
     near-white background if present, and alpha-composites it in.
  5. Saves the final ad — product is your exact pixels, everything else generated.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error, io
from collections import deque
try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

BASE = "https://platform.higgsfield.ai"
UA = "higgsfield-client-py/1.0"
RAW = "https://raw.githubusercontent.com/tkwon94-create/Static-Ads/claude/skill-installation-h9wqve"
REFDIR = ".claude/skills/winning-statics/references"

# ad number -> (prompt file under .workspace/laventra_prompts, reference filename, uses_product)
ADS = [
 ("01","01_anatomy","ref-09-anatomy-self-diagnosis.png",False),
 ("02","02_follicle_concern","ref-22-visceral-organ-concern.png",False),
 ("03","03_flashlight","ref-31-flashlight-label-expose.png",False),
 ("04","04_blame_reframe","ref-01-two-figure-blame-reframe.png",True),
 ("05","05_staged_timeline","ref-10-staged-transformation-timeline.png",True),
 ("06","06_lineart","ref-44-line-art-progress-map.png",True),
 ("07","07_daygrid","ref-11-day-stamped-healing-grid.png",False),
 ("08","08_split","ref-15-split-face-comparison.png",True),
 ("09","09_testimonial","ref-19-portrait-quote-attribution.png",True),
 ("10","10_postit","ref-14-post-it-handwritten-note.png",True),
 ("11","11_ama","ref-46-story-ama-frame.png",True),
 ("12","12_complement","ref-41-complement-table.png",True),
 ("13","13_whiteboard","ref-38-expert-whiteboard-checklist.png",True),
 ("14","14_callout","ref-12-formula-callout-x-pattern.png",True),
 ("15","15_reasons","ref-42-numbered-reasons-why.png",True),
 ("16","16_claim_stat","ref-02-claim-stat-strip.png",True),
 ("17","17_typescale","ref-36-type-scale-contrast-claim.png",True),
 ("18","18_price","ref-13-price-anchor-slash.png",True),
 ("19","19_editorial","ref-03-cultural-secret-long-headline.png",True),
 ("20","20_checklist","ref-50-benefit-checklist-portrait.png",True),
]

PLACEHOLDER = ("\n\nPRODUCT PLACEHOLDER — IMPORTANT: Do NOT draw the product tube or any "
    "product at all — not even a different bottle, jar, or stylized product. In the exact "
    "position, size, and orientation where the product should appear, paint a single SOLID "
    "FLAT pure magenta shape (maximum red, zero green, maximum blue; no gradient, no text, "
    "no shadow on it) as a placeholder for the product. Render everything else — headlines, "
    "body text, people, icons, background — normally and completely. The magenta shape must "
    "be the only magenta in the whole image. Never write any color name or hex code as "
    "visible text anywhere.")

def creds():
    k=os.environ.get("HF_API_KEY","").strip(); s=os.environ.get("HF_API_SECRET","").strip()
    if not k or not s: sys.exit("Set HF_API_KEY and HF_API_SECRET.")
    return k,s

def api(method,url,k,s,body=None):
    h={"Authorization":f"Key {k}:{s}","User-Agent":UA,"Accept":"application/json"}
    data=None
    if body is not None: data=json.dumps(body).encode(); h["Content-Type"]="application/json"
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    for a in range(4):
        try:
            with urllib.request.urlopen(r,timeout=180) as resp: return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503,504) and a<3: time.sleep(2**a); continue
            sys.exit(f"API {e.code}: {e.read().decode()[:200]}")

def download(url):
    r=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(r,timeout=180) as resp: return resp.read()

def gen_layout(num,pf,ref,usep,model,k,s,extra=""):
    prompt=open(f".workspace/laventra_prompts/{pf}.txt").read()
    imgs=[f"{RAW}/{REFDIR}/{ref}"]
    if usep: prompt+=PLACEHOLDER
    if extra: prompt+="\n\n"+extra
    body={"params":{"prompt":prompt,"input_images":[{"type":"image_url","image_url":u} for u in imgs],"aspect_ratio":"1:1"}}
    js=api("POST",f"{BASE}/v1/text2image/{model}",k,s,body); sid=js["id"]
    for _ in range(120):
        time.sleep(5); st=api("GET",f"{BASE}/v1/job-sets/{sid}",k,s); job=st["jobs"][0]
        if job["status"]=="completed": return download(job["results"]["raw"]["url"])
        if job["status"] in ("failed","nsfw"): print(f"  #{num} layout {job['status']}"); return None
    print(f"  #{num} layout timeout"); return None

def is_magenta(r,g,b):
    # strict pure magenta OR shaded crimson-magenta (models often draw the
    # placeholder as a magenta-colored 3D product with shading)
    return (r>180 and b>180 and g<110) or \
           (r>110 and g<r*0.55 and b>g and b-g>25 and r-g>60)

def find_magenta(img):
    """Magenta placeholder mask. Every component above noise size is masked
    (the model sometimes draws the placeholder in disconnected pieces, e.g. a
    separate brush tip); the bbox for product placement comes from the largest.
    Returns (mask 'L' image, bbox) or (None,None)."""
    im=img.convert("RGB"); px=im.load(); W,H=im.size
    mask=bytearray(W*H)
    for y in range(H):
        row=y*W
        for x in range(W):
            r,g,b=px[x,y]
            if is_magenta(r,g,b): mask[row+x]=1
    seen=bytearray(W*H); comps=[]
    for i in range(W*H):
        if mask[i] and not seen[i]:
            comp=[]; q=deque([i]); seen[i]=1
            while q:
                j=q.popleft(); comp.append(j)
                x=j%W; y=j//W
                for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0<=nx<W and 0<=ny<H:
                        k=ny*W+nx
                        if mask[k] and not seen[k]: seen[k]=1; q.append(k)
            if len(comp) >= 200: comps.append(comp)
    if not comps or max(len(c) for c in comps) < (W*H)//1000:
        return None,None  # stray pixels, not a placeholder
    best=max(comps,key=len)
    m=Image.new("L",(W,H),0); mp=m.load()
    for comp in comps:
        for j in comp: mp[j%W,j//W]=255
    minx,miny,maxx,maxy=W,H,-1,-1
    for j in best:
        x=j%W; y=j//W
        if x<minx:minx=x
        if x>maxx:maxx=x
        if y<miny:miny=y
        if y>maxy:maxy=y
    # second pass: inside the blob's neighborhood, sweep up lighter pink shading
    # (highlights on the drawn placeholder) that the strict threshold missed
    pad=24
    for y in range(max(0,miny-pad),min(H,maxy+pad+1)):
        for x in range(max(0,minx-pad),min(W,maxx+pad+1)):
            r,g,b=px[x,y]
            if r>170 and r-g>40 and b>g and b-g>20 and g<r*0.78:
                mp[x,y]=255
    return m,(minx,miny,maxx,maxy)

def inpaint(img,mask):
    """Fill masked pixels by multi-source BFS from the mask boundary, averaging
    already-known neighbors — a smooth smear that blends into photo backgrounds
    (a flat color patch is glaring there)."""
    im=img.convert("RGB"); px=im.load(); W,H=im.size; mp=mask.load()
    known=bytearray(W*H); q=deque()
    for y in range(H):
        row=y*W
        for x in range(W):
            if not mp[x,y]: known[row+x]=1
    for y in range(H):
        for x in range(W):
            if known[y*W+x]:
                for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0<=nx<W and 0<=ny<H and not known[ny*W+nx]:
                        q.append((x,y)); break
    while q:
        x,y=q.popleft()
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0<=nx<W and 0<=ny<H and not known[ny*W+nx]:
                rs=gs=bs=n=0
                for ax,ay in ((nx+1,ny),(nx-1,ny),(nx,ny+1),(nx,ny-1)):
                    if 0<=ax<W and 0<=ay<H and known[ay*W+ax]:
                        r,g,b=px[ax,ay]; rs+=r; gs+=g; bs+=b; n+=1
                if n:
                    px[nx,ny]=(rs//n,gs//n,bs//n)
                    known[ny*W+nx]=1; q.append((nx,ny))
    return im

def prep_product(prod_img):
    """Make the background transparent by flood-filling near-white from the image
    borders only — a white product body stays opaque. Then autocrop."""
    im=prod_img.convert("RGBA"); px=im.load(); W,H=im.size
    def bg(x,y):
        r,g,b,a=px[x,y]; return r>=249 and g>=249 and b>=249
    seen=bytearray(W*H); q=deque()
    for x in range(W):
        for y in (0,H-1):
            if bg(x,y) and not seen[y*W+x]: seen[y*W+x]=1; q.append((x,y))
    for y in range(H):
        for x in (0,W-1):
            if bg(x,y) and not seen[y*W+x]: seen[y*W+x]=1; q.append((x,y))
    while q:
        x,y=q.popleft(); px[x,y]=(255,255,255,0)
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0<=nx<W and 0<=ny<H and not seen[ny*W+nx] and bg(nx,ny):
                seen[ny*W+nx]=1; q.append((nx,ny))
    return im.crop(im.getbbox() or (0,0,W,H))

def composite(layout_bytes,product,out_path):
    layout=Image.open(io.BytesIO(layout_bytes)).convert("RGBA")
    mask,box=find_magenta(layout)
    if mask is None:
        layout.convert("RGB").save(out_path); return False
    l,t,r,b=box; bw,bh=r-l+1,b-t+1; W,H=layout.size
    # dilate the mask a few px to swallow anti-aliased magenta fringes
    mask=mask.filter(ImageFilter.MaxFilter(9))
    # fill the masked pixels by inpainting from their surroundings
    base=inpaint(layout,mask).convert("RGBA")
    prod=prep_product(product)
    scale=min(bw/prod.width,bh/prod.height)
    nw,nh=max(1,int(prod.width*scale)),max(1,int(prod.height*scale))
    prod=prod.resize((nw,nh),Image.LANCZOS)
    base.alpha_composite(prod,(l+(bw-nw)//2, t+(bh-nh)//2))
    base.convert("RGB").save(out_path); return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--product",required=True)
    ap.add_argument("--out",default="out")
    ap.add_argument("--model",default="nano-banana")
    ap.add_argument("--only",default="")
    ap.add_argument("--extra",default="",help="extra instruction appended to every prompt")
    a=ap.parse_args()
    k,s=creds(); os.makedirs(a.out,exist_ok=True)
    product=Image.open(a.product)
    only=set(x.strip() for x in a.only.split(",") if x.strip())
    for num,pf,ref,usep in ADS:
        if only and num not in only: continue
        print(f"#{num} {pf} ...")
        layout=gen_layout(num,pf,ref,usep,a.model,k,s,a.extra)
        if layout is None: continue
        ldir=os.path.join(a.out,"layouts"); os.makedirs(ldir,exist_ok=True)
        open(os.path.join(ldir,f"laventra_{num}_{pf}.layout.png"),"wb").write(layout)
        out=os.path.join(a.out,f"laventra_{num}_{pf}.png")
        if usep:
            ok=composite(layout,product,out)
            print(f"  saved {out} ({'product composited' if ok else 'NO magenta zone found — layout saved as-is'})")
        else:
            Image.open(io.BytesIO(layout)).convert("RGB").save(out); print(f"  saved {out} (no product in this concept)")
    print("done ->",a.out)

if __name__=="__main__":
    main()
