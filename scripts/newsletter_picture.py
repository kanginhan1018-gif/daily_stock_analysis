"""Render explanatory pictograms and bilingual text as one Telegram image."""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/System/Library/Fonts/AppleSDGothicNeo.ttc',
]


def render_picture(stories, items, output, date):
    font_path = next((p for p in [os.environ.get('NEWSLETTER_FONT', '')] + FONT_PATHS if p and Path(p).exists()), None)
    if not font_path:
        raise RuntimeError('A Korean font is required for the visual newsletter')
    image = Image.new('RGB', (1440, 2400), '#eef2f7')
    draw = ImageDraw.Draw(image)
    ink, muted, blue = '#14253c', '#53657b', '#2465dc'

    def text(value, x, y, size, width, max_lines, color=ink):
        font = ImageFont.truetype(font_path, size)
        lines, line = [], ''
        # Character wrapping also supports Korean and long technical names.
        for char in value:
            if draw.textlength(line + char, font=font) > width:
                if ' ' in line.rstrip():
                    head, tail = line.rstrip().rsplit(' ', 1)
                    lines.append(head.strip())
                    line = tail + char
                else:
                    lines.append(line.strip())
                    line = char
            else:
                line += char
        if line:
            lines.append(line.strip())
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1][:-1] + '…'
        for line in lines:
            draw.text((x, y), line, font=font, fill=color)
            y += int(size * 1.45)
        return y

    def pictogram(kind, x, y, color):
        # Simple symbols represent concepts, never measured performance.
        if kind == 'network':
            points = [(x+15,y+15),(x+85,y+15),(x+50,y+55),(x+15,y+95),(x+85,y+95)]
            for a, b in [(0,2),(1,2),(2,3),(2,4)]:
                draw.line([points[a],points[b]], fill=color, width=5)
            for px, py in points:
                draw.ellipse((px-10,py-10,px+10,py+10),fill=color)
        elif kind == 'document':
            draw.rounded_rectangle((x+16,y+3,x+88,y+103),radius=10,outline=color,width=5)
            for dy in [28,48,68]:
                draw.line((x+30,y+dy,x+73,y+dy),fill=color,width=5)
        elif kind == 'optimization':
            for px, py in [(x+15,y+25),(x+85,y+15),(x+65,y+90)]:
                draw.ellipse((px-8,py-8,px+8,py+8),fill=color)
            draw.line([(x+15,y+25),(x+85,y+15),(x+65,y+90)],fill=color,width=5)
        else:
            draw.rounded_rectangle((x+20,y+20,x+85,y+85),radius=10,outline=color,width=5)
            for offset in [30,50,70]:
                draw.line((x+offset,y+5,x+offset,y+20),fill=color,width=4)
                draw.line((x+offset,y+85,x+offset,y+100),fill=color,width=4)
                draw.line((x+5,y+offset,x+20,y+offset),fill=color,width=4)
                draw.line((x+85,y+offset,x+100,y+offset),fill=color,width=4)

    text('SOTA / VISUAL BRIEF', 70, 42, 54, 1300, 1)
    text('그림으로 이해하는 기술 동향', 70, 130, 32, 1300, 1, muted)
    text(date + '  •  EN + 한국어', 70, 187, 25, 1300, 1, muted)
    for number, story in enumerate(stories):
        item = items[story['index']]
        top = 265 + number * 670
        draw.rounded_rectangle((50,top,1390,top+644),radius=28,fill='white')
        text(f"0{number+1} / {item['source']}", 85, top+23, 24, 1250, 1, blue)
        text(item['title'], 85, top+68, 36, 1250, 2)
        y = top + 195
        for x, label, key, color in [(85,'BEFORE / 기존','before',muted),(795,'AFTER / 변화','after',blue)]:
            draw.rounded_rectangle((x,y,x+550,y+205),radius=18,fill='#f1f5fb')
            pictogram(story['icon'],x+20,y+72,color)
            text(label,x+20,y+10,22,510,1,color)
            text(story[key],x+145,y+70,27,380,3,color)
        draw.line((670,y+110,760,y+110),fill=blue,width=7)
        draw.polygon([(760,y+110),(738,y+94),(738,y+126)],fill=blue)
        text('EN  '+story['en'],85,top+424,27,1250,3)
        text('KR  '+story['ko'],85,top+548,26,1250,2)
    text('Concept diagrams • not benchmark charts / 개념도이며 성능 비교표가 아닙니다',70,2290,22,1300,1,muted)
    text('Research claims are preliminary. Source links are in the caption.',70,2332,22,1300,1,muted)
    image.save(output, optimize=True)
    return output
