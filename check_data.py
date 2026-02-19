import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('data.json', encoding='utf-8'))
imgs = [s['image'] for s in d['series'] if s['image']]
print(f"Total series: {d['total']}")
print(f"With images: {len(imgs)}")
print("First 5:")
for s in d['series'][:5]:
    print(f"  {s['title']}: {s['image'][:70] if s['image'] else '(no image)'}")
