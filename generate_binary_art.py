import os
from PIL import Image, ImageEnhance
import random

def generate_binary_svg(input_image_path, output_svg_path, rows=90):
    img = Image.open(input_image_path).convert('RGB')
    
    # Crop to square if not square
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    
    # Enhance contrast and sharpness
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)

    font_size = 7
    char_w = 4.2
    char_h = 7.0
    cols = int(rows * (char_h / char_w))  # ~ 150 cols
    
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    
    width_px = int(cols * char_w)
    height_px = int(rows * char_h)
    
    random.seed(2026)
    
    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="{width_px}" height="{height_px}">
<defs>
  <linearGradient id="cyberBorder" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#38bdf8"/>
    <stop offset="50%" stop-color="#818cf8"/>
    <stop offset="100%" stop-color="#3b82f6"/>
  </linearGradient>
  <clipPath id="cardClip">
    <rect width="{width_px}" height="{height_px}" rx="20"/>
  </clipPath>
</defs>
<style>
  .binary-text {{
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
    font-size: {font_size}px;
    font-weight: 700;
    user-select: all;
  }}
</style>
<g clip-path="url(#cardClip)">
  <rect width="100%" height="100%" fill="#0d1117"/>
''')

    def quantize_color(r, g, b):
        # Slightly boost vibrancy
        # Quantize to 12-level steps (each channel rounded to multiple of 16)
        qr = min(255, int(round(r / 18.0) * 18))
        qg = min(255, int(round(g / 18.0) * 18))
        qb = min(255, int(round(b / 18.0) * 18))
        return f"#{qr:02x}{qg:02x}{qb:02x}"

    for y in range(rows):
        y_pos = y * char_h + font_size * 0.85
        svg_parts.append(f'  <text x="0" y="{y_pos:.1f}" class="binary-text">')
        
        current_color = None
        current_text = []
        
        for x in range(cols):
            r, g, b = img_resized.getpixel((x, y))
            color = quantize_color(r, g, b)
            char = "1" if random.random() > 0.5 else "0"
            
            if color == current_color:
                current_text.append(char)
            else:
                if current_text:
                    svg_parts.append(f'<tspan fill="{current_color}">{"".join(current_text)}</tspan>')
                current_color = color
                current_text = [char]
                
        if current_text:
            svg_parts.append(f'<tspan fill="{current_color}">{"".join(current_text)}</tspan>')
            
        svg_parts.append('</text>\n')

    svg_parts.append(f'''</g>
<rect width="{width_px}" height="{height_px}" rx="20" fill="none" stroke="url(#cyberBorder)" stroke-width="4"/>
</svg>''')

    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write("".join(svg_parts))
    print(f"Generated {output_svg_path} successfully! Size: {os.path.getsize(output_svg_path)} bytes")

if __name__ == '__main__':
    generate_binary_svg('profile.png', 'binary_portrait.svg', rows=90)
