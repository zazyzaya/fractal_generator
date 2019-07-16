import ast
import numpy as np
import scipy.misc as scp
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
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

EXP = 2
C = -0.8 + 1j*0.156

ALG = None

loading = Image.open('loading.gif')
fig, ax = plt.subplots()

''' Mandelbrot set with user defined exponent (default 2 for standard set)
'''
def mandel(x0, xn, y0, yn, exp=EXP, iters=ITERS, width=D_WIDTH, height=D_HEIGHT):
    x = np.linspace(x0, xn, width)
    y = np.linspace(y0, yn, height)

    # Combine x and y into a grid of coordinates
    c = x[:, np.newaxis] + 1j*y[np.newaxis, :]
    iter_map = np.zeros((width, height))

    z = c
    for i in range(iters):
        z = z**exp + c
        iter_map[abs(z) <= 100] += 1

    return color(iter_map, iters, height, width)


''' Julia set for constant c and user defined exp
'''
def defined_julia(x0, xn, y0, yn, exp=EXP, c=C, iters=ITERS, width=D_WIDTH, height=D_HEIGHT):
    x = np.linspace(x0, xn, width)
    y = np.linspace(y0, yn, height)

    # Combine x and y into a grid of coordinates
    z = x[:, np.newaxis] + 1j*y[np.newaxis, :]
    iter_map = np.zeros((width, height))

    for i in range(iters):
        z = z**exp + c
        iter_map[abs(z) <= 100] += 1

    return color(iter_map, iters, height, width)


''' Coloring algorithm for generated fractals
'''
def color(iter_map, iters=ITERS, height=D_HEIGHT, width=D_WIDTH):
    iter_map[iter_map <= 2] = 0
    #iter_map[iter_map == iters] = 0
    iter_map = iter_map / iters

    colors = np.full((height, width, 3), [1., 0.1, 0])
    colors = (colors.T * iter_map).T
    
    iter_map = iter_map.T
    for i in range(iter_map.shape[0]):
        for j in range(iter_map.shape[1]):
            if iter_map[i,j] >= 0.95:
                colors[i,j] = [1-iter_map[i,j]**2,0,0.1*iter_map[i,j]]

    return colors

''' After every zoom certain globals are updated as being closer
    to the screen means zooming must accellarate, and fine details need
    more iterations
'''
def update_globals():
    global ZOOM_LEV, ITER_CLOCK, ITERS

    ZOOM_LEV += 0.1
    ITER_CLOCK += 1
    
    if ITER_CLOCK % 3 == 0:
        ITERS += 7


''' Recalculates the fractal with updated globals
'''
def compute_update():
    #disp(loading)

    x0 = G_CTR_X - G_WIDTH/2 
    xn = G_CTR_X + G_WIDTH/2
    y0 = G_CTR_Y - G_HEIGHT/2 
    yn = G_CTR_Y + G_HEIGHT/2

    colors = ALG(x0, xn, y0, yn)
    disp(colors)

''' For user input. User can
        Toggle render iterations (+/-)
        Refresh the screen (R)
        Move the center of the screen (arrows)
        Reset to default screen (Q)
'''
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

    if event.key.upper() != 'H':
        return 

    reset_globals()
    colors = ALG(-2, 1, -1.5, 1.5)
    disp(colors)

''' Puts globals back to initial settings
'''
def reset_globals():
    global G_WIDTH, G_HEIGHT, G_CTR_X, G_CTR_Y, CENTER_X, CENTER_Y, ITERS, ITER_CLOCK, ZOOM_LEV

    G_WIDTH = 3
    G_HEIGHT = 3

    G_CTR_X = -0.5
    G_CTR_Y = 0

    CENTER_X = D_WIDTH // 2
    CENTER_Y = D_HEIGHT // 2

    ITERS=50
    ITER_CLOCK=0
    ZOOM_LEV = 2

''' Zooms in wherever the user clicked on the graph, recalculates and displays
''' 
def zoom(event):
    global win, G_HEIGHT, G_WIDTH, CENTER_X, CENTER_Y, D_HEIGHT, D_WIDTH, G_CTR_X, G_CTR_Y, ITERS

    #disp(loading)
    
    if event.button == 1:
        G_HEIGHT /= ZOOM_LEV
        G_WIDTH /= ZOOM_LEV
    else:
        G_HEIGHT *= ZOOM_LEV
        G_WIDTH *= ZOOM_LEV

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

def submit_z(text):
    global EXP
    
    try:
        z = ast.literal_eval(text)
        EXP = z
        reset_globals()
        compute_update()

    except (ValueError):
        return

def submit_c(text):
    global C

    # Allows complex
    text = text.split('1j*')
    if len(text) == 2:
        try:
            c = float(text[0]) + 1j*float(text[1])
            C = c

        except (ValueError):
            return

    else:
        try:
            c = float(text[0])
            C = c
        except (ValueError):
            return

    reset_globals()
    compute_update()

def getInfo():
    return "Rendered with %d iterations\nAt coordinates %f, %f" % (ITERS, G_CTR_X, G_CTR_Y)

def disp(img):
    ax.clear()
    ax.imshow(img)
    ax.text(0,-10,getInfo())
    plt.axis('off')
    fig.canvas.draw()

def main():
    # Init
    global ALG

    # TODO make this user defined
    ALG = mandel
    colors = ALG(-2, 1, -1.5, 1.5)
    
    # Show initial fractal
    ax.imshow(colors)
    plt.axis('off')
    plt.show()
    
fig.canvas.mpl_connect('button_press_event', zoom)
fig.canvas.mpl_connect('key_press_event', key_event)

main()