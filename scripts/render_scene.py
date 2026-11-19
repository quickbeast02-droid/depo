#!/usr/bin/env python3
"""Original stylized 3D office and animated cat, using headless VTK CPU rendering."""
import argparse, math, pathlib, vtk

def actor(renderer,source,pos,scale,color,group=None):
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(source.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper);a.SetPosition(*pos);a.SetScale(*scale)
    p=a.GetProperty();p.SetColor(*color);p.SetAmbient(.25);p.SetDiffuse(.7);p.SetSpecular(.3);p.SetSpecularPower(30)
    if group:group.AddPart(a)
    else:renderer.AddActor(a)
    return a
def ball(r,pos,scale,color,group=None):
    s=vtk.vtkSphereSource();s.SetThetaResolution(28);s.SetPhiResolution(24);return actor(r,s,pos,scale,color,group)
def cube(r,pos,scale,color,group=None):
    s=vtk.vtkCubeSource();return actor(r,s,pos,scale,color,group)
def ear(r,pos,group):
    s=vtk.vtkConeSource();s.SetResolution(28);s.SetRadius(.22);s.SetHeight(.5);a=actor(r,s,pos,(1,1,1),(.94,.44,.12),group);a.RotateY(-90)
def line(r,start,end,radius,color):
    s=vtk.vtkLineSource();s.SetPoint1(*start);s.SetPoint2(*end)
    t=vtk.vtkTubeFilter();t.SetInputConnection(s.GetOutputPort());t.SetRadius(radius);t.SetNumberOfSides(9)
    return actor(r,t,(0,0,0),(1,1,1),color)
def make_scene():
    r=vtk.vtkRenderer();r.SetBackground(.025,.045,.10);r.SetBackground2(.11,.16,.23);r.GradientBackgroundOn()
    navy=(.07,.12,.20);gold=(1,.67,.24);aqua=(.23,.78,.89);orange=(.96,.45,.12)
    cube(r,(0,0,-.1),(10,10,.2),(.10,.12,.17))
    cube(r,(0,3.0,2.2),(10,.13,5.3),(.08,.12,.18))
    for x in (-3.1,3.1):
        cube(r,(x,2.87,2.5),(.11,.11,3.7),(.28,.38,.48))
        cube(r,(x,2.80,2.2),(.72,.08,1.8),(.07,.31,.43))
    for z in (1.45,4.22):
        cube(r,(0,2.78,z),(7,.09,.055),aqua)
    cube(r,(0,-.4,.02),(5.4,3.5,.05),(.14,.14,.23))
    for x in (-1.8,1.8):
        cube(r,(x,-1.35,.60),(.14,.13,1.1),(.15,.11,.16))
    cube(r,(0,-1.35,1.25),(4.65,1.38,.19),(.40,.24,.17))
    cube(r,(0,-2.00,1.23),(4.65,.07,.05),gold)
    cube(r,(-.6,-1.25,1.43),(1.15,.88,.06),(.12,.17,.24))
    cube(r,(-.6,-.84,1.90),(1.15,.1,.95),(.14,.18,.24))
    cube(r,(-.6,-.905,1.9),(1.00,.02,.76),(.12,.37,.47))
    for x in (-2.3,2.3):
        cube(r,(x,.95,.46),(.5,.5,.70),(.13,.17,.22))
        for j in range(5):
            ang=j*math.pi*2/5
            ball(r,(x+.23*math.cos(ang),.95+.21*math.sin(ang),1.02),(.20,.17,.40),(.15,.44,.27))
    ball(r,(.48,.5,1.86),(.56,.43,.88),(.12,.24,.39))
    ball(r,(.48,-.02,1.73),(.26,.11,.38),(.95,.89,.8))
    cube(r,(.48,-.14,1.73),(.10,.065,.34),(.79,.20,.25))
    for x in (-.02, .98):ball(r,(x,-.48,1.36),(.25,.26,.14),orange)
    head=vtk.vtkAssembly();head.SetPosition(.49,.32,2.73);r.AddActor(head)
    ball(r,(0,0,0),(.71,.59,.66),orange,head)
    ball(r,(0,-.43,-.23),(.42,.19,.24),(.99,.75,.49),head)
    for x in (-.43,.43):
        ear(r,(x,-.03,.57),head)
        ball(r,(x,-.19,.60),(.10,.05,.16),(.85,.40,.39),head)
    for x in (-.26,.26):
        ball(r,(x,-.52,.08),(.20,.11,.22),(.99,.97,.93),head)
        ball(r,(x,-.635,.06),(.095,.045,.15),(.045,.08,.13),head)
        ball(r,(x-.025,-.672,.12),(.043,.015,.048),(1,1,1),head)
    ball(r,(0,-.606,-.22),(.10,.067,.052),(.44,.15,.20),head)
    for sign in (-1,1):
        line(r,(sign*.18,-.58,-.28),(sign*.59,-.57,-.20),.008,(.94,.75,.53))
        line(r,(sign*.18,-.58,-.31),(sign*.61,-.57,-.40),.008,(.94,.75,.53))
    cube(r,(1.42,-1.60,1.40),(.4,.65,.045),(.13,.17,.22))
    for pos,color,intensity in [((-4,-5,8),(1,.82,.65),.85),((3,4,6),(.35,.70,1),1.05),((3,-5,3),(1,1,1),.4)]:
        light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos);light.SetFocalPoint(0,0,2);light.SetColor(*color);light.SetIntensity(intensity);r.AddLight(light)
    cam=r.GetActiveCamera();cam.SetPosition(0,-9.6,3.2);cam.SetFocalPoint(.1,.05,2.1);cam.SetViewUp(0,0,1);cam.SetViewAngle(36);cam.SetClippingRange(.1,50)
    return r,cam,head
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--frames',type=int,default=24)
    p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960);p.add_argument('--shot',type=int,default=0);p.add_argument('--seed',type=int,default=0)
    a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
    r,cam,head=make_scene()
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(a.width,a.height);win.AddRenderer(r);win.SetMultiSamples(4)
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
    writer=vtk.vtkPNGWriter()
    for i in range(a.frames):
        t=i/max(1,a.frames-1);ph=2*math.pi*t
        head.SetOrientation(2*math.sin(ph),0,7*math.sin(ph+a.shot*.4))
        cam.SetPosition(-.17+.34*t+(a.shot%3-1)*.25,-9.6+.25*t,3.15+.07*math.sin(ph))
        cam.SetFocalPoint(.1,.05,2.1)
        win.Render();capture.Modified();capture.Update()
        writer.SetFileName(str(out/f'frame_{i:04d}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
    win.Finalize()
if __name__=='__main__':main()
