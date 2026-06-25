import csv, random
rows = list(csv.DictReader(open("manifests/in_the_wild.csv")))
real=[r for r in rows if r["label"]=="0"]; fake=[r for r in rows if r["label"]=="1"]
random.seed(0); random.shuffle(real); random.shuffle(fake)
N=2000; sub=real[:N]+fake[:N]; random.shuffle(sub)
with open("manifests/itw_small.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["path","label","dataset"])
    for r in sub: w.writerow([r["path"],r["label"],"in_the_wild"])
print("wrote",len(sub),"rows")
