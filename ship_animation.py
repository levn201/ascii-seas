#!/usr/bin/env python3
"""
ASCII Ozean & Segelschiff-Animation
===================================
Ein Segelschiff segelt über ein wogendes Meer, schaukelt im Wellengang
und reagiert dynamisch auf die Wellenhöhe.

Steuerung:
  [Q]         Beenden
  [Leertaste] Pause / Fortsetzen
  [+] / [W]   Wellengang verstärken (Sturm)
  [-] / [S]   Wellengang beruhigen
"""

import sys
import os
import time
import math
import random
import shutil

# Windows VT100 / UTF-8 Unterstützung aktivieren
if sys.platform == "win32":
    os.system("")
    import msvcrt
else:
    msvcrt = None

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ANSI Farbcodes (24-bit Truecolor & Standard-Fallback)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Himmelsfarben
MOON_COLOR = "\033[38;2;255;245;180m"
STAR_COLOR = "\033[38;2;240;240;180m"
STAR_DIM = "\033[38;2;130;135;160m"
CLOUD_COLOR = "\033[38;2;160;175;200m"
BIRD_COLOR = "\033[38;2;210;220;230m"

# Schiff-Farben
WOOD_COLOR = "\033[38;2;195;125;65m"
WOOD_DARK = "\033[38;2;135;75;30m"
SAIL_COLOR = "\033[38;2;250;245;230m"
MAST_COLOR = "\033[38;2;175;110;50m"
FLAG_COLOR = "\033[38;2;230;60;50m"

# Wasserfarben
FOAM_COLOR = "\033[38;2;255;255;255m"
WATER_SURF = "\033[38;2;70;190;240m"
WATER_MID = "\033[38;2;30;130;210m"
WATER_DEEP = "\033[38;2;15;70;150m"
WATER_ABYSS = "\033[38;2;8;35;90m"
HUD_COLOR = "\033[38;2;120;140;170m"

# 3 Schaukelstufen (Tilt):
#  -1 = Heck tief, Bug steigt Welle hoch (Neigung nach links/hinten)
#   0 = Ausgeglichen / waagerecht
#  +1 = Heck hoch, Bug taucht ins Wellental (Neigung nach rechts/vorne)
BOAT_FRAMES = {
    -1: [
        ("               \\~               ", "FFFFFFFFFFFFFFFMMF"),
        ("              / \\       \\~      ", "FFFFFFFFFFFFFMMFMFFFFFMMF"),
        ("             /__ \\     / \\      ", "FFFFFFFFFFFFMMMMMFFFFMMFM"),
        ("               \\      /__ \\     ", "FFFFFFFFFFFFFFFMMFFFFMMMMM"),
        ("             )-\\-()     \\       ", "FFFFFFFFFFFFFSSSSSSFFFMM"),
        ("            )__\\__()  )-\\-() __ ", "FFFFFFFFFFFSSSSSSSSSSFSSSSSSFFWW"),
        ("           )____\\___() )_\\__()\\\\", "FFFFFFFFFFSSSSSSSSSSSSSSSSSSSSSWW"),
        ("    __ _ ___ \\___\\___)_ \\___()\\\\", "FFFFWWWWWWWWWWMMMMMMMMMSMMMMSSSWW"),
        ("   \\===================o==o==o=\\", "FFFWHHHHHHHHHHHHHHHHHHHHHHHHHHWW"),
        ("    \\==========================/", "FFFFWHHHHHHHHHHHHHHHHHHHHHHHHHHW"),
    ],
    0: [
        ("              |~                ", "FFFFFFFFFFFFFFMMF"),
        ("             /|        |~       ", "FFFFFFFFFFFFFMMFFFFFFFFMMF"),
        ("            /_|___    /|        ", "FFFFFFFFFFFMMMMMMMFFFMMFF"),
        ("              |      /_|___     ", "FFFFFFFFFFFFFFMMFFFFMMMMMMM"),
        ("            ) | ()     |        ", "FFFFFFFFFFFFFSSSSSSFFFFMM"),
        ("           )__|__()  ) | ()  __ ", "FFFFFFFFFFSSSSSSSSSFSSSSSSFFWW"),
        ("          )___|___() )_|__() \\ \\", "FFFFFFFFFSSSSSSSSSSSSSSSSSSSWFWW"),
        ("     ______|____|___)__|___() \\ \\", "FFFFFWWWWWWWMMMMMMMMSSSSSSSSSSFWWW"),
        ("    \\==================o==o==o==/", "FFFFWHHHHHHHHHHHHHHHHHHHHHHHHHWW"),
        ("     \\=========================/ ", "FFFFFWHHHHHHHHHHHHHHHHHHHHHHHHHWF"),
    ],
    1: [
        ("             ~/                 ", "FFFFFFFFFFFFFMF"),
        ("             |/         ~/      ", "FFFFFFFFFFFFFMMFFFFFFFFFMF"),
        ("           __|_/        |/      ", "FFFFFFFFFFMMMMMMFFFFFFFMM"),
        ("             /        __|_/     ", "FFFFFFFFFFFFFMMFFFFFMMMMMM"),
        ("           ()-/-(       /       ", "FFFFFFFFFFFSSSSSSFFFFFFMM"),
        ("          ()__/__(    ()-/-(    ", "FFFFFFFFFSSSSSSSSSSFFSSSSSS"),
        ("        __()___|___() ()__/__(  ", "FFFFFFFFWWSSSSSSSSSSSFSSSSSSSS"),
        ("       /  /____/____/ ()___/__()", "FFFFFFWWFWWMMMMMMMMMMMSSSSSSSSSS"),
        ("      /==================o==o==o\\", "FFFFWWFHHHHHHHHHHHHHHHHHHHHHHHHW"),
        ("     /==========================/", "FFFFWHHHHHHHHHHHHHHHHHHHHHHHHHHW"),
    ]
}

