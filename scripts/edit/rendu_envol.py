"""Plan B de fin : layout de travelling vertical Zak -> ciel (guide caméra pour Seedance).
Ne sauvegarde PAS le .blend. Usage :
  Blender -b IF/EP01/SCENE_BLENDER/decor_ep01.blend --python IF/EP01/scripts/rendu_envol.py
Sortie : PLANS/P02_test_runway/2_A_ENVOYER/ETAPE_6_fin_B_envol/frames/####.png"""
import bpy, os
ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ICI, "PLANS/P02_test_runway/2_A_ENVOYER/ETAPE_6_fin_B_envol/frames/")
FIN, TENUE = 240, 36          # 10 s à 24 i/s ; 1,5 s de plan fixe avant le décollage
Z_BAS, Z_HAUT = 0.55, 48.0

s = bpy.context.scene
s.frame_start, s.frame_end = 1, FIN

# caméra : plan fixe, puis montée ease-in / ease-out (décollage doux, arrivée posée)
cam = bpy.data.objects["CAM_IF"]
fc = next(f for f in cam.animation_data.action.fcurves if f.data_path == "location" and f.array_index == 2)
while fc.keyframe_points: fc.keyframe_points.remove(fc.keyframe_points[0])
for f, z in [(1, Z_BAS), (TENUE, Z_BAS), (FIN, Z_HAUT)]:
    k = fc.keyframe_points.insert(f, z); k.interpolation = "BEZIER"
    k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
fc.update()

# Zak : boucle de frappe jouée 2x plus vite (frénésie), toujours à l'endroit
rig = bpy.data.objects["RIG_ZAK"]
for f in rig.animation_data.action.fcurves:
    for k in f.keyframe_points:
        k.co[0] = 1 + (k.co[0] - 1) / 2
        k.handle_left[0] = 1 + (k.handle_left[0] - 1) / 2
        k.handle_right[0] = 1 + (k.handle_right[0] - 1) / 2
    f.update()

# layout rapide : Workbench, demi-résolution
s.render.engine = "BLENDER_WORKBENCH"
s.render.resolution_percentage = 50
s.render.image_settings.file_format = "PNG"
s.render.filepath = OUT
bpy.ops.render.render(animation=True)
