import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_matrix_portrait():
    # Load the perfectly framed headshot mask
    mask = Image.open('face_only_mask.png').convert('L')
    
    out_w, out_h = 360, 360
    font_size = 8
    char_w = 4.5
    char_h = 7.5
    
    cols = int(out_w / char_w)  # 80 cols
    rows = int(out_h / char_h)  # 48 rows
    
    # Resize mask to grid
    grid_mask = mask.resize((cols, rows), Image.Resampling.LANCZOS)
    
    lum_grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            val = grid_mask.getpixel((x, y)) / 255.0
            row.append(val)
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
        col_trails.append(random.randint(12, 20))
        # Continuous binary sequence
        col_streams.append([random.choice(['0', '1']) for _ in range(rows + num_frames * 3)])
        
    frames = []
    
    for f in range(num_frames):
        img = Image.new('RGB', (out_w, out_h), (0, 0, 0)) # Pure black background
        draw = ImageDraw.Draw(img)
        
        for y in range(rows):
            for x in range(cols):
                speed = col_speeds[x]
                # Character index shifting down (falling rain motion)
                char_idx = (y - f * speed) % len(col_streams[x])
                char = col_streams[x][char_idx]
                
                # Falling light beam wave
                head_y = (f * speed * 2 + col_offsets[x]) % rows
                dist = (head_y - y) % rows
                trail = col_trails[x]
                
                if dist < trail:
                    pulse = (1.0 - dist / trail) ** 1.3
                else:
                    pulse = 0.0
                    
                face_weight = lum_grid[y][x]
                
                if face_weight > 0.02:
                    # ON THE FACE / PERSON:
                    # Purely constructed out of falling white and gray binary numbers!
                    # Strong baseline visibility (0.70) + falling light surge (0.30 * pulse)
                    illum = face_weight * (0.70 + 0.30 * pulse)
                    val = int(min(255, max(18, illum * 255)))
                    color = (val, val, val) # Strictly Black & White / Monochrome
                else:
                    # IN THE BACKGROUND:
                    # Stealth falling matrix raindrops in the black space
                    if pulse > 0.6:
                        val = int(32 * pulse)
                        color = (val, val, val)
                    else:
                        color = (0, 0, 0)
                        
                if color[0] > 6:
                    px = int(x * char_w)
                    py = int(y * char_h)
                    draw.text((px, py), char, font=font, fill=color)
                    
        frames.append(img)
        
    output_gif = 'binary_matrix_portrait.gif'
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=70,  # ~14 fps smooth animation
        loop=0,       # Infinite loop
        optimize=True
    )
    print(f"Generated {output_gif} successfully! Size: {os.path.getsize(output_gif)/1024:.1f} KB")

if __name__ == '__main__':
    generate_matrix_portrait()
