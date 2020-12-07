from matplotlib import cm
from numpy import *


def get_cmap(type="prism",FPS=1):
    if type == "prism":
        return [list((255 * array(cm.get_cmap("prism")(i)[:3])).astype(int)) for i in range(256)], 1,0,1
    radius = random.uniform(0.4, 0.5)
    rad = linspace(0, 2 * pi, 256)
    x = radius * cos(rad)
    y = radius * sin(rad)
    z = cos(rad) if type == "cyclic" else cos(rad * 128)
    Z = array([x, y, z])
    q, r = linalg.qr(random.rand(3, 3))
    center = random.uniform(radius, 1 - radius, size=(3, 1))
    Z = q.dot(Z) + center  # q is orthogonal matrix for rotation
    Z -= Z.min()
    (speed_of_color,soc_a,soc_b)=(5,-0.1, 7.5) if type == "blink" else (10,-0.3,17.5)#speed=a*FPS+b
    cmap = true_divide(Z, [Z.max()], out=None).T
    return [[int(c * 255) for c in cmap[i]] for i in range(256)], int(speed_of_color/(FPS/25)),soc_a, soc_b
