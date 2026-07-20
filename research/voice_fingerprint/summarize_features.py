"""VFP-03 Task 3: Feature summary statistics per register."""
import json
import time
import math
import statistics
from collections import defaultdict

INPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\features.jsonl"
OUT_JSON = r"D:\Projects\SCRVNR\research\voice_fingerprint\feature_summary.json"
OUT_MD = r"D:\Projects\SCRVNR\research\voice_fingerprint\feature_summary.md"
OUT_RARITY = r"D:\Projects\SCRVNR\research\voice_fingerprint\rarity_by_register.json"

NUMERIC_FEATURES = [
    "word_count", "unique_words", "type_token_ratio", "mean_word_length",
    "mean_zipf", "median_zipf", "min_zipf", "pct_rare", "pct_very_rare",
    "pct_unknown", "sentence_count", "mean_sentence_len", "median_sentence_len",
    "max_sentence_len", "min_sentence_len", "std_sentence_len", "sentence_len_skew",
    "question_count", "question_density",
    "contraction_count", "contraction_rate",
    "caps_emphasis_count", "caps_emphasis_rate",
    "profanity_count", "profanity_rate",
    "double_period_count", "hyphen_count", "em_dash_count",
    "exclamation_count", "ellipsis_count", "number_density",
]
RARITY_BINS = [(1.0,2.0),(2.0,3.0),(3.0,4.0),(4.0,5.0),(5.0,6.0),(6.0,10.0)]
SENT_LEN_BINS = [(1,5),(5,10),(10,15),(15,20),(20,30),(30,999)]

def pctl(data, p):
    if not data: return None
    s = sorted(data)
    k = (len(s)-1)*(p/100); f=math.floor(k); c=math.ceil(k)
    return s[int(k)] if f==c else s[f]*(c-k)+s[c]*(k-f)

def bc_calc(values):
    """Bimodality coefficient: (skew^2+1)/kurtosis. >0.555 = bimodal."""
    if len(values) < 4: return None
    n=len(values); m=sum(values)/n
    var=sum((x-m)**2 for x in values)/n
    if var==0: return None
    std=math.sqrt(var)
    skew=sum(((x-m)/std)**3 for x in values)/n
    kurt=sum(((x-m)/std)**4 for x in values)/n
    return (skew**2+1)/kurt if kurt!=0 else None

