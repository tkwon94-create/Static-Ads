import json,os,time,urllib.request,urllib.error
BASE="https://platform.higgsfield.ai";AUTH=f"Key {os.environ['HF_API_KEY']}:{os.environ['HF_API_SECRET']}"
RAW="https://raw.githubusercontent.com/tkwon94-create/Static-Ads/claude/skill-installation-h9wqve"
def req(m,u,d=None):
    h={"Authorization":AUTH,"User-Agent":"higgsfield-client-py/1.0","Accept":"application/json"}
    if d is not None:h["Content-Type"]="application/json"
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d else None,headers=h,method=m)
    for a in range(4):
        try:return json.loads(urllib.request.urlopen(r,timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code in(429,500,502,503,504) and a<3:time.sleep(2**a);continue
            return {"__error__":f"HTTP {e.code}: {e.read().decode()[:120]}"}
        except urllib.error.URLError as e:
            if a<3:time.sleep(2**a);continue
            return {"__error__":str(e)}
PROD=["laventra_product.png","laventra_brush.png"]
P1=["laventra_product.png"]
# (num, promptfile, ref, product_inputs)
JOBS=[
 ("01","01_anatomy","ref-09-anatomy-self-diagnosis.png",[]),
 ("02","02_follicle_concern","ref-22-visceral-organ-concern.png",[]),
 ("03","03_flashlight","ref-31-flashlight-label-expose.png",[]),
 ("04","04_blame_reframe","ref-01-two-figure-blame-reframe.png",P1),
 ("05","05_staged_timeline","ref-10-staged-transformation-timeline.png",P1),
 ("06","06_lineart","ref-44-line-art-progress-map.png",P1),
 ("07","07_daygrid","ref-11-day-stamped-healing-grid.png",[]),
 ("08","08_split","ref-15-split-face-comparison.png",P1),
 ("09","09_testimonial","ref-19-portrait-quote-attribution.png",PROD),
 ("10","10_postit","ref-14-post-it-handwritten-note.png",P1),
 ("11","11_ama","ref-46-story-ama-frame.png",PROD),
 ("12","12_complement","ref-41-complement-table.png",P1),
 ("13","13_whiteboard","ref-38-expert-whiteboard-checklist.png",P1),
 ("14","14_callout","ref-12-formula-callout-x-pattern.png",PROD),
 ("15","15_reasons","ref-42-numbered-reasons-why.png",P1),
 ("16","16_claim_stat","ref-02-claim-stat-strip.png",P1),
 ("17","17_typescale","ref-36-type-scale-contrast-claim.png",P1),
 ("18","18_price","ref-13-price-anchor-slash.png",P1),
 ("19","19_editorial","ref-03-cultural-secret-long-headline.png",P1),
 ("20","20_checklist","ref-50-benefit-checklist-portrait.png",PROD),
]
def u_ref(n):return f"{RAW}/.claude/skills/winning-statics/references/{n}"
def u_in(n):return f"{RAW}/.workspace/inputs/{n}"
# load prior results if resuming
results={}
if os.path.exists("all_urls.json"):results=json.load(open("all_urls.json"))
sets=[]
for num,pf,ref,prods in JOBS:
    if num in results:continue
    imgs=[u_ref(ref)]+[u_in(x) for x in prods]
    body={"params":{"prompt":open(f"prompts/{pf}.txt").read(),
        "input_images":[{"type":"image_url","image_url":u} for u in imgs],"aspect_ratio":"1:1"}}
    sub=req("POST",f"{BASE}/v1/text2image/nano-banana",body)
    if "__error__" in sub:print(f"#{num} SUBMIT-ERR {sub['__error__']}");continue
    sets.append((num,pf,ref,prods,sub["id"]));print(f"#{num} submitted {sub['id']}")
    time.sleep(0.5)
print("--- polling",len(sets),"jobs ---")
deadline=time.time()+1200
retry_pool=[]
while sets and time.time()<deadline:
    time.sleep(6);still=[]
    for num,pf,ref,prods,sid in sets:
        js=req("GET",f"{BASE}/v1/job-sets/{sid}")
        if "__error__" in js:still.append((num,pf,ref,prods,sid));continue
        job=js["jobs"][0];st=job["status"]
        if st=="completed":
            results[num]=job["results"]["raw"]["url"];print(f"#{num} DONE")
            json.dumps(results)  # noop
        elif st in("failed","nsfw"):print(f"#{num} {st}");retry_pool.append((num,pf,ref,prods))
        else:still.append((num,pf,ref,prods,sid))
    sets=still
    json.dump(results,open("all_urls.json","w"),indent=2)
json.dump(results,open("all_urls.json","w"),indent=2)
print(f"\nCOMPLETED {len(results)}/20")
for num,pf,ref,prods in JOBS:
    if num in results:print(f"#{num} {pf}: {results[num]}")
    else:print(f"#{num} {pf}: (not completed)")
