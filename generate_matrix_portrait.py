import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_full_cell_matrix_portrait():
    # 1. Load the edge-to-edge cropped portrait
    src = Image.open('crop_edge_to_edge.png').convert('RGB')
    
    out_w, out_h = 360, 400
    font_size = 8
    char_w = 4.8
    char_h = 8.0
    
    cols = int(out_w / char_w)  # 75 cols
    rows = int(out_h / char_h)  # 50 rows
    
    grid_img = src.resize((cols, rows), Image.Resampling.LANCZOS)
    
    # 2. Build precision luminance mask
    lum_grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            r, g, b = grid_img.getpixel((x, y))
            # Accurate detection of sky blue background
            if b > 170 and b > r + 28 and g > r + 15:
                row.append(0.0) # Background is 0
            else:
                lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                # Skin highlights
                if r > b + 18 and r > 65:
                    boosted = min(1.0, (lum ** 0.75) * 1.4)
                    row.append(boosted)
                elif lum > 0.65:
                    # White shirt
                    row.append(min(1.0, lum * 1.1))
                elif lum < 0.35:
                    # Dark hair, beard, tie
                    row.append(max(0.12, lum * 0.7))
                else:
                    row.append(lum)
        lum_grid.append(row)
        
    font = ImageFont.truetype('C:\\Windows\\Fonts\\consola.ttf', font_size)
    
    num_frames = 20
    random.seed(2026)
    
    col_speeds = []
    col_offsets = []
    col_trails = []
    col_streams = []
    
    for c in range(cols):
        col_speeds.append(random.choice([1, 2]))
        col_offsets.append(random.randint(0, rows))
        col_trails.append(random.randint(12, 22))
        col_streams.append([random.choice(['0', '1']) for _ in range(rows + num_frames * 3)])
        
    frames = []
    
    # GitHub dark theme background color (#0d1117)
    bg_color = (13, 17, 23)
    
    for f in range(num_frames):
        img = Image.new('RGB', (out_w, out_h), bg_color)
        draw = ImageDraw.Draw(img)
        
        for y in range(rows):
            for x in range(cols):
                speed = col_speeds[x]
                char_idx = (y - f * speed) % len(col_streams[x])
                char = col_streams[x][char_idx]
                
                head_y = (f * speed * 2 + col_offsets[x]) % rows
                dist = (head_y - y) % rows
                trail = col_trails[x]
                
                if dist < trail:
                    pulse = (1.0 - dist / trail) ** 1.3
                else:
                    pulse = 0.0
                    
                face_weight = lum_grid[y][x]
                
                if face_weight > 0.02:
                    # ON THE PERSON:
                    # Brightness surges as the light pulse falls
                    illum = face_weight * (0.65 + 0.35 * pulse)
                    val = int(min(255, max(20, illum * 255)))
                    color = (val, val, val) # Pure monochrome black & white
                else:
                    # IN THE BACKGROUND:
                    # Subtle stealth matrix rain matching GitHub's dark theme
                    if pulse > 0.65:
                        val = int(35 * pulse)
                        color = (val, val + 2, val + 5)
                    else:
                        color = bg_color
                        
                if color != bg_color:
                    px = int(x * char_w)
                    py = int(y * char_h)
                    draw.text((px, py), char, font=font, fill=color)
                    
        frames.append(img)
        
    output_gif = 'matrix_binary_portrait.gif'
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=70,
        loop=0,
        optimize=True
    )
    print(f"Generated {output_gif} successfully! Size: {os.path.getsize(output_gif)/1024:.1f} KB")

if __name__ == '__main__':
    generate_full_cell_matrix_portrait()
