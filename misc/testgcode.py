import os 
import numpy as np 


tool_diameter = 3.0
stepz  = tool_diameter * 0.2
stepxy = tool_diameter * 0.4
fz  = 100
fxy = 300


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


def create_grids(x0, y0, fxy=300, fz=100, zsafe=3, max_zmill=-1.0):
    dxy = 5
    nline = 5
    z0 = 0
    dz = max_zmill/(nline-1)
    zinit = -0.1
    gcode = [f'G0 Z{zsafe}', f'G0 X{x0:.2f} Y{y0:.2f}']
    for i in range(nline):
        gcode += [f'G0 X{x0+(i+1)*dxy:.2f} Y{y0:.2f}', 
            f'G1 Z{zinit:.2f} f{fz}', 
            f'G1 X{x0+(i+1)*dxy:.2f} Y{y0+(nline+1)*dxy:.2f} F{fxy}', 
            f'G1 Z{zinit+z0+i*dz:.2f} F{fz}', 
            f'G1 X{x0+(i+1)*dxy:.2f} Y{y0:.2f} F{fxy}', 
            f'G0 Z{zsafe}']
        gcode += [f'G0 X{x0:.2f} Y{y0+(i+1)*dxy:.2f}', 
            f'G1 Z{zinit:.2f} f{fz}', 
            f'G1 X{x0+(nline+1)*dxy:.2f} Y{y0+(i+1)*dxy:.2f} F{fxy}', 
            f'G1 Z{zinit+z0+i*dz:.2f} F{fz}', 
            f'G1 X{x0:.2f} Y{y0+(i+1)*dxy:.2f} F{fxy}', 
            f'G0 Z{zsafe}']
    return gcode 


def create_circles(x0, y0, fxy=300, fz=100, zsafe=3, zmill=-0.4):
    rs = [15, ]
    nseg = 60
    dangle = 40
    gcode = [f'G0 Z{zsafe}', f'G0 X{x0:.2f} Y{y0}']
    for r in rs:
        gcode += [f'G0 X{x0+r:.2f} Y{y0:.2f}', f'G1 Z{zmill:.2f} F{fz}']
        for i in range(nseg):
            ang = np.pi*2/nseg * (i+1)
            gcode += [f'G1 X{x0+r*np.cos(ang):.2f} Y{y0+r*np.sin(ang):.2f} F{fxy}']
        gcode += [f'G0 Z{zsafe}']

    for ang in np.arange(0,np.pi*2,dangle/180*np.pi):
        gcode += [f'G0 X{x0:.2f} Y{y0:.2f}', 
                  f'G1 Z{zmill:.2f} F{fz}', 
                  f'G1 X{x0+rs[0]*np.cos(ang):.2f} Y{y0+rs[0]*np.sin(ang):.2f} F{fxy}', 
                  f'G0 Z{zsafe}']    

    return gcode 


def create_holes(x0, y0, fxy=300, fz=100, zsafe=3, stepxy=0.4, direction=0):
    # direction: 0 - climb; 1 - convetional
    nlayer = 4
    rs = [2*i for i in range(nlayer)]
    zs = [-2+i*0.5 for i in range(nlayer)]
    ang0 = 90
    nseg = 6
    angs = np.linspace(0,360,nseg+1)
    if direction > 0:
        angs = angs[::-1]

    gcode = [f'G0 Z{zsafe}', f'G0 X{x0:.2f} Y{y0:.2f}', f'G1 Z{zs[0]:.2f} F{fz}', f'G0 Z{zsafe}']
    for i in range(1,nlayer):
        for j in range(nlayer-i):
            gcode += [f'G1 X{x0+rs[i-1]*np.cos(ang0/180*np.pi):.2f} Y{y0+rs[i-1]*np.sin(ang0/180*np.pi):.2f} F{fxy}', 
                      f'G1 Z{zs[nlayer-1-j]:.2f} F{fz}']
            for r in np.arange(rs[i-1], rs[i], stepxy):
                gcode += [f'G1 X{x0+(r+stepxy)*np.cos(ang0/180*np.pi):.2f} Y{y0+(r+stepxy)*np.sin(ang0/180*np.pi):.2f} F{fxy}']
                for dang in angs:
                    ang = ang0 + dang
                    gcode += [f'G1 X{x0+(r+stepxy)*np.cos(ang/180*np.pi):.2f} Y{y0+(r+stepxy)*np.sin(ang/180*np.pi):.2f} F{fxy}']
    gcode += [f'G0 Z{zsafe}']
    return gcode 


