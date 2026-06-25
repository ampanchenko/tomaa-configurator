import os, shutil
from PIL import Image

ROOT = "/Users/amp/Yandex.Disk.localized/tomaa/Конфигуратор"
SRC_BASE = os.path.join(ROOT, "images/base/10-Black.png")
SRC_SHARMS = os.path.join(ROOT, "images/sharms")
OUT = os.path.join(ROOT, "assets")

for d in ["bracelets","charms/gold","charms/silver","charms/preview/gold","charms/preview/silver"]:
    os.makedirs(os.path.join(OUT,d), exist_ok=True)

charms = {
 "Дракон":"dragon","Единорог":"unicorn","Иероглиф":"hieroglyph",
 "Клевер":"clover","Лапа":"paw","Подкова":"horseshoe",
 "Ракушка":"shell","Стрела":"arrow",
}

def trim_alpha(im, pad_frac=0.04):
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w,h = im.size
    side = max(w,h)
    pad = int(side*pad_frac)
    canvas = Image.new("RGBA",(side+2*pad, side+2*pad),(0,0,0,0))
    canvas.paste(im, ((side+2*pad-w)//2, (side+2*pad-h)//2), im)
    return canvas

def trim_white_square(im, pad_frac=0.07, out=260):
    """Каталожное фото на белом фоне → обрезать по объекту и вписать в единый квадрат
    (нормализует масштаб разнокалиберных фото)."""
    im = im.convert("RGB")
    gray = im.convert("L")
    mask = gray.point(lambda p: 255 if p < 244 else 0)  # объект = не белое
    bbox = mask.getbbox()
    if bbox:
        im = im.crop(bbox)
    w,h = im.size
    side = int(max(w,h) * (1 + 2*pad_frac))
    canvas = Image.new("RGB",(side,side),(255,255,255))
    canvas.paste(im, ((side-w)//2,(side-h)//2))
    return canvas.resize((out,out), Image.LANCZOS)

# Явный маппинг файлов каталожных превью (имена в исходниках не совпадают с шармами)
PREVIEW_FILES = {
  ("gold","dragon"):"Дракон.webp", ("gold","unicorn"):"Единорог.jpg",
  ("gold","hieroglyph"):"Иероглиф.jpg", ("gold","clover"):"Studio_Session-143__.jpg",
  ("gold","paw"):"Лапа.jpg", ("gold","horseshoe"):"ПОдкова.jpg",
  ("gold","shell"):"Ракушка.jpg", ("gold","arrow"):"Стрела.jpg",
  ("silver","dragon"):"WhatsApp_Image_2021-.jpg.webp", ("silver","unicorn"):"Studio_Session-175__.jpg",
  ("silver","hieroglyph"):"Studio_Session-217__.jpeg", ("silver","clover"):"Studio_Session-143__.jpg",
  ("silver","paw"):"Studio_Session-148__.jpg", ("silver","horseshoe"):"Studio_Session-225__.jpg",
  ("silver","shell"):"_silver_2.jpg", ("silver","arrow"):"Studio_Session-150__.jpg",
}

total=0
# ---- charms: gold/silver full + preview ----
for ru,en in charms.items():
    for src_dir, out_dir in [("gold","gold"),("Silver","silver")]:
        # full — фронтальный шарм с прозрачным фоном (для наложения на браслет)
        src = os.path.join(SRC_SHARMS, src_dir, ru+".png")
        im = Image.open(src).convert("RGBA")
        im = trim_alpha(im)               # обрезка по содержимому → единый масштаб у всех шармов
        full = im.resize((700,700), Image.LANCZOS)
        fp = os.path.join(OUT,"charms",out_dir,en+".webp")
        full.save(fp,"WEBP",quality=86,method=6)
        # preview — каталожное фото шарма (объёмное), нормализованное по масштабу.
        pp = os.path.join(OUT,"charms","preview",out_dir,en+".webp")
        prev_name = PREVIEW_FILES.get((out_dir,en))
        prev_path = os.path.join(SRC_SHARMS, src_dir, "preview", prev_name) if prev_name else None
        if prev_path and os.path.exists(prev_path):
            trim_white_square(Image.open(prev_path)).save(pp,"WEBP",quality=85,method=6)
        else:
            print("  ! нет превью для", out_dir, en, "->", prev_name)
            im.resize((240,240), Image.LANCZOS).save(pp,"WEBP",quality=84,method=6)
        total += os.path.getsize(fp)+os.path.getsize(pp)

# ---- single bracelets ----
b10 = Image.open(SRC_BASE).convert("RGBA")
W,H = b10.size
b10.save(os.path.join(OUT,"bracelets","single-10.webp"),"WEBP",quality=88,method=6)

scale_v = 1.45  # плейсхолдер 15мм = более широкий ремешок
b15 = b10.resize((W, int(H*scale_v)), Image.LANCZOS)
b15.save(os.path.join(OUT,"bracelets","single-15.webp"),"WEBP",quality=88,method=6)

STRAP_CENTER = 0.48  # центр ремешка по вертикали в одиночной картинке (замерено)

def make_double(strip, name):
    """Два одинаковых ремешка (верх+низ) с зазором. Возвращает % центров уровней."""
    h = strip.size[1]
    gap = int(h*0.20)
    ch = h + gap + h
    canvas = Image.new("RGBA",(W,ch),(255,255,255,255))
    canvas.paste(strip,(0,0)); canvas.paste(strip,(0,h+gap))
    canvas.save(os.path.join(OUT,"bracelets",name+".webp"),"WEBP",quality=88,method=6)
    top_lvl = (STRAP_CENTER*h)/ch*100
    bot_lvl = (h+gap+STRAP_CENTER*h)/ch*100
    return round(top_lvl,1), round(bot_lvl,1)

d10 = make_double(b10, "double-10")
d15 = make_double(b15, "double-15")

# remove obsolete combined file
old = os.path.join(OUT,"bracelets","double-10-15.webp")
if os.path.exists(old): os.remove(old)

for f in ["single-10","single-15","double-10","double-15"]:
    p=os.path.join(OUT,"bracelets",f+".webp")
    total+=os.path.getsize(p)
    print(f"bracelet {f:12} {os.path.getsize(p)//1024:3}KB")

print(f"TOTAL assets: {total//1024} KB")
print(f"LEVELS double-10: top={d10[0]}%  bottom={d10[1]}%")
print(f"LEVELS double-15: top={d15[0]}%  bottom={d15[1]}%")
