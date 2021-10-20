import os 
import numpy as np 

def save_gcode(gcode, fn):
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

def nut_hole(cx, cy, d1=-13.4, d2=-6.5, fz=200, fxy=300, dxy=0.3, dtool=3.175):
    gcode = ['G0 Z3', f'G0 X{cx:.3f} Y{cy:.3f}', f'G1 Z{d1} F{fz}', f'G1 Z{d2} F{fz}']
    rmax = (2.7-dtool/2)/1.732*2
    rs = list(np.arange(dxy, rmax, dxy)) + [rmax]
    for r in rs:
        gcode += [f'G1 X{cx+r:.3f} F{fxy}']
        for ang in range(60, 360+60, 60):
            gcode += [f'G1 X{cx+r*np.cos(ang/180*np.pi):.3f} Y{cy+r*np.sin(ang/180*np.pi):.3f} F{fxy}']
    gcode.append('G0 Z3')
    return gcode 


def move_along_yaxis(x, zmin, zmax, ymin, ymax, dz, fz, fxy):
    gcode = ['G0 Z3', f'G0 X{x:.3f} Y{ymin:.3f}']
    xdir = 1
    zs = list(np.arange(zmin+dz, zmax, dz)) + [zmax]
    for z in zs:        
        if xdir > 0:
            gcode += [f'G1 Z{z} F{fz}', f'G1 Y{ymax:.3f} F{fxy}']
        else:
            gcode += [f'G1 Z{z} F{fz}', f'G1 Y{ymin:.3f} F{fxy}']
        xdir *= -1
    return gcode 

def pocket(xmin, xmax, ymin, ymax, depth, dx, fz, fxy, offset, xdir=1):
    if xdir > 0:
        gcode = ['G0 Z3', f'G0 X{xmin-offset:.3f} Y{ymin:.3f}', f'G1 Z{depth} F{fz}']
        xs = list(np.arange(xmin-offset+dx, xmax-offset, dx)) + [xmax-offset]
    else:
        gcode = ['G0 Z3', f'G0 X{xmax+offset:.3f} Y{ymin:.3f}', f'G1 Z{depth} F{fz}']
        xs = list(np.arange(xmax+offset-dx, xmin+offset, -dx)) + [xmin+offset]

    ydir = 1
    for x in xs:
        gcode.append(f'G1 X{x:.3f} F{fxy}')
        if ydir > 0:
            gcode.append(f'G1 Y{ymax:.3f} F{fxy}')
        else:
            gcode.append(f'G1 Y{ymin:.3f} F{fxy}')
        ydir *= -1
    return gcode 


def move_inline(xmin, xmax, ymin, ymax, depth, dz, fz, fxy):
    gcode = ['G0 Z3', f'G0 X{xmax:.3f} Y{ymin:.3f}']
    zs = list(np.arange(dz, depth, dz)) + [depth]
    for z in zs:
        gcode += [F'G1 Z{z} F{fz}', f'G1 X{xmax:.3f} Y{ymax:.3f}', 
            f'G1 X{xmin:.3f} Y{ymax:.3f}', f'G1 X{xmin:.3f} Y{ymin:.3f}', f'G1 X{xmax:.3f} Y{ymin:.3f}', ]
    return gcode 

