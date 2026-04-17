#!/usr/bin/env python3
import curses
import random
import math
import time

class Particle:
    def __init__(self, x, y, vx, vy, char, color, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.char = char
        self.color = color
        self.life = life
        self.max_life = life

class Rocket:
    def __init__(self, x, y, target_y):
        self.x = x
        self.y = y
        self.vy = -1.2
        self.target_y = target_y
        self.trail = []

class Firework:
    def __init__(self, x, y, color, style):
        self.particles = []
        self.style = style
        count = random.randint(30, 60)

        if style == "circle":
            for i in range(count):
                angle = 2 * math.pi * i / count
                speed = random.uniform(0.5, 2.0)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed * 0.5
                char = random.choice(".*+o#@")
                life = random.randint(8, 18)
                self.particles.append(Particle(x, y, vx, vy, char, color, life))

        elif style == "ring":
            for i in range(count):
                angle = 2 * math.pi * i / count
                speed = random.uniform(1.4, 1.8)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed * 0.5
                life = random.randint(10, 15)
                self.particles.append(Particle(x, y, vx, vy, "o", color, life))

        elif style == "star":
            for i in range(count):
                angle = 2 * math.pi * i / count
                points = 5
                r = 1.8 if (i % (count // points)) < (count // points // 2) else 0.8
                speed = r * random.uniform(0.9, 1.1)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed * 0.5
                life = random.randint(10, 16)
                self.particles.append(Particle(x, y, vx, vy, "*", color, life))

        elif style == "willow":
            for i in range(count):
                angle = 2 * math.pi * i / count
                speed = random.uniform(0.3, 1.5)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed * 0.5 - 0.1
                life = random.randint(14, 25)
                self.particles.append(Particle(x, y, vx, vy, ".", color, life))

        elif style == "burst":
            for i in range(count * 2):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2, 2.5)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed * 0.5
                char = random.choice(".:*")
                life = random.randint(6, 14)
                self.particles.append(Particle(x, y, vx, vy, char, color, life))

    def update(self):
        gravity = 0.04
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += gravity
            if self.style == "willow":
                p.vy += 0.02
            p.vx *= 0.97
            p.life -= 1

        self.particles = [p for p in self.particles if p.life > 0]


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    curses.start_color()
    curses.use_default_colors()
    colors = [
        curses.COLOR_RED,
        curses.COLOR_GREEN,
        curses.COLOR_YELLOW,
        curses.COLOR_BLUE,
        curses.COLOR_MAGENTA,
        curses.COLOR_CYAN,
        curses.COLOR_WHITE,
    ]
    for i, c in enumerate(colors, 1):
        curses.init_pair(i, c, -1)

    fireworks = []
    rockets = []
    sparks = []
    max_h, max_w = stdscr.getmaxyx()
    frame = 0
    messages = [
        "~ FIREWORKS ~",
        "Press 'q' to quit",
        "Press SPACE to launch!",
    ]

    while True:
        max_h, max_w = stdscr.getmaxyx()
        key = stdscr.getch()
        if key == ord('q'):
            break

        if key == ord(' '):
            x = random.randint(max_w // 4, 3 * max_w // 4)
            target_y = random.randint(3, max_h // 3)
            rockets.append(Rocket(x, max_h - 2, target_y))

        if frame % 12 == 0 and random.random() < 0.6:
            x = random.randint(max_w // 4, 3 * max_w // 4)
            target_y = random.randint(3, max_h // 3)
            rockets.append(Rocket(x, max_h - 2, target_y))

        stdscr.erase()

        ground_char = "─"
        ground_y = max_h - 1
        for gx in range(max_w):
            try:
                stdscr.addch(ground_y, gx, ground_char, curses.color_pair(3) | curses.A_DIM)
            except curses.error:
                pass

        new_rockets = []
        for r in rockets:
            r.y += r.vy
            r.trail.append((int(r.x), int(r.y)))
            if len(r.trail) > 4:
                r.trail.pop(0)

            if r.y <= r.target_y:
                color = random.randint(1, len(colors))
                style = random.choice(["circle", "ring", "star", "willow", "burst"])
                fireworks.append(Firework(r.x, r.y, color, style))

                if random.random() < 0.3:
                    color2 = random.randint(1, len(colors))
                    style2 = random.choice(["circle", "ring", "burst"])
                    fireworks.append(Firework(r.x, r.y, color2, style2))
            else:
                new_rockets.append(r)
                for i, (tx, ty) in enumerate(r.trail):
                    brightness = curses.A_DIM if i < len(r.trail) // 2 else curses.A_NORMAL
                    char = "|" if i == len(r.trail) - 1 else "'"
                    if 0 <= ty < max_h and 0 <= tx < max_w:
                        try:
                            stdscr.addch(int(ty), int(tx), char, curses.color_pair(7) | brightness)
                        except curses.error:
                            pass
        rockets = new_rockets

        for fw in fireworks:
            fw.update()
            for p in fw.particles:
                ix, iy = int(p.x), int(p.y)
                if 0 <= iy < max_h and 0 <= ix < max_w:
                    fade = p.life / p.max_life
                    if fade > 0.6:
                        attr = curses.A_BOLD
                    elif fade > 0.3:
                        attr = curses.A_NORMAL
                    else:
                        attr = curses.A_DIM
                    try:
                        stdscr.addch(iy, ix, p.char, curses.color_pair(p.color) | attr)
                    except curses.error:
                        pass

        fireworks = [fw for fw in fireworks if fw.particles]

        if frame < 60:
            for i, msg in enumerate(messages):
                mx = max_w // 2 - len(msg) // 2
                my = max_h // 2 - 1 + i
                if 0 <= my < max_h and 0 <= mx < max_w:
                    fade = max(0, 1.0 - frame / 60)
                    attr = curses.A_BOLD if fade > 0.5 else curses.A_NORMAL if fade > 0.2 else curses.A_DIM
                    try:
                        stdscr.addstr(my, mx, msg, curses.color_pair(7) | attr)
                    except curses.error:
                        pass

        stdscr.refresh()
        frame += 1
        time.sleep(0.03)


if __name__ == "__main__":
    curses.wrapper(main)