def test_dxy(x0, y0, fxy=300, fz=100, zsafe=3, min_dxy=0.1, max_dxy=1, direction=0, zmill=-0.4):
    # direction: 0 - row; 1 - column
    size = 12
    nline = int(2*size/(max_dxy + min_dxy)) + 1
    dxy = (max_dxy - min_dxy) / (nline-2)
    gcode = [f'G0 Z{zsafe}']
    for i in range(nline):
        if direction == 0:
            pstart = (x0, y0+i*min_dxy+i*(i-1)*dxy/2)
            pend   = (x0+size, y0+i*min_dxy+i*(i-1)*dxy/2)
        else:
            pstart = (x0+i*min_dxy+i*(i-1)*dxy/2, y0)
            pend   = (x0+i*min_dxy+i*(i-1)*dxy/2, y0+size)

        gcode += [f'G0 X{pstart[0]:.2f} Y{pstart[1]:.2f}', 
                  f'G1 Z{zmill:.2f} F{fz}', 
                  f'G1 X{pend[0]:.2f} Y{pend[1]:.2f} F{fxy}', 
                  f'G0 Z{zsafe}']
    return gcode 

def test_engrave(x0, y0, fxy=300, fz=100, zsafe=3, depth0=3.0, fengrave=200, dx=0.5, dy=0.2, dz=-0.4):
    size = 30
    depth = depth0/2
    gcode = [f'G0 Z{zsafe}', f'G0 X{x0:.2f} Y{y0:.2f}']

    zmill = dz
    flag = 1
    while zmill >= -depth:
        if flag > 0:
            xend = x0 + size
        else:
            xend = x0
        gcode += [f'G1 Z{max(zmill, -depth):.2f} F{fz}', f'G1 X{xend} Y{y0} F{fxy}']
        zmill += dz
        flag = int(-1*flag)

    flag = 1    
    gcode += [f'G0 Z{zsafe}', f'G0 X{x0} Y{y0+dy}']
    for j in range(1, int(size/dy)+1):
        for i in range(int(size/dx)+1)[::flag]:
            px = x0 + i*dx
            py = y0 + j*dy
            pz = depth * (np.sin(i*dx/size*2*np.pi) * np.sin(j*dy/size*2*np.pi)-1)
            gcode += [f'G1 X{px:.2f} Y{py:.2f} Z{pz:.2f} F{fengrave}']
        flag = int(-1*flag)
    gcode.append(f'G0 Z{zsafe}')
    return gcode 
    

def main(fn, fxy=300, fz=100, fengrave=200, 
        zmill=-0.4, max_zmill=-1, 
        stepxy=0.4, max_stepxy=1, 
        engrave_depth=3, engrave_stepxy=0.2):
    
    zsafe = 3
    engrave_dx = 0.5

    gcode = ['G90', 'G49', 'M3 S1000']

    gcode += create_grids(x0=0, y0=0, fxy=fxy, fz=fz, zsafe=zsafe, max_zmill=max_zmill)
    gcode += test_engrave(x0=34, y0=0, fxy=fxy, fz=fz, zsafe=zsafe, depth0=engrave_depth, fengrave=fengrave, dx=engrave_dx, dy=engrave_stepxy, dz=zmill)

    gcode += create_circles(x0=15, y0=49, fxy=fxy, fz=fz, zsafe=zsafe, zmill=zmill)

    gcode += create_holes(x0=40, y0=58, fxy=fxy, fz=fz, zsafe=zsafe, stepxy=stepxy, direction=1)
    gcode += create_holes(x0=58, y0=58, fxy=fxy, fz=fz, zsafe=zsafe, stepxy=stepxy, direction=0)

    gcode += test_dxy(x0=34, y0=35, fxy=fxy, fz=fz, zsafe=zsafe, min_dxy=0.1, max_dxy=max_stepxy, direction=0, zmill=zmill)
    gcode += test_dxy(x0=52, y0=35, fxy=fxy, fz=fz, zsafe=zsafe, min_dxy=0.1, max_dxy=max_stepxy, direction=1, zmill=zmill)



    gcode += ['G0 Z3', 'G0 X0 Y0', 'M05', 'M02']
    save_gcode(clean_gcode(gcode), fn)
    return 


if __name__ == "__main__":
    for d in [0.1, 0.5, 1, 1.5, 2, 2.5, 3]:
        for frate in [200, 300, 400, 600, 800, 1000]:
            fn = f'D{d*10:02.0f}F{frate/100:.0f}.gcode'
            print(fn)
            main(fn, fxy=frate, fz=100, fengrave=frate, 
                zmill=-max(0.1, d/6), max_zmill=-max(0.1, d/3), 
                stepxy=max(0.1, d*0.3), max_stepxy=max(0.1, d), 
                engrave_depth=3, engrave_stepxy=max(0.1, d/10))




