import json,os,sys,time,urllib.request,urllib.error
BASE="https://platform.higgsfield.ai";AUTH=f"Key {os.environ['HF_API_KEY']}:{os.environ['HF_API_SECRET']}"
RAW="https://raw.githubusercontent.com/tkwon94-create/Static-Ads/claude/skill-installation-h9wqve"
def req(m,u,d=None):
    h={"Authorization":AUTH,"User-Agent":"higgsfield-client-py/1.0","Accept":"application/json"}
    if d is not None:h["Content-Type"]="application/json"
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d else None,headers=h,method=m)
    for a in range(3):
        try:return json.loads(urllib.request.urlopen(r,timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code in(429,500,502,503,504) and a<2:time.sleep(2**a);continue
            return {"__error__":f"HTTP {e.code}: {e.read().decode()[:150]}"}
# jobs: (label, ref_filename, [product refs], promptfile)
JOBS=[
 ("16_claim_stat","ref-02-claim-stat-strip.png",["laventra_product.png"],"prompts/16_claim_stat.txt"),
 ("09_testimonial","ref-19-portrait-quote-attribution.png",["laventra_product.png","laventra_brush.png"],"prompts/09_testimonial.txt"),
 ("04_blame_reframe","ref-01-two-figure-blame-reframe.png",["laventra_product.png"],"prompts/04_blame_reframe.txt"),
]
def imgurl(name):
    if name.startswith("ref-"):return f"{RAW}/.claude/skills/winning-statics/references/{name}"
    return f"{RAW}/.workspace/inputs/{name}"
sets=[]
for label,ref,prods,pf in JOBS:
    imgs=[imgurl(ref)]+[imgurl(p) for p in prods]
    p={"params":{"prompt":open(pf).read(),"input_images":[{"type":"image_url","image_url":u} for u in imgs],"aspect_ratio":"1:1"}}
    sub=req("POST",f"{BASE}/v1/text2image/nano-banana",p)
    if "__error__" in sub:print(f"{label}: SUBMIT {sub['__error__']}");continue
    sets.append((label,sub["id"]));print(f"{label}: submitted {sub['id']}")
print("--- polling ---")
results={}
deadline=time.time()+600
while sets and time.time()<deadline:
    time.sleep(5)
    still=[]
    for label,sid in sets:
        js=req("GET",f"{BASE}/v1/job-sets/{sid}")
        if "__error__" in js:still.append((label,sid));continue
        job=js["jobs"][0];st=job["status"]
        if st=="completed":
            results[label]=job["results"]["raw"]["url"];print(f"{label}: DONE {results[label]}")
        elif st in("failed","nsfw"):print(f"{label}: {st}")
        else:still.append((label,sid))
    sets=still
open("proof_urls.json","w").write(json.dumps(results,indent=2))
print("\nRESULT URLS:");print(json.dumps(results,indent=2))
