import json,os,time,urllib.request,urllib.error
BASE="https://platform.higgsfield.ai";AUTH=f"Key {os.environ['HF_API_KEY']}:{os.environ['HF_API_SECRET']}"
RAW="https://raw.githubusercontent.com/tkwon94-create/Static-Ads/claude/skill-installation-h9wqve"
HERO="https://d3u0tzju9qaucj.cloudfront.net/1c0bbe60-da3c-4723-aae6-a16da75136ad/ecc95869-365a-4cc4-9de5-a75add5c8d1a.png"
def req(m,u,d=None):
    h={"Authorization":AUTH,"User-Agent":"higgsfield-client-py/1.0","Accept":"application/json"}
    if d is not None:h["Content-Type"]="application/json"
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d else None,headers=h,method=m)
    for a in range(4):
        try:return json.loads(urllib.request.urlopen(r,timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code in(429,500,502,503,504) and a<3:time.sleep(2**a);continue
            return {"__error__":f"HTTP {e.code}: {e.read().decode()[:120]}"}
        except urllib.error.URLError:
            if a<3:time.sleep(2**a);continue
            return {"__error__":"urlerror"}
# (num, promptfile, ref, uses_product)
JOBS=[
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
results=json.load(open("all_urls_v2.json")) if os.path.exists("all_urls_v2.json") else {}
sets=[]
for num,pf,ref,usep in JOBS:
    if num in results:continue
    imgs=[f"{RAW}/.claude/skills/winning-statics/references/{ref}"]+([HERO] if usep else [])
    body={"params":{"prompt":open(f"prompts/{pf}.txt").read(),
        "input_images":[{"type":"image_url","image_url":u} for u in imgs],"aspect_ratio":"1:1"}}
    sub=req("POST",f"{BASE}/v1/text2image/nano-banana",body)
    if "__error__" in sub:print(f"#{num} SUBMIT-ERR {sub['__error__']}");continue
    sets.append((num,sub["id"]));print(f"#{num} submitted")
    time.sleep(0.4)
print("--- polling",len(sets),"---")
dead=time.time()+1200
while sets and time.time()<dead:
    time.sleep(6);still=[]
    for num,sid in sets:
        js=req("GET",f"{BASE}/v1/job-sets/{sid}")
        if "__error__" in js:still.append((num,sid));continue
        job=js["jobs"][0];st=job["status"]
        if st=="completed":results[num]=job["results"]["raw"]["url"];print(f"#{num} DONE")
        elif st in("failed","nsfw"):print(f"#{num} {st}")
        else:still.append((num,sid))
    sets=still;json.dump(results,open("all_urls_v2.json","w"),indent=2)
json.dump(results,open("all_urls_v2.json","w"),indent=2)
print(f"\nCOMPLETED {len(results)}/20")
for num,pf,ref,usep in JOBS:print(f"#{num} {pf}: {results.get(num,'(missing)')}")
