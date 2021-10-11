import os 
import numpy as np 


def save_gcode(gcode, fn):
    print('save gcode to:', fn)
    open(fn, 'wb').write(b'\r\n'.join([x.encode() for x in gcode]))
    return 

def clean_gcode(gcode):
    if len(gcode) > 1:
        i = 1
        while i < len(gcode):
            if (gcode[i].strip() == gcode[i-1].strip()) or (('G0 X' in gcode[i-1]) and ('G0 X' in gcode[i])):
                gcode.pop(i-1)
            else:
                i += 1
    return gcode

def flat_surface(fn, lx=70, ly=67):
    gcode = ['G90', 'G49', 'M3 S1000', 'G1 Z-2 F100']
    dy = 0.4
    fxy = 500
    x = 0
    ys = np.arange(0, ly+dy, dy)
    for y in ys:        
        gcode += [f'G1 X{lx-x:.2f} F{fxy}', f'G1 Y{y:.2f} F{fxy}']
        x = lx - x

    gcode += ['M05', 'M02']
    save_gcode(clean_gcode(gcode), fn)
    return 

def create_front(fn):
    gcode = ['G90', 'G49', 'M3 S1000', 'G0 Z3']
    dxy = 0.3
    dy = dxy
    fxy = 500
    size = 65
    offset = 3.175/2

    x = size/3*2+offset
    gcode += [f'G0 X{x:.3f} Y{-offset:.3f}', 'G1 Z-8 F200']
    for y in np.arange(-offset+dy, size/3-offset+dy, dy):
        x = (size/3*2+offset + size-offset) - x
        gcode += [f'G1 Y{y:.3f} F{fxy}', f'G1 X{x:.3f} F{fxy}']

    x = size/3*2 + offset
    y = size/3 - offset
    gcode += [f'G1 X{x:.3f} Y{y:.3f} F{fxy}']
    ys = np.arange(y+dy, size/3*2-offset+dy, dy)
    zs = np.linspace(-8, -6, len(ys))
    #zs = [-8+ 0.4*(int((y-size/3+offset)/(size/12))+1) for y in ys]
    for i in range(len(ys)):
        x = (size/3*2+offset + size-offset) - x
        gcode += [f'G1 Y{ys[i]:.3f} Z{zs[i]:.3f} F{fxy}', f'G1 X{x:.3f} F{fxy}']

    x = size/3*2 + offset
    y = size/3*2 - offset
    gcode += [f'G1 X{x:.3f} Y{y:.3f} Z-6 F{fxy}']
    for y in list(np.arange(y+dy, size, dy)) + [size]:
        x = (size/3*2+offset + size-offset) - x
        gcode += [f'G1 Y{y:.3f} F{fxy}', f'G1 X{x:.3f} F{fxy}']

    x = size/3*2 + offset
    y = size/3*2 + offset
    gcode += [f'G1 X{x:.3f} Y{y:.3f} F{fxy}']
    dx = -dxy
    xs = np.arange(x+dx, size/3+offset+dx, dx)
    zs = np.linspace(-6, -4, len(xs))
    for i in range(len(zs)):
        y = (size/3*2+offset + size) - y 
        gcode += [f'G1 X{xs[i]:.3f} Z{zs[i]:.3f} F{fxy}', f'G1 Y{y:.3f} F{fxy}']

    x = size/3 + offset
    y = size/3*2 + offset
    gcode += [f'G1 X{x:.3f} Y{y:.3f} F{fxy}']
    for x in list(np.arange(x+dx, offset, dx)) + [offset]:
        y = (size/3*2+offset + size) - y 
        gcode += [f'G1 X{x:.3f} F{fxy}', f'G1 Y{y:.3f} F{fxy}']

    x = size/3 - offset
    y = size/3*2 + offset
    gcode += [f'G1 X{x:.3f} Y{y:.3f} F{fxy}']
    dy = -dxy
    ys = np.arange(y+dy, size/3+offset+dy, dy)
    zs = np.linspace(-4, -2, len(ys))
    for i in range(len(zs)):
        x = (size/3-offset + offset) - x 
        gcode += [f'G1 Y{ys[i]:.3f} Z{zs[i]:.3f} F{fxy}', f'G1 X{x:.3f} F{fxy}']

    x = size/3 - offset
    y = size/3 + offset
    gcode += [f'G1 X{x:.3f} Y{y:.3f} F{fxy}']
    for y in np.arange(y+dy, 0+dy, dy):
        x = (size/3-offset + offset) - x 
        gcode += [f'G1 y{y:.3f} F{fxy}', f'G1 X{x:.3f} F{fxy}']

    gcode += [f'G1 X{size/3-offset} Y{-offset} F{fxy}', 
              f'G1 Z-1.6 F{fxy}']
    
    dy = dxy
    ys = np.arange(-offset+dy, size/3-offset, dy)
    zs = [-1.6+ 0.4*int((y+offset)/(size/12)) for y in ys]
    x = size/3
    for i in range(len(ys)):
        x = (size/3 + size/3*2) - x
        gcode += [f'G1 Y{ys[i]:.3f} Z{zs[i]:.3f} F{fxy}', f'G1 X{x:.3f} F{fxy}']

    gcode += ['G0 Z3', 'G0 X0 Y65', 'M05', 'M02']
    save_gcode(clean_gcode(gcode), fn)
    return 


create_front('frontjy.gcode')
