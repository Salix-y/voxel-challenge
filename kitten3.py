from scene import Scene
import taichi as ti
from taichi.math import *
scene = Scene(voxel_edges=0, exposure=1)
scene.set_floor(-64, (1.0, 1.0, 1.0))
scene.set_background_color((0.5, 0.8, 0.9))
scene.set_directional_light((-1, 1, 0.3), 0.0, (1, 1, 1))
char_list = ['0001110111101111011110111','1011101011000110101101011','0001110111101111011100011',
             '0001101111011110111100011','0101101011000110101101011','0001110111101111011100011']
@ti.func
def create_char(pos, type, color):
    for l in ti.static(range(6)):
        for i in ti.static(range(5)):
            for j in ti.static(range(5)):
                index = ti.static(j * 5 + i)
                if char_list[l][index] == '0':
                    scene.set_voxel( vec3(j,i + l * 5, 0) + pos, 2, vec3(0.6,0.9,1))
@ti.func
def rgb(r,g,b):
    return vec3(r/255.0, g/255.0, b/255.0)
@ti.func
def proj_plane(o, n, t, p):
    y = dot(p-o,n);xz=p-(o+n*y);bt=cross(t,n);return vec3(dot(xz,t), y, dot(xz, bt))
@ti.func
def elli(rx,ry,rz,p1_unused,p2_unused,p3_unused,p):
    r = p/vec3(rx,ry,rz); return ti.sqrt(dot(r,r))<1
@ti.func
def cyli(r1,h,r2,round, cone, hole_unused, p):
    ms=min(r1,min(h,r2));rr=ms*round;rt=mix(cone*(max(ms-rr,0)),0,float(h-p.y)*0.5/h);r=vec2(p.x/r1,p.z/r2)
    d=vec2((r.norm()-1.0)*ms+rt,ti.abs(p.y)-h)+rr; return min(max(d.x,d.y),0.0)+max(d,0.0).norm()-rr<0
@ti.func
def box(x, y, z, round, cone, unused, p):
    ms=min(x,min(y,z));rr=ms*round;rt=mix(cone*(max(ms-rr,0)),0,float(y-p.y)*0.5/y);q=ti.abs(p)-vec3(x-rt,y,z-rt)+rr
    return ti.max(q, 0.0).norm() + ti.min(ti.max(q.x, ti.max(q.y, q.z)), 0.0) - rr< 0
@ti.func
def tri(r1, h, r2, round_unused, cone, vertex, p):
    r = vec3(p.x/r1, p.y, p.z/r2);rt=mix(1.0-cone,1.0,float(h-p.y)*0.5/h);r.z+=(r.x+1)*mix(-0.577, 0.577, vertex)
    q = ti.abs(r); return max(q.y-h,max(q.z*0.866025+r.x*0.5,-r.x)-0.5*rt)< 0
@ti.func
def make(func: ti.template(), p1, p2, p3, p4, p5, p6, pos, dir, up, color, mat, mode):
    max_r = 2 * int(max(p3,max(p1, p2))); dir = normalize(dir); up = normalize(cross(cross(dir, up), dir))
    for i,j,k in ti.ndrange((-max_r,max_r),(-max_r,max_r),(-max_r,max_r)):
        xyz = proj_plane(vec3(0.0,0.0,0.0), dir, up, vec3(i,j,k))
        if func(p1,p2,p3,p4,p5,p6,xyz):
            if mode == 0: scene.set_voxel(pos + vec3(i,j,k), mat, color) # additive
            if mode == 1: scene.set_voxel(pos + vec3(i,j,k), 0, color) # subtractive
            if mode == 2 and scene.get_voxel(pos + vec3(i,j,k))[0] > 0: scene.set_voxel(pos + vec3(i,j,k), mat, color)
@ti.kernel
def initialize_voxels():
    create_char(vec3(-35, 0, -35), 1, vec3(1, 1, 1))
    make(elli,31.5,32.0,36.0,0.0,0.0,0.0,vec3(13,16,2),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(255,255,255),1,0)
    make(elli,13.0,21.5,23.5,0.0,0.0,0.0,vec3(-8,9,3),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(255,255,255),1,0)
    make(tri,2.5,5.5,5.0,0.3,0.0,0.5,vec3(-15,17,3),vec3(1.0,-0.2,0.0),vec3(-0.2,-1.0,0.0),rgb(255,173,167),1,0)
    make(elli,32.0,32.0,32.0,0.0,0.0,0.0,vec3(9,37,-26),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(195,125,71),1,2)
    make(elli,32.0,32.0,32.0,0.0,0.0,0.0,vec3(12,33,32),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(85,54,30),1,2)
    make(tri,19.5,8.5,17.5,0.1,0.0,0.5,vec3(18,41,26),vec3(-1.0,0.0,-0.2),vec3(-0.0,0.9,0.3),rgb(85,54,30),1,0)
    make(tri,19.5,8.5,17.5,0.1,0.0,0.5,vec3(18,42,-24),vec3(-1.0,0.1,0.1),vec3(0.0,0.9,-0.4),rgb(196,125,72),1,0)
    make(cyli,1.0,2.0,1.0,0.1,0.0,0.0,vec3(-20,14,3),vec3(-0.2,-1.0,-0.0),vec3(1.0,-0.2,-0.0),rgb(101,98,97),1,2)
    make(cyli,1.0,3.0,1.0,0.1,0.0,0.0,vec3(-20,12,0),vec3(-0.1,-0.3,-1.0),vec3(1.0,-0.2,-0.1),rgb(101,98,97),1,2)
    make(cyli,1.0,3.0,1.0,0.1,0.0,0.0,vec3(-20,12,6),vec3(0.1,0.4,-0.9),vec3(1.0,-0.2,-0.0),rgb(101,98,97),1,2)
    make(tri,19.5,8.9,17.5,0.1,0.0,0.5,vec3(16,36,-21),vec3(-1.0,0.1,0.1),vec3(0.0,0.9,-0.4),rgb(223,188,153),1,0)
    make(tri,19.5,8.5,17.5,0.1,0.0,0.5,vec3(16,34,23),vec3(-1.0,0.0,-0.2),vec3(-0.0,0.9,0.3),rgb(154,141,131),1,0)
    make(elli,37.5,37.5,37.5,0.0,0.0,0.0,vec3(12,-15,2),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(255,255,255),1,0)
    make(elli,4.5,5.5,6.5,0.0,0.0,0.0,vec3(-15,27,-12),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(16,21,28),1,2)
    make(elli,9.1,1.5,1.5,0.0,0.0,0.0,vec3(-17,26,-9),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(234,237,241),1,2)
    make(elli,32.0,32.0,32.0,0.0,0.0,0.0,vec3(12,-37,-30),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(195,125,71),1,2)
    make(elli,33.0,20.5,12.0,0.0,0.0,0.0,vec3(11,13,-22),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(195,125,71),1,2)
    make(elli,4.5,5.5,6.5,0.0,0.0,0.0,vec3(-15,27,17),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(16,21,28),1,2)
    make(elli,9.1,1.5,1.5,0.0,0.0,0.0,vec3(-17,26,17),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(234,237,241),1,2)
    make(elli,33.0,20.5,12.0,0.0,0.0,0.0,vec3(11,-3,35),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(195,125,71),1,2)
    make(elli,33.0,20.5,12.0,0.0,0.0,0.0,vec3(11,-3,33),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(195,125,71),1,2)
initialize_voxels()
scene.finish()
