from pylab import *
import pygame as pg
import mycmap

points = loadtxt("drawing.txt").reshape(-1, 2)
y = array([complex(p[0], p[1]) for p in points])
Fs = num_circle = N = len(y)  # Fs, num of circles and N actually refer to the same thing
Y = zeros(N, dtype=complex)  # The result of DFT
for k in range(Fs):
    for n in range(N):
        Y[k] += y[n] * exp(-1j * 2 * pi * k / N * n) / N  # DFT result divided by N
aY = angle(Y)  # The phase of the circle at each frequency
mY = abs(Y)  # The radius (magnitude) of the circle at each frequency
aYs = arange(Fs) / N * 2 * pi  # The angular velocity(not rad/seconds, but rad/frame) of the circle at each frequency
aYt = [aY + aYs * t for t in range(N)]  # The angle of the circle at each frequency over time step(frame)
HW = 500  # The height and weight of drawing panel
pg.init()
pg.display.set_caption('timmmGZ-Fourier Series Drawing')
screen = pg.display.set_mode((HW, HW + 50))
screen.fill("white")


def create_circle_surfaces(z):
    global cirfaces, zoom
    zoom = z
    cirfaces = [pg.Surface((mY[f] * 2 * zoom, mY[f] * 2 * zoom), pg.SRCALPHA) for f in range(Fs)]  # Circle surfaces
    [sf.set_colorkey("white") for sf in cirfaces]


def create_and_blit_button(text, x, y, w, h):
    text_surf = pg.font.Font(None, 25).render(text, True, 'black')
    pg.draw.rect(screen, "gray", (x, y, w, h))
    screen.blit(text_surf, text_surf.get_rect(center=(x + w // 2, y + h // 2)))
    return pg.Rect(x, y, w, h)


create_circle_surfaces(3)
drawing = pg.surface.Surface((HW, HW), pg.SRCALPHA)  # The drawing surface under circle surfaces
button_names = ["FPS +", "FPS -", "prism", "blink", "cyclic", "Fs+", "Fs-","follow"]
buttons = [create_and_blit_button(button_names[i], 5 + i * 62, HW, 56, 45) for i in range(8)]
path = []  # Color effect: transparency(path[x])=a*x+b
path_a = 255 / (15 - 80)  # 80 means 65 nodes before the last 15 nodes will be fading
path_b = path_a * (15 - Fs)  # 15 means the last 15 nodes will be invisible
colors, speed_of_color, soc_a, soc_b = mycmap.get_cmap()  # soc_a/b is also color effect, check it in mycmap.py
clock = pg.time.Clock()
FPS, FPS_limit = 25, 0
mY_filter = 0  # For decreasing the number of circles(filter out certain frequencies of signal y)
offX, offY = HW // 2, HW // 2
follow_drawing = False


def draw_frame(t):
    global FPS, FPS_limit, period, offX, offY  # FPS_limit is used to check the performance limit of the CPU
    period = clock.tick(FPS)
    drawing.fill((255, 255, 255))
    screen.blit(drawing, (0, 0))
    for i in range(len(path)):
        pg.draw.circle(drawing, (128, 128, 128, max(0, min(path_a * (len(path) - i) + path_b, 255))),
                       (path[i][0] * zoom + offX, HW - path[i][1] * zoom - offY), 3, 2)
    c_sum = 0 + 0j  # The sum of circle at time step t, path[t]
    screen.blit(drawing, (0, 0))
    for f in range(Fs):
        if mY[f] > mY_filter:
            cirfaces[f].fill("white")
            r = mY[f] * zoom  # Radius of the circle
            c = r * exp(1j * aYt[t][f])  # c for the current circle
            color = colors[(f + t * speed_of_color) % 256] + [128]
            pg.draw.line(cirfaces[f], color, (r, r), (r + c.real, r - c.imag), 2)
            pg.draw.circle(cirfaces[f], color, (r, r), r, 2)
            drawing.blit(cirfaces[f], (offX + c_sum.real - r, HW - (offY + c_sum.imag) - r))  # 250 is offset
            c_sum += c
    screen.blit(drawing, (0, 0))
    screen.blit(pg.font.Font(None, 20).render("FPS: %.2f" % (1000 / period), True, 'black'), (3, 3))
    screen.blit(pg.font.Font(None, 20).render("Number of circles: " + str(num_circle), True, 'black'), (3, 20))
    path.append(array([c_sum.real, c_sum.imag]) / zoom)
    if len(path) > N: del path[0]  # For looping the drawing
    pg.display.flip()
    if follow_drawing:
        offX, offY = (offX*5+HW - c_sum.real - 250)//6, (offY*5+HW - c_sum.imag - 250)//6

draging = False
while True:
    for t in range(len(y)):
        draw_frame(t)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if buttons[0].collidepoint(event.pos):
                        FPS_limit = 1000 / period if 1000 / period > FPS_limit else FPS_limit
                        FPS = FPS + 1 if FPS + 1 - 1000 / period < 2.5 or FPS < FPS_limit else FPS_limit
                        speed_of_color = max(1, int(soc_a * FPS + soc_b))
                    elif buttons[1].collidepoint(event.pos):
                        FPS = max(FPS - 1, 1)
                        speed_of_color = max(1, int(soc_a * FPS + soc_b))
                    elif buttons[2].collidepoint(event.pos):
                        colors, speed_of_color, soc_a, soc_b = mycmap.get_cmap("prism")
                    elif buttons[3].collidepoint(event.pos):
                        colors, speed_of_color, soc_a, soc_b = mycmap.get_cmap("blink", FPS)
                        speed_of_color = max(1, int(soc_a * FPS + soc_b))
                    elif buttons[4].collidepoint(event.pos):
                        colors, speed_of_color, soc_a, soc_b = mycmap.get_cmap("cyclic", FPS)
                        speed_of_color = max(1, int(soc_a * FPS + soc_b))
                    elif buttons[5].collidepoint(event.pos):
                        mY_filter = max(0, mY_filter - 0.1)
                        num_circle = len([m for m in mY if m > mY_filter])
                    elif buttons[6].collidepoint(event.pos):
                        mY_filter += 0.1
                        num_circle = len([m for m in mY if m > mY_filter])
                    elif buttons[7].collidepoint(event.pos):
                        follow_drawing=True if not follow_drawing else False
                    elif pg.Rect(0, 0, HW, HW).collidepoint(event.pos):
                        draging = True
                        global x_dragstart, y_dragstart
                        x_dragstart, y_dragstart = offX - event.pos[0], offY - (HW - event.pos[1])
                elif event.button == 4:
                    create_circle_surfaces(zoom + 0.25)
                elif event.button == 5:
                    create_circle_surfaces(zoom - 0.25)
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    draging = False
            elif event.type == pg.MOUSEMOTION:
                if draging:
                    offX, offY = event.pos[0] + x_dragstart, HW - event.pos[1] + y_dragstart
