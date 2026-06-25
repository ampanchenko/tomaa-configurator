"""Скачивает каталожные фото шармов (золото/серебро) с tildacdn и нормализует их в
единый квадрат (обрезка по контуру на белом фоне) — для палитры. Превью новых шармов
становятся одного размера с шармами серии «Удача» и лёгкими по весу.
Превью кладутся в assets/charms/preview/{gold,silver}/u{TildaUID}.webp"""
import csv, os, io, urllib.request
from PIL import Image

ROOT="/Users/amp/Yandex.Disk.localized/tomaa/Конфигуратор"
CSV="/Users/amp/Downloads/store-1344131-Katalog_sharmov-202606251754.csv"
OUTG=os.path.join(ROOT,"assets/charms/preview/gold")
OUTS=os.path.join(ROOT,"assets/charms/preview/silver")
NAME2LOC={'Дракон благополучия','Волшебный единорог','Счастье, японский иероглиф','Клевер большой удачи',
 'Мягкая лапка','Сила подковы','Талисман-ракушка','Стрела в цель'}

def trim_white_square(im, pad_frac=0.07, out=260):
    im=im.convert("RGB"); g=im.convert("L")
    bbox=g.point(lambda p:255 if p<244 else 0).getbbox()
    if bbox: im=im.crop(bbox)
    w,h=im.size; side=int(max(w,h)*(1+2*pad_frac))
    c=Image.new("RGB",(side,side),(255,255,255)); c.paste(im,((side-w)//2,(side-h)//2))
    return c.resize((out,out),Image.LANCZOS)

rows=[r for r in csv.reader(open(CSV,encoding='utf-8'),delimiter=';') if r and r[0].strip()][1:]
parents={}
for r in rows:
    if not r[15]:
        parents[r[0]]={'name':r[5].replace('Шарм: ','').strip(),'g':None,'s':None}
for r in rows:
    p=r[15]
    if p not in parents or not r[8]: continue
    pl='g' if 'Золото' in r[12] else 's'
    if not parents[p][pl]: parents[p][pl]=r[8]

def fetch(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return Image.open(io.BytesIO(urllib.request.urlopen(req,timeout=20).read()))

done=0; skip=0; nogold=[]
for uid,p in parents.items():
    if p['name'] in NAME2LOC: skip+=1; continue   # у «Удачи» уже есть локальные превью
    g=p['g'] or p['s']; s=p['s'] or p['g']
    if not p['g']: nogold.append(p['name'])
    try:
        trim_white_square(fetch(g)).save(os.path.join(OUTG,"u"+uid+".webp"),"WEBP",quality=84,method=6)
        trim_white_square(fetch(s)).save(os.path.join(OUTS,"u"+uid+".webp"),"WEBP",quality=84,method=6)
        done+=1
    except Exception as e:
        print("  ! ",p['name'],e)
print(f"обработано {done} шармов, пропущено (Удача) {skip}")
print(f"без отдельного золотого фото ({len(nogold)}):", ", ".join(nogold) if nogold else "—")