def get_wave_height(x, t, wave_scale=1.0):
    """Berechnet die natürliche Wellenhöhe an Stelle x zur Zeit t."""
    w1 = 1.8 * math.sin(0.09 * x - 2.6 * t)
    w2 = 1.1 * math.sin(0.05 * x - 1.5 * t + 1.2)
    w3 = 0.5 * math.sin(0.20 * x - 3.4 * t)
    return (w1 + w2 + w3) * wave_scale

def read_key():
    """Liest einen nicht-blockierenden Tastendruck unter Windows aus."""
    if msvcrt and msvcrt.kbhit():
        ch = msvcrt.getch()
        try:
            return ch.decode("utf-8").lower()
        except Exception:
            return ""
    return None

def main():
    # Terminal säubern & Cursor ausblenden
    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    # Sternenfeld
    random.seed(42)
    stars = []
    for _ in range(50):
        sx = random.randint(0, 160)
        sy = random.randint(1, 9)
        char = random.choice([".", "*", "+", "°"])
        brightness = random.choice([STAR_COLOR, STAR_DIM])
        stars.append((sx, sy, char, brightness))

    # Wolken
    clouds = [
        {"x": 8.0, "y": 2, "shape": ["   .--.   ", " .-(    )-. ", "(___.__)__)"]},
        {"x": 58.0, "y": 3, "shape": ["     .---.   ", "   .-(     )-. ", "  (___.__)____)"]},
        {"x": 115.0, "y": 1, "shape": ["  .--. ", " (    )", "(__.__)"]},
    ]

    # Möwen
    seagulls = [
        {"x": 22.0, "y": 5.0, "speed": 1.1},
        {"x": 78.0, "y": 4.0, "speed": 1.4},
    ]

    t = 0.0
    ship_x = -32.0
    wave_scale = 1.0
    paused = False

    try:
        while True:
            t_frame_start = time.time()

            # Tastatureingaben abfragen
            key = read_key()
            if key == "q":
                break
            elif key == " ":
                paused = not paused
            elif key in ("+", "w"):
                wave_scale = min(2.2, wave_scale + 0.2)
            elif key in ("-", "s"):
                wave_scale = max(0.4, wave_scale - 0.2)

            cols, rows = shutil.get_terminal_size((80, 24))
            sea_base_y = max(13, rows - 9)

            # 2D Zeichenpuffer vorbereiten
            buffer = [[" " for _ in range(cols)] for _ in range(rows)]
            color_buf = [["" for _ in range(cols)] for _ in range(rows)]

            # 1. Himmel: Mondsichel
            moon_x = cols - 16
            moon_y = 2
            moon_art = [
                r"   .-.   ",
                r"  (   ). ",
                r"   `-'   "
            ]
            if moon_x > 0 and moon_x + 9 < cols and moon_y + 3 < sea_base_y:
                for dy, line in enumerate(moon_art):
                    for dx, ch in enumerate(line):
                        if ch != " ":
                            buffer[moon_y + dy][moon_x + dx] = ch
                            color_buf[moon_y + dy][moon_x + dx] = MOON_COLOR

            # 2. Himmel: Sterne mit Funkeln
            for sx, sy, ch, c in stars:
                target_x = sx % cols
                if sy < sea_base_y - 2 and buffer[sy][target_x] == " ":
                    twinkle = math.sin(t * 3.5 + sx)
                    color = c if twinkle > -0.2 else STAR_DIM
                    buffer[sy][target_x] = ch
                    color_buf[sy][target_x] = color

            # 3. Himmel: Wolkenzug
            for cloud in clouds:
                if not paused:
                    cloud["x"] = (cloud["x"] + 0.1) % (cols + 20)
                cx_int = int(cloud["x"]) - 10
                cy = cloud["y"]
                for dy, row_str in enumerate(cloud["shape"]):
                    draw_y = cy + dy
                    if 0 <= draw_y < sea_base_y - 1:
                        for dx, ch in enumerate(row_str):
                            draw_x = cx_int + dx
                            if 0 <= draw_x < cols and ch != " ":
                                buffer[draw_y][draw_x] = ch
                                color_buf[draw_y][draw_x] = CLOUD_COLOR

            # 4. Himmel: Möwenflug
            for bird in seagulls:
                if not paused:
                    bird["x"] = (bird["x"] + bird["speed"] * 0.35) % (cols + 15)
                bird_x = int(bird["x"]) - 5
                bird_y = int(bird["y"] + math.sin(t * 2.2 + bird["speed"]) * 0.7)
                wing = "v" if (int(t * 4) % 2 == 0) else "^"
                bird_str = f"\\{wing}/"
                if 0 <= bird_y < sea_base_y - 2:
                    for dx, ch in enumerate(bird_str):
                        bx = bird_x + dx
                        if 0 <= bx < cols:
                            buffer[bird_y][bx] = ch
                            color_buf[bird_y][bx] = BIRD_COLOR

            # 5. Ozean: Wellen & Tiefe zeichnen
            for x in range(cols):
                wh = get_wave_height(x, t, wave_scale)
                wave_surface_y = int(round(sea_base_y + wh))

                # Wellenoberfläche mit Schaumkronen
                if 0 <= wave_surface_y < rows:
                    wh_prev = get_wave_height(x - 1, t, wave_scale)
                    wh_next = get_wave_height(x + 1, t, wave_scale)
                    is_crest = wh < wh_prev and wh < wh_next

                    if is_crest:
                        crest_char = "^" if (x % 2 == 0) else "~"
                        buffer[wave_surface_y][x] = crest_char
                        color_buf[wave_surface_y][x] = FOAM_COLOR
                    else:
                        wave_char = "~" if ((x + int(t * 3)) % 3 != 0) else "≈"
                        buffer[wave_surface_y][x] = wave_char
                        color_buf[wave_surface_y][x] = WATER_SURF

                # Tiefe Wasserschichten mit Farbverlauf
                for y in range(wave_surface_y + 1, rows):
                    depth = y - wave_surface_y
                    if depth == 1:
                        char = "≈" if (x % 3 == 0) else "~"
                        color = WATER_MID
                    elif depth in (2, 3):
                        char = "≈" if ((x + y) % 2 == 0) else " "
                        color = WATER_DEEP
                    else:
                        char = "░" if ((x + y) % 4 == 0) else " "
                        color = WATER_ABYSS
                    
                    buffer[y][x] = char
                    color_buf[y][x] = color

            # 6. Schiff: Physik, Schaukeln & Auf/Ab-Bewegung
            if not paused:
                ship_x += 0.35
                if ship_x > cols + 5:
                    ship_x = -32.0

            # Höhe an Heck, Mitte und Bug abtasten
            ship_mid_x = ship_x + 16
            ship_stern_x = ship_x + 6
            ship_bow_x = ship_x + 26

            y_mid = get_wave_height(ship_mid_x, t, wave_scale)
            y_stern = get_wave_height(ship_stern_x, t, wave_scale)
            y_bow = get_wave_height(ship_bow_x, t, wave_scale)

            # Neigung aus Wellensteigung ermitteln
            slope = y_bow - y_stern
            if slope < -0.7 * wave_scale:
                tilt_state = -1  # Bug steigt Welle hoch
            elif slope > 0.7 * wave_scale:
                tilt_state = 1   # Bug neigt sich nach unten
            else:
                tilt_state = 0   # Ausgeglichen

            ship_draw_y = int(round(sea_base_y - 7 + y_mid * 0.75))

            # Schiff in den Vordergrund zeichnen
            boat_lines = BOAT_FRAMES[tilt_state]
            for b_row, (line_text, mask) in enumerate(boat_lines):
                target_y = ship_draw_y + b_row
                if 0 <= target_y < rows:
                    for b_col, ch in enumerate(line_text):
                        target_x = int(round(ship_x)) + b_col
                        if 0 <= target_x < cols and ch != " ":
                            buffer[target_y][target_x] = ch
                            m = mask[b_col] if b_col < len(mask) else " "
                            if m == "M":
                                color_buf[target_y][target_x] = MAST_COLOR
                            elif m == "F":
                                color_buf[target_y][target_x] = FLAG_COLOR
                            elif m == "S":
                                color_buf[target_y][target_x] = SAIL_COLOR
                            elif m == "W":
                                color_buf[target_y][target_x] = WOOD_COLOR
                            elif m == "H":
                                color_buf[target_y][target_x] = WOOD_DARK if ch == "o" else WOOD_COLOR
                            else:
                                color_buf[target_y][target_x] = WOOD_COLOR

            # Gischt am Schiffsbug
            splash_x = int(round(ship_bow_x)) + 1
            splash_y = int(round(sea_base_y + y_bow))
            if 0 <= splash_x < cols and 0 <= splash_y < rows:
                spray_char = random.choice(["*", "°", "~"])
                buffer[splash_y][splash_x] = spray_char
                color_buf[splash_y][splash_x] = FOAM_COLOR

            # 7. Statuszeile / HUD am unteren Bildschirmrand
            state_text = "PAUSE" if paused else "FAHRT"
            status = f" [Q] Beenden | [Leertaste] {state_text} | [+/-] Wellengang: {wave_scale:.1f}x "
            status = status.ljust(cols)[:cols]
            hud_y = rows - 1
            for i, ch in enumerate(status):
                buffer[hud_y][i] = ch
                color_buf[hud_y][i] = HUD_COLOR

            # 8. Frame flackerfrei als Gesamtblock rendern
            output = ["\033[H"]
            current_c = None

            for r in range(rows):
                line_parts = []
                for c in range(cols):
                    col = color_buf[r][c]
                    ch = buffer[r][c]
                    if col != current_c:
                        line_parts.append(col if col else RESET)
                        current_c = col
                    line_parts.append(ch)
                if r < rows - 1:
                    line_parts.append("\n")
                output.append("".join(line_parts))

            output.append(RESET)
            sys.stdout.write("".join(output))
            sys.stdout.flush()

            if not paused:
                t += 0.08

            # Zeit für saubere ~25 FPS berechnen
            elapsed = time.time() - t_frame_start
            sleep_time = max(0.01, 0.04 - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass
    finally:
        # Terminal wieder in Normalzustand versetzen
        sys.stdout.write("\033[?25h\033[0m\n\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