def xbottom(fn='xbottom.gcode'):
    offset = 3.175/2
    frate = 800
    fz = 100
    max_depth = -13.2 - 0.2
    ymin = -45.1
    ymax = 0
    dz = -0.5
    dz_inline = -1.0
    dx = 1.2
    dx_fine = 0.2
    dy = dx
    
    gcode = ['G90', 'G49', 'M3 S2000', 'G0 Z3']
    gcode += nut_hole(cx=179.3/2, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2-45, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2+45, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2-66, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2+66, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)

    for i in range(4):
        gcode += nut_hole(cx=11.3+i*44.9+11, cy=-15, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
        gcode += nut_hole(cx=11.3+i*44.9+11, cy=-35, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)

    path = [(offset, -2.7), 
            (offset, -0.7), 
            (8+offset, -0.7), 
            (8+offset, max_depth)]
    
    
    gcode += move_along_yaxis(x=offset, zmin=0, zmax=-2.7, ymin=ymin-offset, ymax=ymax-offset, dz=dz, fz=fz, fxy=frate)
    for x in list(np.arange(offset, 8+offset, dx)) + [8+offset]:
        gcode += move_along_yaxis(x=x, zmin=0, zmax=-0.7, ymin=ymin-offset, ymax=ymax-offset, dz=dz, fz=fz, fxy=frate)

    gcode += move_along_yaxis(x=179.3-offset, zmin=0, zmax=-2.7, ymin=ymin-offset, ymax=ymax-offset, dz=dz, fz=fz, fxy=frate)
    for x in list(np.arange(171.3-offset, 179.3-offset, dx)) + [179.3-offset]:
        gcode += move_along_yaxis(x=x, zmin=0, zmax=-0.7, ymin=ymin-offset, ymax=ymax-offset, dz=dz, fz=fz, fxy=frate)

    gcode += move_inline(xmin=8+offset, xmax=11.3-offset, ymin=ymin-offset, ymax=-offset, depth=max_depth, dz=dz_inline, fz=fz, fxy=frate)
    xinits = np.arange(3)*44.9 + 11.3+22
    for x0 in xinits:
        gcode += move_inline(xmin=x0+offset, xmax=x0+22.9-offset, ymin=ymin-offset, ymax=-offset, depth=max_depth, dz=dz_inline, fz=fz, fxy=frate)

    xinits = np.arange(4)*44.9 + 11.3
    for x0 in xinits:
        gcode += pocket(xmin=x0, xmax=x0+3.7, ymin=ymin-offset, ymax=-offset, depth=-6.5, dx=dx_fine, fz=fz, fxy=frate, offset=offset, xdir=1)
        gcode += pocket(xmin=x0+3.7, xmax=x0+9, ymin=ymin-offset, ymax=-offset, depth=-2.7, dx=dx_fine, fz=fz, fxy=frate, offset=offset, xdir=1)
        gcode += pocket(xmin=x0+9, xmax=x0+13+offset, ymin=ymin-offset, ymax=-offset, depth=-0.7, dx=dx_fine, fz=fz, fxy=frate, offset=offset, xdir=1)
        
        gcode += pocket(xmin=x0+18.3, xmax=x0+22, ymin=ymin-offset, ymax=-offset, depth=-6.5, dx=dx_fine, fz=fz, fxy=frate, offset=offset, xdir=-1)
        gcode += pocket(xmin=x0+13, xmax=x0+18.3, ymin=ymin-offset, ymax=-offset, depth=-2.7, dx=dx_fine, fz=fz, fxy=frate, offset=offset, xdir=-1)


    gcode += ['G0 Z3', 'G0 X0 Y0', 'M05', 'M02']
    save_gcode(clean_gcode(gcode), fn)
    return 

def create_bottom(fn='bottom.gcode'):
    offset = 3.175/2
    frate = 800
    dy = 0.3
    max_depth = -13.2 - 0.2
    ymin = -45.1
    ymax = 0
    path = [(offset, -2.7), 
            (offset, -0.7), 
            (8+offset, -0.7), 
            (8+offset, max_depth)]
    
    xinits = np.arange(4)*44.9 + 11.3
    for x0 in xinits:
        path += [(x0-offset, max_depth), 
            (x0-offset, -6.5), 
            (x0+3.7-offset, -4.5), 
            (x0+3.7-offset, -2.7), 
            (x0+7-offset, -2.7), 
            (x0+9-offset, -0.7), 
            (x0+13+offset, -0.7), 
            (x0+15+offset, -2.7), 
            (x0+18.3+offset, -2.7), 
            (x0+18.3+offset, -4.5), 
            (x0+22+offset, -6.5), 
            (x0+22+offset, max_depth)]
    
    path += [(171.3-offset, max_depth), 
            (171.3-offset, -0.7), 
            (179.3-offset, -0.7), 
            (179.3-offset, -2.7)]

    ys = list(np.arange(ymin-offset, ymax-offset, dy)) + [ymax-offset]
    gcode = ['G90', 'G49', 'M3 S2000', 'G0 Z3', f'G0 X{path[0][0]:.3f} Y{ys[0]:.3f}']
    xdir = 1
    for y in ys:
        gcode.append(f'G1 Y{y:.3f} F{frate}')
        mill = True
        for p in path[::xdir]:
            if len(p) == 2:
                if not mill:
                    gcode.append(f'G0 X{p[0]:.3f}')
                    mill = True
                gcode.append(f'G1 X{p[0]:.3f} Z{p[1]:.3f} F{frate}')
            else:
                gcode.append(f'G0 Z1')
                mill = False
        xdir = int(-1*xdir)
    gcode.append('G0 Z3')

    gcode += nut_hole(cx=179.3/2, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2-45, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2+45, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2-66, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
    gcode += nut_hole(cx=179.3/2+66, cy=10, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)

    for i in range(4):
        gcode += nut_hole(cx=11.3+i*44.9+11, cy=-15, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)
        gcode += nut_hole(cx=11.3+i*44.9+11, cy=-35, d1=-13.4, d2=-6.5, fz=100, fxy=frate, dxy=dy, dtool=offset*2)


    gcode += ['G0 Z3', 'G0 X0 Y0', 'M05', 'M02']
    save_gcode(clean_gcode(gcode), fn)
    return 

def create_top(fn='top.gcode'):
    offset = 3.175/2
    frate = 800
    max_depth = -13.2 - 0.2
    ymin = 45.1
    ymax = 0
    dy = -0.3
    path = [(offset, -4.4), 
            (offset, -2.4), 
            (8+offset, -2.4)]
    
    xinits = np.arange(4)*44.9 + 11.3
    for x0 in xinits:
        path += [(x0-offset, -2.4), 
            (x0+7-offset, -2.4), 
            (x0+7-offset, -4.4), 
            (x0+7-offset, 0), 
            (x0+15+offset, 0), 
            (x0+15+offset, -4.4), 
            (x0+15+offset, -2.4), 
            (x0+22, -2.4)]
    
    path += [(179.3-offset, -2.4),             
            (179.3-offset, -4.4)]

    ys = list(np.arange(ymin+offset, ymax+offset, dy)) + [ymax+offset]
    gcode = ['G90', 'G49', 'M3 S2000', 'G0 Z3', f'G0 X{path[0][0]:.3f} Y{ys[0]:.3f}']
    xdir = 1
    for y in ys:
        gcode.append(f'G1 Y{y:.3f} F{frate}')
        for p in path[::xdir]:
            gcode.append(f'G1 X{p[0]:.3f} Z{p[1]:.3f} F{frate}')
        xdir = int(-1*xdir)

    gcode += ['G0 Z3', 'G0 X0 Y0', 'M05', 'M02']
    save_gcode(clean_gcode(gcode), fn)
    return 

create_bottom()
create_top()
