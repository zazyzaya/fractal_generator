from graphics import *
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import scipy.misc as scp
import matplotlib.pyplot as plt
from PIL import Image

D_WIDTH = 600
D_HEIGHT = 600

G_WIDTH = 3
G_HEIGHT = 3

G_CTR_X = -0.5
G_CTR_Y = 0

CENTER_X = D_WIDTH // 2
CENTER_Y = D_HEIGHT // 2

ITERS=50
ITER_CLOCK=0
ZOOM_LEV = 2

ALG = None

loading = Image.open('loading.gif')
fig, ax = plt.subplots()

def mandel(x0, xn, y0, yn, iters=ITERS, width=D_WIDTH, height=D_HEIGHT):
    x = np.linspace(x0, xn, width)
    y = np.linspace(y0, yn, height)

    # Combine x and y into a grid of coordinates
    c = x[:, np.newaxis] + 1j*y[np.newaxis, :]
    iter_map = np.zeros((width, height))

    z = c
    n = 0
    for i in range(iters):
        z = z**2 + c
        iter_map[abs(z) <= 100] += 1

    iter_map[iter_map <= 2] = 0
    iter_map = iter_map / iters
    
    colors = np.full((height, width, 3), [255, 0, 200])
    colors = (colors.T * iter_map).T
    
    for i in range(iter_map.shape[0]):
        for j in range(iter_map.shape[1]):
            if iter_map[i,j] > iters/2:
                colors[i,j] = [0,0,255 * (iter_map[i,j]/iters)]

    return colors

def update_globals():
    global ZOOM_LEV, ITER_CLOCK, ITERS

    ZOOM_LEV += 0.1
    ITER_CLOCK += 1
    
    if ITER_CLOCK % 3 == 0:
        ITERS += 7

def compute_update():
    disp(loading)

    x0 = G_CTR_X - G_WIDTH/2 
    xn = G_CTR_X + G_WIDTH/2
    y0 = G_CTR_Y - G_HEIGHT/2 
    yn = G_CTR_Y + G_HEIGHT/2

    colors = ALG(x0, xn, y0, yn)
    disp(colors)

def key_event(event):
    global G_WIDTH, G_HEIGHT, G_CTR_X, G_CTR_Y, CENTER_X, CENTER_Y, ITERS, ITER_CLOCK, ZOOM_LEV

    if event.key == '=' or event.key == '+':
        ITERS += 5
        print('Calculating ' + str(ITERS) + ' iterations')
        return

    if event.key == '-':
        ITERS -= 1
        print('Calculating ' + str(ITERS) + ' iterations')
        return

    if event.key.upper() == 'R':
        compute_update()
        return 

    if event.key == 'right':
        G_CTR_X += G_WIDTH * 0.1
        return
    elif event.key == 'left':
        G_CTR_X -= G_WIDTH * 0.1
        return
    elif event.key == 'up':
        G_CTR_Y -= G_HEIGHT * 0.1
        return
    elif event.key == 'down':
        G_CTR_Y += G_HEIGHT * 0.1
        return

    if event.key.upper() != 'Q':
        return 


    G_WIDTH = 3
    G_HEIGHT = 3

    G_CTR_X = -0.5
    G_CTR_Y = 0

    CENTER_X = D_WIDTH // 2
    CENTER_Y = D_HEIGHT // 2

    ITERS=50
    ITER_CLOCK=0
    ZOOM_LEV = 2

    colors = ALG(-2, 1, -1.5, 1.5)
    disp(colors)


def zoom(event):
    global win, G_HEIGHT, G_WIDTH, CENTER_X, CENTER_Y, D_HEIGHT, D_WIDTH, G_CTR_X, G_CTR_Y, ITERS

    disp(loading)
    
    G_HEIGHT /= ZOOM_LEV
    G_WIDTH /= ZOOM_LEV

    # The coordinate selected
    xc = ((event.xdata-CENTER_X) * (G_WIDTH / D_WIDTH)) + G_CTR_X
    yc = ((event.ydata-CENTER_Y) * (G_HEIGHT / D_HEIGHT)) + G_CTR_Y

    G_CTR_X = xc
    G_CTR_Y = yc

    x0 = xc - G_WIDTH/2 
    xn = xc + G_WIDTH/2
    y0 = yc - G_HEIGHT/2 
    yn = yc + G_HEIGHT/2

    colors = ALG(x0, xn, y0, yn, iters=ITERS)

    print("Displaying new mandel\nCenter: (" + str(xc) + ", " + str(yc) + ")")
    disp(colors)

    update_globals()

def getInfo():
    return "Rendered with %d iterations\nAt coordinates %f, %f" % (ITERS, G_CTR_X, G_CTR_Y)

def disp(img):
    fig.clear()
    ax.imshow(img)
    ax.text(0,0,getInfo())
    fig.add_axes(ax)
    fig.canvas.draw()

def main():
    # Init
    global ALG
    ALG = mandel
    colors = ALG(-2, 1, -1.5, 1.5)
    ax.imshow(colors)
    plt.show()
    
fig.canvas.mpl_connect('button_press_event', zoom)
fig.canvas.mpl_connect('key_press_event', key_event)
main()