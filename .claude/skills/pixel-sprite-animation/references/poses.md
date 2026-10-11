# Starting pose values (64x64, facing right, 6 frames)

Hand offsets are pixels relative to the shoulder; feet are absolute (ground row GY=58, hip column CX=30).
Angles: 0 = down, 90 = right/forward, 180 = up. Lists are per frame index 0..5.
Reach: arm ~13 px (6.5+6.5), knight leg ~17 px, ogre leg ~15.6 px.

## Knight - cycles (looping)
- idle: feet (CX+5, CX-4); `tdy=[0,0,1,1,1,0]` (breathing); `wang=165`.
- walk: phase p = i*60deg+30deg; foot x = CX + 6*cos(p), lift = 3*max(0,-sin p); far leg = p+180deg;
  sink = 0.4+1.2*|cos p|; lean 4; far arm swings with the near leg.
- run: same, stride 9, lift 6, sink = 0.5+2.5*|cos p|, lean 14, tabard flap -3, plume (-10, 1+sin p).

## Knight - melee (ready, windup, peak, strike, impact, recovery)
sword: handN=[(5,-2),(-5,-8),(6,-9),(11,0),(10,7),(6,2)], wang=[175,225,150,100,35,120],
       lean=[-4,-12,-2,8,16,6], sink=[1,1.5,1,2,3.5,2], hx=[-1,-3,0,3,5,2], shift=[0,0,0,-2,-2,0],
       trail on frames 3-4.
axe (two-handed): handN=[(5,-4),(-4,-10),(-1,-10),(7,-6),(9,6),(7,0)], wang=[185,215,200,140,70,165],
       lean=[-4,-14,-8,12,22,6], hx=[-1,-3,-2,1,0,0], shift=[0,0,0,-2,-3,0].

## Knight - ranged
bow: bowhand=[(7,5),(10,-1),(12,-5),(12,-5),(11,-5),(9,0)], aim=[65,80,90,92,94,75],
     pull=[0,0,4,9,0,0], hand_pull=[0,0,4,9,10,4], arrow=[nock x4, fly, none],
     elbow=['y','y','xm','xm','xm','y'], shift on frame 4 = -3.
crossbow: R=[(-2,8),(-1,3),(1,-2),(1,-3),(-1,-3),(-1,2)], ang=[100,95,92,90,98,100],
     loaded=[T,T,T,T,F,F], bolt=[load x4, fly, none], shift on frame 4 = -2.

## Knight - hurt and death
hurt:  hx=[-1,-4,-5,-4,-2,0], lean=[-6,-16,-14,-8,-3,2], sink=[1,1.5,2,2,1.5,1],
       flash=[.85,.3,0,0,0,0], feet pulled back, head pushed back (headoff), wang 165->205->165.
death: lean=[-8,-22,-52,-86,-88,-88], sink=[1,3,3,4.5,3,4], hx=[-1,-4,-2,4,4,4],
       feet slide forward to CX+19 / CX+17 on frames 3-5, `wback` + `wpos=[-,-,(40,34),(54,55),(56,57),(56,57)]`
       (sword drops beside the body), `rot_head` + `head_rot=90` from frame 3, `knee='ym'` from frame 3,
       `cloth_ang=[0,0,40,88,88,88]`, flash on frame 0. Frames 3-5 are the lying pose (hold).

## Ogre (ogre_gen.py) - `o_render(p)` with its own pose dicts
Body: skin green (84,140,64), fur loincloth, tusks, leather strap, iron axe. Leg bones 8+8, `REACH = 15.6`,
torso length 14, resting `lean=18` (stooped), head offset +3.5 forward.
idle: feet (CX+5, CX-5), handN=(4,2), wang=228, handF=[(3,12),(3,12),(4,11),(4,11),(3,11),(3,12)], worder='mid'.
walk: stride 5, lift 3, sink=.6+1.6|cos p|, lean 20, same axe-on-shoulder carry.
attack: handN=[(4,2),(-3,-9),(0,-7),(8,-6),(10,6),(6,1)], wang=[228,205,195,140,68,170],
        lean=[18,6,2,24,40,22], sink=[1,1.5,1,2.5,4,2], hx=[0,-3,-3,1,2,1], two_hand from frame 1,
        shift=[0,0,0,-2,-4,-2]. Hit frames 3-4.
hurt: hx=[-1,-4,-4,-3,-1,0], lean=[10,-2,2,10,15,18], eyes shut on frames 1-3, flash=[.85,.3,0,0,0,0].
death: like the knight's (lean to -88, `worder='back'`, axe dropped at (54,55)), `shift` frame 1 = +3,
       cloth_ang=[0,0,70,88,88,88], sink=[1,3,.5,.5,0,0] (the ogre is bulkier: keep it from clipping the bottom).
