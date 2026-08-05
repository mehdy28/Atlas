
import re
import math
import hashlib
from PIL import Image, ImageDraw, ImageFont

def ease_out_cubic(t):
    t = max(0, min(t, 1.0))
    return 1 - (1 - t) ** 3

def ease_out_back(t, overshoot=1.6):
    t = max(0, min(t, 1.0))
    c1 = overshoot; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_in_out(t):
    t = max(0, min(t, 1.0))
    return t * t * (3 - 2 * t)

def new_canvas(width, height):
    return Image.new("RGBA", (width, height), (0, 0, 0, 0))

def text_with_shadow(draw, xy, text, font, fill, shadow, off=(3, 3)):
    x, y = xy
    draw.text((x+off[0], y+off[1]), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

def autofit_font(draw, text, font_path, max_width, max_height, start_size=90, min_size=20, wrap=True):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        if wrap:
            words, lines, cur = text.split(), [], ""
            for w in words:
                cand = (cur + " " + w).strip()
                bbox = draw.textbbox((0, 0), cand, font=font)
                if bbox[2]-bbox[0] <= max_width or not cur:
                    cur = cand
                else:
                    lines.append(cur); cur = w
            if cur: lines.append(cur)
        else:
            lines = [text]
        line_h = int(round(size * 1.3))
        total_h = line_h * len(lines)
        max_line_w = max(draw.textbbox((0,0), l, font=font)[2] for l in lines)
        if total_h <= max_height and max_line_w <= max_width:
            return font, lines, line_h
        size -= 4
    font = ImageFont.truetype(font_path, min_size)
    return font, [text], int(round(min_size * 1.3))

def reveal_bottom_to_top(layer, progress, box=None):
    w, h = layer.size
    if box is None: box = (0, 0, w, h)
    x0, y0, x1, y1 = box
    visible_h = int((y1-y0) * ease_out_cubic(progress))
    mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(mask).rectangle([x0, y1-visible_h, x1, y1], fill=255)
    out = Image.new("RGBA", layer.size, (0,0,0,0))
    out.paste(layer, (0,0), mask)
    return out

def fade_alpha(img, factor):
    r,g,b,a = img.split()
    img.putalpha(a.point(lambda p: int(p*max(0,min(factor,1)))))
    return img

def navy_panel(w, h, palette, radius=22, accent_left=True):
    w, h = int(w), int(h)
    p = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(p)
    d.rounded_rectangle([0,0,w-1,h-1], radius=radius, fill=palette["navy_panel"])
    if accent_left: d.rectangle([0,0,10,h], fill=palette["orange"])
    return p, d

def extract_percent(text):
    m = re.search(r"(\d+(\.\d+)?)\s*%", str(text))
    return float(m.group(1)) if m else None

def pick_variant(candidates, seed_key):
    h = int(hashlib.md5(str(seed_key).encode()).hexdigest(), 16)
    return candidates[h % len(candidates)]


# ============== STYLE FUNCTIONS ==============
# Each: fn(t, content, W, H, fonts, palette) -> RGBA Image, size (W,H)

def s_lower_third(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    heading = str(content.get("heading", content.get("stat", ""))).upper()
    body = str(content.get("body", content.get("label", "")))
    bar_h = 210; y = H - bar_h
    panel = Image.new("RGBA", (W, bar_h), (0,0,0,0))
    pd = ImageDraw.Draw(panel)
    pd.rectangle([0,0,W,bar_h], fill=palette["navy_panel"])
    pd.rectangle([0,0,12,bar_h], fill=palette["orange"])
    f1 = ImageFont.truetype(fonts["bold"], 48); f2 = ImageFont.truetype(fonts["reg"], 27)
    text_with_shadow(pd, (55,48), heading, f1, palette["white"], palette["shadow"])
    pd.text((55,118), body, font=f2, fill=palette["offwhite"])
    rev = reveal_bottom_to_top(panel, min(t/0.4,1.0))
    fo = 1.0 if t<0.85 else max(1-(t-0.85)/0.15,0)
    if fo<1: rev = fade_alpha(rev, fo)
    img.alpha_composite(rev, (0,y))
    return img

def s_typewriter(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    full_text = str(content.get("body", content.get("heading","")))
    measure = ImageDraw.Draw(Image.new("RGBA",(10,10)))
    font, lines, line_h = autofit_font(measure, full_text, fonts["bold"], W*0.7, 200, start_size=58, wrap=False)
    fw = measure.textbbox((0,0), full_text, font=font)[2]
    strip_w, strip_h = int(fw+160), int(line_h+120)
    panel, pd = navy_panel(strip_w, strip_h, palette, radius=20, accent_left=False)
    chars_shown = int(len(full_text)*min(t/0.75,1.0)); shown = full_text[:chars_shown]
    text_with_shadow(pd, (80,60), shown, font, palette["white"], palette["shadow"])
    if chars_shown < len(full_text) and int(t*10)%2==0:
        bb = pd.textbbox((0,0), shown, font=font)
        pd.rectangle([80+bb[2]+8,55,80+bb[2]+16,55+line_h], fill=palette["orange"])
    img.alpha_composite(panel, ((W-strip_w)//2,(H-strip_h)//2))
    return img

def s_corner_chip(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    tag = str(content.get("heading","KEY FACT")).upper()[:20]
    body = str(content.get("body", content.get("stat","")))
    chip_w, chip_h = 620, 160
    panel, pd = navy_panel(chip_w, chip_h, palette, radius=18)
    f1=ImageFont.truetype(fonts["bold"],36); f2=ImageFont.truetype(fonts["reg"],24)
    pd.text((45,32),tag,font=f2,fill=palette["orange"])
    text_with_shadow(pd,(45,68),body[:36],f1,palette["white"],palette["shadow"])
    slide = ease_out_cubic(min(t/0.3,1.0))
    x = W-int(chip_w*slide)-40; y=60
    fo = 1.0 if t<0.85 else max(1-(t-0.85)/0.15,0)
    panel2 = fade_alpha(panel, fo) if fo<1 else panel
    img.alpha_composite(panel2,(x,y))
    return img

def s_breaking_banner(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    text = str(content.get("body", content.get("heading","")))
    bar_h = 120; slide = ease_out_cubic(min(t/0.25,1.0)); y = -bar_h+int(bar_h*slide)
    banner = Image.new("RGBA",(W,bar_h),palette["navy_panel"]); bd = ImageDraw.Draw(banner)
    badge_w=230; bd.rectangle([0,0,badge_w,bar_h],fill=palette["orange"])
    fb=ImageFont.truetype(fonts["bold"],30); bd.text((30,bar_h//2-18),"ANALYSIS",font=fb,fill=palette["navy_deep"])
    ft=ImageFont.truetype(fonts["bold"],34); text_with_shadow(bd,(badge_w+30,bar_h//2-20),text[:60],ft,palette["white"],palette["shadow"])
    fo = 1.0 if t<0.85 else max(1-(t-0.85)/0.15,0)
    banner2 = fade_alpha(banner, fo) if fo<1 else banner
    img.alpha_composite(banner2,(0,y))
    return img

def s_highlight_sweep(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    body = str(content.get("body", content.get("heading","")))
    words = body.split()
    keyword_idx = max(0, len(words)//2)
    keyword = words[keyword_idx] if words else ""
    draw = ImageDraw.Draw(img)
    panel_w, panel_h = min(W-160, 1500), 240
    panel, pd = navy_panel(panel_w, panel_h, palette, radius=20, accent_left=False)
    font, lines, line_h = autofit_font(pd, body, fonts["bold"], panel_w-100, 160, start_size=48)
    y0 = (panel_h - line_h*len(lines))//2
    for line in lines:
        lw = pd.textbbox((0,0), line, font=font)[2]
        x0 = (panel_w-lw)//2
        if keyword.strip(".,") in line:
            kw_bbox = pd.textbbox((0,0), keyword, font=font)
            sweep = ease_out_cubic(min(max((t-0.15)/0.35,0),1.0))
            pd.rectangle([x0,y0+8,x0+int((kw_bbox[2])*sweep),y0+line_h-8], fill=palette["orange"])
        pd.text((x0,y0), line, font=font, fill=palette["white"])
        y0 += line_h
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_diagonal_wipe(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    text = str(content.get("heading","")).upper()
    progress = ease_in_out(min(t/0.5,1.0)); offset = int(-W*1.4*(1-progress))
    layer = Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    poly=[(offset,0),(offset+W*0.7,0),(offset+W*0.3,H),(offset,H)]
    ld.polygon(poly, fill=palette["navy_panel"])
    img.alpha_composite(layer)
    draw = ImageDraw.Draw(img)
    if progress>0.75:
        font, lines, line_h = autofit_font(draw, text, fonts["bold"], W*0.5, 200, start_size=64)
        y = H//2-line_h
        for line in lines:
            text_with_shadow(draw,(150,y),line,font,palette["white"],palette["shadow"])
            y += line_h
    return img

def s_word_cascade(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    heading = str(content.get("heading","")).upper()
    words = (heading + " " + str(content.get("body",""))).split()[:5]
    if not words: words = ["KEY", "POINT."]
    font = ImageFont.truetype(fonts["bold"], 78)
    measure = ImageDraw.Draw(Image.new("RGBA",(10,10)))
    line_h = 96; total_h = line_h*len(words); y0 = (H-total_h)//2
    per_word = 0.85 / max(1,len(words))
    for idx, word in enumerate(words):
        w_start = idx*per_word
        progress = min(max((t-w_start)/0.22,0),1.0)
        if progress<=0: continue
        color = palette["orange"] if idx == len(words)-1 else palette["white"]
        wbb = measure.textbbox((0,0), word, font=font); ww = wbb[2]-wbb[0]
        layer = Image.new("RGBA",(W,H),(0,0,0,0)); ld = ImageDraw.Draw(layer)
        x = (W-ww)//2; y = y0 + idx*line_h
        text_with_shadow(ld, (x,y), word, font, color, palette["shadow"])
        layer = fade_alpha(layer, min(progress*2,1.0))
        img.alpha_composite(layer)
    return img

def s_pin_drop(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    heading = str(content.get("heading","LOCATION")).upper()
    body = str(content.get("body",""))
    bounce_t = min(t/0.5,1.0); drop = ease_out_back(bounce_t, overshoot=2.2)
    cy = int(-100 + (H//2-60 - (-100))*drop); cx = W//2; r = 40
    layer = Image.new("RGBA",(W,H),(0,0,0,0)); ld = ImageDraw.Draw(layer)
    ld.polygon([(cx,cy+80),(cx-r,cy),(cx-r,cy-r),(cx,cy-r-30),(cx+r,cy-r),(cx+r,cy)], fill=palette["orange"])
    ld.ellipse([cx-r,cy-r*2-10,cx+r,cy-10], fill=palette["orange"])
    ld.ellipse([cx-14,cy-r*2+18,cx+14,cy-r*2+46], fill=palette["navy_deep"])
    img.alpha_composite(layer)
    if bounce_t>=1.0 and t>0.55:
        panel_w, panel_h = 560, 150
        panel, pd = navy_panel(panel_w, panel_h, palette, radius=16, accent_left=False)
        f1=ImageFont.truetype(fonts["bold"],32); f2=ImageFont.truetype(fonts["reg"],22)
        pd.text((30,28),heading[:26],font=f1,fill=palette["white"])
        pd.text((30,76),body[:42],font=f2,fill=palette["offwhite"])
        fade = min((t-0.55)/0.2,1.0)
        panel = fade_alpha(panel, max(0,fade))
        img.alpha_composite(panel, (cx-panel_w//2, cy+100))
    return img

def s_count_up(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    pct = extract_percent(content.get("stat","")) or 50.0
    label_text = str(content.get("label",""))
    progress = ease_out_cubic(min(t/0.55,1.0)); value = int(pct*progress)
    num_text = str(value)+"%"
    measure = ImageDraw.Draw(Image.new("RGBA",(10,10)))
    num_font = ImageFont.truetype(fonts["title"], 190)
    sub_font, sub_lines, sub_line_h = autofit_font(measure, label_text, fonts["reg"], 480, 100, start_size=32)
    num_bbox = measure.textbbox((0,0), num_text, font=num_font)
    num_w, num_h = num_bbox[2]-num_bbox[0], num_bbox[3]-num_bbox[1]
    PAD = 70
    box_w = int(max(num_w, max((measure.textbbox((0,0),l,font=sub_font)[2] for l in sub_lines), default=0)) + PAD*2)
    box_h = int(num_h + (sub_line_h*len(sub_lines)) + PAD*2 + 40)
    panel, pd = navy_panel(box_w, box_h, palette, radius=24, accent_left=False)
    pd.rounded_rectangle([0,0,box_w-1,box_h-1], radius=24, outline=palette["orange"], width=3)
    text_with_shadow(pd, ((box_w-num_w)//2-num_bbox[0], PAD-num_bbox[1]), num_text, num_font, palette["white"], palette["shadow"])
    sy = PAD+num_h+30
    for line in sub_lines:
        lw = pd.textbbox((0,0),line,font=sub_font)[2]
        pd.text(((box_w-lw)//2, sy), line, font=sub_font, fill=palette["offwhite"]); sy += sub_line_h
    scale = max(0.01, ease_out_back(min(t/0.45,1.0)))
    scaled = panel.resize((max(1,int(box_w*scale)), max(1,int(box_h*scale))))
    img.alpha_composite(scaled, ((W-scaled.width)//2,(H-scaled.height)//2))
    return img

def s_circular_badge(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    pct = extract_percent(content.get("stat","")) 
    display = content.get("stat","") if pct is None else str(int(pct))+"%"
    label_text = str(content.get("label",""))
    scale_t = min(t/0.4,1.0); scale = ease_out_back(scale_t); radius=int(220*max(scale,0.01))
    cx,cy = W//2, H//2
    layer = Image.new("RGBA",(W,H),(0,0,0,0)); ld = ImageDraw.Draw(layer)
    ld.ellipse([cx-radius,cy-radius,cx+radius,cy+radius], fill=palette["navy_panel"])
    ld.ellipse([cx-radius,cy-radius,cx+radius,cy+radius], outline=palette["orange"], width=6)
    img.alpha_composite(layer)
    draw = ImageDraw.Draw(img)
    if scale_t>0.6:
        font = ImageFont.truetype(fonts["title"],80); 
        bb = draw.textbbox((0,0),display,font=font)
        text_with_shadow(draw,(cx-(bb[2]-bb[0])//2,cy-70),display,font,palette["white"],palette["shadow"])
        f2=ImageFont.truetype(fonts["reg"],26)
        bb2=draw.textbbox((0,0),label_text[:24],font=f2)
        draw.text((cx-bb2[2]//2,cy+50),label_text[:24].upper(),font=f2,fill=palette["orange"])
    return img

def s_progress_ring(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    pct = extract_percent(content.get("stat","")) or 50.0
    label_text = str(content.get("label",""))
    d = 560
    panel = Image.new("RGBA",(d,d),(0,0,0,0)); pd = ImageDraw.Draw(panel)
    pd.ellipse([0,0,d-1,d-1], fill=palette["navy_panel"])
    cx,cy,r = d//2, d//2-30, 210
    target_pct=pct/100.0; progress = ease_out_cubic(min(t/0.7,1.0))*target_pct
    pd.arc([cx-r,cy-r,cx+r,cy+r], start=-90, end=270, fill=(70,80,100,255), width=24)
    pd.arc([cx-r,cy-r,cx+r,cy+r], start=-90, end=-90+360*progress, fill=palette["orange"], width=24)
    font = ImageFont.truetype(fonts["title"],90); pctxt=str(int(progress*100))+"%"
    bb = pd.textbbox((0,0),pctxt,font=font)
    text_with_shadow(pd,(cx-(bb[2]-bb[0])//2,cy-60),pctxt,font,palette["white"],palette["shadow"])
    f2=ImageFont.truetype(fonts["reg"],22)
    bb2=pd.textbbox((0,0),label_text[:30],font=f2); pd.text((cx-bb2[2]//2,cy+70),label_text[:30].upper(),font=f2,fill=palette["offwhite"])
    img.alpha_composite(panel, ((W-d)//2,(H-d)//2))
    return img

def s_split_comparison(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    ll = str(content.get("left_label","")); lv = str(content.get("left_value",""))
    rl = str(content.get("right_label","")); rv = str(content.get("right_value",""))
    panel_w, panel_h = min(W-160,1500), 480
    panel, pd = navy_panel(panel_w, panel_h, palette, radius=22, accent_left=False)
    slide = ease_out_cubic(min(t/0.4,1.0))
    half = panel_w//2
    f1=ImageFont.truetype(fonts["title"],56); f2=ImageFont.truetype(fonts["reg"],28)
    lx = int(-half*(1-slide)) + 70
    pd.text((lx, 100), lv, font=f1, fill=palette["white"])
    for i2, line in enumerate(str(ll).split("\n")[:2]):
        pd.text((lx, 190+i2*36), line, font=f2, fill=palette["offwhite"])
    rx = half + 70 - int(half*(1-slide))
    text_with_shadow(pd,(rx, 100), rv, f1, palette["orange"], palette["shadow"])
    for i2, line in enumerate(str(rl).split("\n")[:2]):
        pd.text((rx, 190+i2*36), line, font=f2, fill=palette["offwhite"])
    pd.line([(half,60),(half,panel_h-60)], fill=(90,100,120,255), width=2)
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_before_after(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    ll = str(content.get("left_label","BEFORE")); lv = str(content.get("left_value",""))
    rl = str(content.get("right_label","AFTER")); rv = str(content.get("right_value",""))
    panel_w, panel_h = min(W-160,1500), 420
    slide_progress = ease_in_out(min(t/0.5,1.0))
    panel = Image.new("RGBA",(panel_w,panel_h),(0,0,0,0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([0,0,panel_w-1,panel_h-1], radius=22, fill=(225,228,234,255))
    slider_x = int(panel_w*slide_progress)
    mask = Image.new("L",(panel_w,panel_h),0)
    ImageDraw.Draw(mask).rectangle([0,0,slider_x,panel_h], fill=255)
    navy_side = Image.new("RGBA",(panel_w,panel_h),(0,0,0,0))
    ImageDraw.Draw(navy_side).rounded_rectangle([0,0,panel_w-1,panel_h-1], radius=22, fill=palette["navy_panel"])
    clipped = Image.new("RGBA",(panel_w,panel_h),(0,0,0,0)); clipped.paste(navy_side,(0,0),mask)
    panel.alpha_composite(clipped)
    pd.line([(slider_x,0),(slider_x,panel_h)], fill=palette["orange"], width=6)
    if slide_progress>0.85:
        f1=ImageFont.truetype(fonts["bold"],40); f2=ImageFont.truetype(fonts["reg"],28)
        pd.text((60,50),ll.upper(),font=f1,fill=palette["navy_deep"])
        pd.text((60,110),lv,font=f2,fill=(80,80,90,255))
        text_with_shadow(pd,(panel_w-360,50),rl.upper(),f1,palette["white"],palette["shadow"])
        pd.text((panel_w-360,110),rv,font=f2,fill=palette["offwhite"])
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_bar_chart_grow(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    title = str(content.get("title","")).upper()
    categories = content.get("categories", []) or ["A","B"]
    values = content.get("values", []) or [1,2]
    try: values = [float(v) for v in values]
    except: values = [1.0]*len(categories)
    max_v = max(values) if values else 1
    panel_w, panel_h = min(W-160,1300), 680
    panel, pd = navy_panel(panel_w, panel_h, palette)
    PAD_L,PAD_T,PAD_B = 90,120,100
    chart_w, chart_h = panel_w-PAD_L-70, panel_h-PAD_T-PAD_B
    ox, oy = PAD_L, PAD_T+chart_h
    tf = ImageFont.truetype(fonts["bold"],38); text_with_shadow(pd,(PAD_L,40),title[:40],tf,palette["white"],palette["shadow"])
    pd.line([(ox,oy),(ox+chart_w,oy)],fill=(120,130,150,255),width=2)
    n = max(1,len(values)); bar_w = chart_w//(n*2); progress = ease_out_cubic(min(t/0.7,1.0))
    fl=ImageFont.truetype(fonts["reg"],26); fv=ImageFont.truetype(fonts["bold"],30)
    for idx,(cat,val) in enumerate(zip(categories,values)):
        bh=int((val/max_v)*chart_h*progress); x=ox+idx*2*bar_w+bar_w//2
        pd.rectangle([x,oy-bh,x+bar_w,oy], fill=palette["orange"] if idx==len(values)-1 else (90,120,170,255))
        pd.text((x,oy+18),str(cat)[:10],font=fl,fill=palette["offwhite"])
        if bh>40: pd.text((x,oy-bh-42),str(int(val)),font=fv,fill=palette["white"])
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_line_chart_draw(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    title = str(content.get("title","")).upper()
    x_labels = content.get("x_labels", []) or ["A","B"]
    values = content.get("values", []) or [1,2]
    try: values = [float(v) for v in values]
    except: values = [1.0]*len(x_labels)
    max_v = max(values) if values else 1
    panel_w, panel_h = min(W-160,1350), 680
    panel, pd = navy_panel(panel_w, panel_h, palette)
    PAD_L,PAD_T,PAD_B = 80,110,90
    chart_w, chart_h = panel_w-PAD_L-60, panel_h-PAD_T-PAD_B
    ox, oy = PAD_L, PAD_T+chart_h
    tf=ImageFont.truetype(fonts["bold"],38); text_with_shadow(pd,(PAD_L,40),title[:40],tf,palette["white"],palette["shadow"])
    pd.line([(ox,oy),(ox+chart_w,oy)],fill=(120,130,150,255),width=2)
    progress = ease_out_cubic(min(t/0.75,1.0)); n_pts=max(2,len(values))
    exact = progress*(n_pts-1); full=int(exact); partial=exact-full
    pts=[]
    for idx in range(min(full+1,n_pts)):
        px=ox+int(idx/(n_pts-1)*chart_w); py=oy-int(values[idx]/max_v*chart_h); pts.append((px,py))
    if partial>0 and full+1<n_pts:
        x0=ox+int(full/(n_pts-1)*chart_w); y0=oy-int(values[full]/max_v*chart_h)
        x1=ox+int((full+1)/(n_pts-1)*chart_w); y1=oy-int(values[full+1]/max_v*chart_h)
        pts.append((int(x0+(x1-x0)*partial),int(y0+(y1-y0)*partial)))
    if len(pts)>1: pd.line(pts, fill=palette["orange"], width=6, joint="curve")
    for px,py in pts: pd.ellipse([px-7,py-7,px+7,py+7], fill=palette["white"])
    fl=ImageFont.truetype(fonts["reg"],22)
    for idx,lt in enumerate(x_labels):
        px=ox+int(idx/(n_pts-1)*chart_w); lw=pd.textbbox((0,0),str(lt),font=fl)[2]
        pd.text((px-lw//2,oy+18),str(lt),font=fl,fill=palette["offwhite"])
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_timeline_progression(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    title = str(content.get("title","")).upper()
    years = content.get("x_labels", []) or []
    values = content.get("values", []) or []
    n_pts = max(2, len(years))
    panel_w, panel_h = min(W-160,1400), 360
    panel, pd = navy_panel(panel_w, panel_h, palette, accent_left=False)
    tf=ImageFont.truetype(fonts["bold"],32); text_with_shadow(pd,(60,30),title[:40],tf,palette["white"],palette["shadow"])
    line_y = panel_h//2 + 30; PAD = 90; line_w = panel_w - PAD*2
    progress = ease_out_cubic(min(t/0.8,1.0)); line_x2 = PAD + int(line_w*progress)
    pd.line([(PAD,line_y),(PAD+line_w,line_y)], fill=(80,90,110,255), width=4)
    pd.line([(PAD,line_y),(line_x2,line_y)], fill=palette["orange"], width=4)
    f_year = ImageFont.truetype(fonts["bold"],22)
    for idx, yr in enumerate(years):
        px = PAD + int(idx/(n_pts-1)*line_w)
        if px <= line_x2:
            rad = 9 if idx < len(years)-1 else 13
            pd.ellipse([px-rad,line_y-rad,px+rad,line_y+rad], fill=palette["white"] if idx<len(years)-1 else palette["orange"])
            yw = pd.textbbox((0,0),str(yr),font=f_year)[2]
            pd.text((px-yw//2, line_y-56), str(yr), font=f_year, fill=palette["white"])
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_list_reveal(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    heading = str(content.get("heading","")).upper()
    items = content.get("items", []) or []
    panel_w, panel_h = min(W-160,1200), min(650, 200+len(items)*100)
    panel, pd = navy_panel(panel_w, panel_h, palette)
    hf = ImageFont.truetype(fonts["bold"],42); itf = ImageFont.truetype(fonts["reg"],32)
    text_with_shadow(pd,(60,50),heading[:40],hf,palette["orange"],palette["shadow"])
    for idx,item in enumerate(items[:6]):
        item_start = 0.2+idx*0.15
        progress = min(max((t-item_start)/0.2,0),1.0)
        if progress<=0: continue
        yy = 150+idx*90
        layer = Image.new("RGBA",(panel_w,panel_h),(0,0,0,0)); ld=ImageDraw.Draw(layer)
        ld.ellipse([60,yy+10,76,yy+26], fill=palette["orange"])
        ld.text((95,yy),str(item)[:60],font=itf,fill=palette["white"])
        rev = reveal_bottom_to_top(layer, progress, box=(60,yy-10,panel_w-60,yy+50))
        panel.alpha_composite(rev)
    img.alpha_composite(panel, ((W-panel_w)//2,(H-panel_h)//2))
    return img

def s_ticker_scroll(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    items = content.get("items", []) or [str(content.get("heading",""))]
    ticker = "    ".join(str(i).upper() for i in items) + "          "
    bar_h=100; y=H-bar_h
    bar = Image.new("RGBA",(W,bar_h),palette["navy_panel"]); bd=ImageDraw.Draw(bar)
    tag_w=220; bd.rectangle([0,0,tag_w,bar_h],fill=palette["orange"])
    ft=ImageFont.truetype(fonts["bold"],26); bd.text((25,bar_h//2-14),"KEY FACTS",font=ft,fill=palette["navy_deep"])
    img.alpha_composite(bar,(0,y))
    fk=ImageFont.truetype(fonts["bold"],28)
    measure = ImageDraw.Draw(Image.new("RGBA",(10,10)))
    text_w = max(1,measure.textbbox((0,0),ticker,font=fk)[2])
    speed=380; offset=int(t*speed); x=tag_w+40-(offset%text_w)
    layer = Image.new("RGBA",(W,bar_h),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    ld.text((x,bar_h//2-16),ticker,font=fk,fill=palette["white"])
    ld.text((x+text_w,bar_h//2-16),ticker,font=fk,fill=palette["white"])
    mask=Image.new("L",(W,bar_h),0); ImageDraw.Draw(mask).rectangle([tag_w+20,0,W,bar_h],fill=255)
    clipped = Image.new("RGBA",(W,bar_h),(0,0,0,0)); clipped.paste(layer,(0,0),mask)
    img.alpha_composite(clipped,(0,y))
    return img

def s_quote_card(t, content, W, H, fonts, palette):
    img = new_canvas(W, H)
    quote = "\u201c" + str(content.get("quote","")) + "\u201d"
    attribution = str(content.get("attribution",""))
    glass = Image.new("RGBA",(W,H),palette["navy_panel"])
    img.alpha_composite(fade_alpha(glass.copy(), min(t/0.3,1.0)))
    draw = ImageDraw.Draw(img)
    font, lines, line_h = autofit_font(draw, quote, fonts["serif"], W*0.6, 350, start_size=56)
    total_h = line_h*len(lines); y0=(H-total_h)//2-40
    layer = Image.new("RGBA",(W,H),(0,0,0,0)); ld = ImageDraw.Draw(layer)
    y=y0
    for line in lines:
        lw = ld.textbbox((0,0),line,font=font)[2]
        text_with_shadow(ld,((W-lw)//2,y),line,font,palette["white"],palette["shadow"],off=(2,2)); y+=line_h
    rev = reveal_bottom_to_top(layer, min(t/0.5,1.0), box=(0,y0-20,W,y0+total_h+20))
    img.alpha_composite(rev)
    if t>0.6 and attribution:
        f2=ImageFont.truetype(fonts["reg"],28)
        attr = "\u2014 " + attribution
        bb2=draw.textbbox((0,0),attr,font=f2)
        draw.text(((W-bb2[2])//2,y0+total_h+30),attr,font=f2,fill=palette["orange"])
    return img

def s_title_reveal_stat(t, content, W, H, fonts, palette):
    """Fallback for non-numeric stat_callout content (e.g. 'Increased')."""
    img = new_canvas(W, H)
    stat = str(content.get("stat","")).upper()
    label_text = str(content.get("label",""))
    draw = ImageDraw.Draw(img)
    font, lines, _ = autofit_font(draw, stat, fonts["title"], W*0.6, 200, start_size=100, wrap=False)
    bbox = draw.textbbox((0,0), lines[0], font=font); tw = bbox[2]-bbox[0]
    x, y = (W-tw)//2, H//2-100
    layer = Image.new("RGBA",(W,H),(0,0,0,0)); ld = ImageDraw.Draw(layer)
    text_with_shadow(ld, (x,y), lines[0], font, palette["white"], palette["shadow"])
    rev = reveal_bottom_to_top(layer, min(t/0.35,1.0), box=(x,y-20,x+tw+20,y+140))
    img.alpha_composite(rev)
    lp = ease_out_cubic(min(max((t-0.3)/0.3,0),1.0))
    ImageDraw.Draw(img).rectangle([x,y+130,x+int(tw*lp),y+143], fill=palette["orange"])
    if t>0.5:
        f2 = ImageFont.truetype(fonts["reg"], 32)
        bb2 = draw.textbbox((0,0), label_text, font=f2)
        draw.text(((W-bb2[2])//2, y+170), label_text, font=f2, fill=palette["offwhite"])
    return img


# ============== TYPE -> STYLE REGISTRY ==============

TEXT_BOX_STYLES = [s_lower_third, s_typewriter, s_corner_chip, s_breaking_banner,
                    s_highlight_sweep, s_diagonal_wipe, s_word_cascade, s_pin_drop]
COMPARISON_STYLES = [s_split_comparison, s_before_after]
BAR_CHART_STYLES = [s_bar_chart_grow]
LINE_CHART_STYLES = [s_line_chart_draw, s_timeline_progression]
LIST_REVEAL_STYLES = [s_list_reveal, s_ticker_scroll]
QUOTE_CARD_STYLES = [s_quote_card]
STAT_NUMERIC_STYLES = [s_count_up, s_circular_badge, s_progress_ring]
STAT_FALLBACK_STYLES = [s_title_reveal_stat]

def select_style_fn(graphic):
    g_type = graphic["type"]
    content = graphic.get("content", {})
    seed = graphic.get("trigger_phrase", "") + str(graphic.get("paragraph_index", 0))

    if g_type == "text_box":
        return pick_variant(TEXT_BOX_STYLES, seed)
    if g_type == "comparison":
        return pick_variant(COMPARISON_STYLES, seed)
    if g_type == "bar_chart":
        return pick_variant(BAR_CHART_STYLES, seed)
    if g_type == "line_chart":
        return pick_variant(LINE_CHART_STYLES, seed)
    if g_type == "list_reveal":
        return pick_variant(LIST_REVEAL_STYLES, seed)
    if g_type == "quote_card":
        return pick_variant(QUOTE_CARD_STYLES, seed)
    if g_type == "stat_callout":
        if extract_percent(content.get("stat", "")) is not None:
            return pick_variant(STAT_NUMERIC_STYLES, seed)
        return pick_variant(STAT_FALLBACK_STYLES, seed)
    return pick_variant(TEXT_BOX_STYLES, seed)
