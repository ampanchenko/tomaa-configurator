"""Перекраска базовой формы браслета в цвета каталога (кожа/бархат).
Использует ImageOps.colorize по яркости: тёмные участки -> dark, светлые -> light.
Фон делается прозрачным. Запускать после build_assets.py."""
import json, os
from PIL import Image, ImageOps

ROOT="/Users/amp/Yandex.Disk.localized/tomaa/Конфигуратор"
OUT=os.path.join(ROOT,"assets","bracelets")
GEOMS=["single-10","single-15","double-10","double-15"]

# (dark, light) для colorize — подобраны под текстуру кожи
PAIRS={
 "leather":{
   "black":("#0a0a0a","#3c3c3c"), "brown":("#170d06","#6e4628"),
   "bordo":("#1c0a10","#7e2e42"), "red":("#2c0a0a","#b23030"),
   "powder":("#8c6155","#edd3c8"), "white":("#b2a99d","#f5f1e9"),
 },
 "velvet":{
   "blue":("#2c4a63","#a6c8e0"), "ruby":("#230810","#92263a"),
   "turquoise":("#0a3838","#33a6a6"), "grey":("#4a4a52","#c4c4ca"),
   "orange":("#5e2f0e","#ef9d50"), "powder":("#8c6155","#edd3c8"),
 },
}
def hx(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))

uid=json.load(open("/tmp/bases_uid.json")) if os.path.exists("/tmp/bases_uid.json") else None
total=0; n=0
for geom in GEOMS:
    src=Image.open(os.path.join(OUT, geom+".webp")).convert("RGBA")
    gray=src.convert("L")
    alpha=gray.point(lambda p: 0 if p>=236 else 255)   # фон (белое) -> прозрачно
    for mat,cols in PAIRS.items():
        for cid,(dk,lt) in cols.items():
            # генерим только реально существующие в каталоге комбинации (если есть карта uid)
            if uid and not uid.get(mat,{}).get(geom,{}).get(cid): continue
            col=ImageOps.colorize(gray, hx(dk), hx(lt)).convert("RGBA")
            col.putalpha(alpha)
            p=os.path.join(OUT, f"{geom}-{mat}-{cid}.webp")
            col.save(p,"WEBP",quality=88,method=6)
            total+=os.path.getsize(p); n+=1
print(f"сгенерировано {n} браслетов, {total//1024} KB")