def compute_stats(values):
    vals=[float(v) for v in values if v is not None]
    if not vals: return None
    m=sum(vals)/len(vals)
    if len(vals)>1:
        std_val=math.sqrt(sum((x-m)**2 for x in vals)/len(vals))
    else:
        std_val=0.0
    return {
        "count":len(vals),"mean":round(m,4),
        "median":round(sorted(vals)[len(vals)//2],4),
        "std":round(std_val,4),
        "min":round(min(vals),4),"max":round(max(vals),4),
        "p5":round(pctl(vals,5),4),"p25":round(pctl(vals,25),4),
        "p75":round(pctl(vals,75),4),"p95":round(pctl(vals,95),4),
    }

def bin_value(val, bins):
    for lo,hi in bins:
        if lo<=val<hi: return f"{lo}-{hi}"
    return None

def main():
    start=time.time()
    reg_data=defaultdict(lambda:defaultdict(list))
    reg_rarity_hist=defaultdict(lambda:defaultdict(int))
    reg_sent_hist=defaultdict(lambda:defaultdict(int))
    total=0

    with open(INPUT,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            rec=json.loads(line); total+=1
            reg=rec.get("register","UNKNOWN")
            for feat in NUMERIC_FEATURES:
                val=rec.get(feat)
                if val is not None: reg_data[reg][feat].append(float(val))
            mz=rec.get("mean_zipf")
            if mz is not None:
                b=bin_value(float(mz),RARITY_BINS)
                if b: reg_rarity_hist[reg][b]+=1
            msl=rec.get("mean_sentence_len")
            if msl is not None and msl>0:
                b=bin_value(float(msl),SENT_LEN_BINS)
                if b: reg_sent_hist[reg][b]+=1

    registers=sorted(reg_data.keys())
    print(f"Loaded {total:,} messages across {len(registers)} registers\n")

    # Build summary
    summary={}
    for reg in registers:
        summary[reg]={}
        for feat in NUMERIC_FEATURES:
            vals=reg_data[reg].get(feat,[])
            summary[reg][feat]=compute_stats(vals)
    with open(OUT_JSON,"w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)
    print(f"Wrote {OUT_JSON}")

    # Rarity histograms
    bin_labels=[f"{lo}-{hi}" for lo,hi in RARITY_BINS]
    rarity_data={}
    for reg in registers:
        rarity_data[reg]={b:reg_rarity_hist[reg].get(b,0) for b in bin_labels}
    with open(OUT_RARITY,"w",encoding="utf-8") as f:
        json.dump(rarity_data,f,indent=2,ensure_ascii=False)
    print(f"Wrote {OUT_RARITY}")

    # Bimodality
    bimod={}
    for reg in ["TECH","CREATIVE_DIRECTION"]:
        vals=reg_data.get(reg,{}).get("mean_sentence_len",[])
        bc=bc_calc(vals) if vals else None
        bimod[reg]={"bc":round(bc,4) if bc else None,"bimodal":bc>0.555 if bc else None,"n":len(vals)}

    # Cross-register rankings
    cross={}
    for feat in NUMERIC_FEATURES:
        ranks=[]
        for reg in registers:
            s=summary[reg].get(feat)
            if s and s.get("mean") is not None: ranks.append((reg,s["mean"]))
        ranks.sort(key=lambda x:-x[1])
        cross[feat]={"highest":ranks[0] if ranks else None,"lowest":ranks[-1] if ranks else None}

    # Write markdown
    with open(OUT_MD,"w",encoding="utf-8") as md:
        md.write("# Feature Summary Statistics\n\n")
        md.write(f"Total messages: {total:,} | Registers: {len(registers)}\n\n")
        md.write("## Key Metrics by Register\n\n")
        md.write("| Register | N | Mean Words | Mean Zipf | Contract Rate | Caps Rate | Profanity Rate | Q Density |\n")
        md.write("|----------|---|-----------|-----------|--------------|-----------|---------------|----------|\n")
        for reg in registers:
            s=summary[reg]
            n=s["word_count"]["count"] if s.get("word_count") else 0
            mw=s["word_count"]["mean"] if s.get("word_count") else 0
            mz=s["mean_zipf"]["mean"] if s.get("mean_zipf") else 0
            cr=s["contraction_rate"]["mean"] if s.get("contraction_rate") else 0
            ce=s["caps_emphasis_rate"]["mean"] if s.get("caps_emphasis_rate") else 0
            pr=s["profanity_rate"]["mean"] if s.get("profanity_rate") else 0
            qd=s["question_density"]["mean"] if s.get("question_density") else 0
            md.write(f"| {reg} | {n:,} | {mw:.1f} | {mz:.2f} | {cr:.2f} | {ce:.2f} | {pr:.2f} | {qd:.3f} |\n")

        md.write("\n## Vocabulary Rarity Distribution by Register (Kite Shape)\n\n")
        md.write("| Register | "+" | ".join(bin_labels)+" |\n")
        md.write("|----------|"+"|".join(["---"]*len(bin_labels))+"|\n")
        for reg in registers:
            v=[str(rarity_data[reg].get(b,0)) for b in bin_labels]
            md.write(f"| {reg} | "+" | ".join(v)+" |\n")

        sl_labels=[f"{lo}-{hi}" for lo,hi in SENT_LEN_BINS]
        md.write("\n## Sentence Length Distribution by Register\n\n")
        md.write("| Register | "+" | ".join(sl_labels)+" |\n")
        md.write("|----------|"+"|".join(["---"]*len(sl_labels))+"|\n")
        for reg in registers:
            v=[str(reg_sent_hist[reg].get(b,0)) for b in sl_labels]
            md.write(f"| {reg} | "+" | ".join(v)+" |\n")

        md.write("\n## Bimodality Detection (Sentence Length)\n\n")
        for reg,res in bimod.items():
            md.write(f"- **{reg}**: BC={res['bc']}, bimodal={res['bimodal']} (n={res['n']})\n")

        md.write("\n## Cross-Register Feature Rankings (by mean)\n\n")
        for feat in ["mean_zipf","contraction_rate","profanity_rate","caps_emphasis_rate",
                     "question_density","mean_sentence_len","type_token_ratio","pct_rare"]:
            cr=cross.get(feat,{})
            hi,lo=cr.get("highest"),cr.get("lowest")
            if hi and lo:
                md.write(f"- **{feat}**: highest={hi[0]} ({hi[1]:.3f}), lowest={lo[0]} ({lo[1]:.3f})\n")

    print(f"Wrote {OUT_MD}")
    elapsed=time.time()-start
    print(f"\nDone in {elapsed:.1f}s")
    with open(OUT_MD,"r",encoding="utf-8") as f:
        print(f.read())

if __name__=="__main__":
    main()
