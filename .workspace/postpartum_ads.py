#!/usr/bin/env python3
"""Postpartum batch: same gold-standard pipeline as gold_standard_ads.py
(magenta placeholder layout -> composite the real tube), with its own
prompt set and ad->reference mapping."""
import argparse, os, sys, io, importlib.util
spec = importlib.util.spec_from_file_location("gsa", os.path.join(os.path.dirname(__file__), "gold_standard_ads.py"))
gsa = importlib.util.module_from_spec(spec); spec.loader.exec_module(gsa)
from PIL import Image

ADS = [
 ("p01","p01_anatomy","ref-49-shock-education-split.png",False),
 ("p02","p02_follicle","ref-22-visceral-organ-concern.png",False),
 ("p03","p03_blame","ref-01-two-figure-blame-reframe.png",True),
 ("p04","p04_ama","ref-40-oversized-quote-lead.png",True),
 ("p05","p05_postit","ref-14-post-it-handwritten-note.png",True),
 ("p06","p06_portrait","ref-19-portrait-quote-attribution.png",True),
 ("p07","p07_editorial","ref-03-cultural-secret-long-headline.png",True),
 ("p08","p08_lifestyle","ref-25-lifestyle-first-person-overlay.png",True),
 ("p09","p09_stat","ref-02-claim-stat-strip.png",True),
 ("p10","p10_cooling","ref-39-sensory-fear-claim.png",True),
]

def gen(num,pf,ref,usep,model,k,s,extra):
    prompt=open(f".workspace/postpartum_prompts/{pf}.txt").read()
    imgs=[f"{gsa.RAW}/{gsa.REFDIR}/{ref}"]
    if usep: prompt+=gsa.PLACEHOLDER
    if extra: prompt+="\n\n"+extra
    body={"params":{"prompt":prompt,"input_images":[{"type":"image_url","image_url":u} for u in imgs],"aspect_ratio":"1:1"}}
    js=gsa.api("POST",f"{gsa.BASE}/v1/text2image/{model}",k,s,body); sid=js["id"]
    import time
    for _ in range(120):
        time.sleep(5); st=gsa.api("GET",f"{gsa.BASE}/v1/job-sets/{sid}",k,s); job=st["jobs"][0]
        if job["status"]=="completed": return gsa.download(job["results"]["raw"]["url"])
        if job["status"] in ("failed","nsfw"): print(f"  {num} layout {job['status']}"); return None
    print(f"  {num} layout timeout"); return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--product",default=".workspace/inputs/laventra_user_tube.png")
    ap.add_argument("--out",default=".workspace/out_pp")
    ap.add_argument("--model",default="seedream")
    ap.add_argument("--only",default="")
    ap.add_argument("--extra",default="")
    a=ap.parse_args()
    k,s=gsa.creds(); os.makedirs(a.out,exist_ok=True)
    product=Image.open(a.product)
    only=set(x.strip() for x in a.only.split(",") if x.strip())
    for num,pf,ref,usep in ADS:
        if only and num not in only: continue
        print(f"{num} {pf} ...")
        layout=gen(num,pf,ref,usep,a.model,k,s,a.extra)
        if layout is None: continue
        ldir=os.path.join(a.out,"layouts"); os.makedirs(ldir,exist_ok=True)
        open(os.path.join(ldir,f"{num}_{pf}.layout.png"),"wb").write(layout)
        out=os.path.join(a.out,f"laventra_{num}_{pf}.png")
        if usep:
            ok=gsa.composite(layout,product,out)
            print(f"  saved {out} ({'product composited' if ok else 'NO magenta zone'})")
        else:
            Image.open(io.BytesIO(layout)).convert("RGB").save(out); print(f"  saved {out} (no product)")
    print("done ->",a.out)

if __name__=="__main__":
    main()
