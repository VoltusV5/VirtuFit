import bpy
import math
import os

# ===== НАСТРОЙКИ =====
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01  # 1 ед = 1 см

# ===== ОЧИСТКА СЦЕНЫ =====
def clear_scene():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type not in {'CAMERA', 'LIGHT'}:
            obj.select_set(True)
    bpy.ops.object.delete()

# ===== ИМПОРТ ОБЪЕКТА =====
def import_fbx(filepath):
    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return
    bpy.ops.import_scene.fbx(filepath=filepath)
    
    # Получаем последний добавленный объект (предположительно это импортированный объект)
    imported_object = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if imported_object:
        print(f"Объект {imported_object.name} успешно импортирован.")
        # Проверим позицию и размер объекта
        imported_object.location = (-2, 0, 1)  # Устанавливаем объект в центр сцены
        imported_object.scale = (1, 1, 1)  # Убедимся, что объект имеет нормальный размер
        imported_object.show_in_front = True  # Делает объект видимым в рендере (если скрыт)
    else:
        print("Ошибка: объект не был импортирован.")


# ===== ИМПОРТ ОБЪЕКТА ===== ТУТ!!!!!!!!!!!!!!!!!!!!!!!!
fbx_file_path = r"D:\project\VirtuFit\models\MVP_MAN.fbx"  # Укажи путь к своему .fbx
clear_scene()
import_fbx(fbx_file_path)

# ===== ОСВЕЩЕНИЕ =====
def setup_lighting():
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
    sun = bpy.context.object
    sun.data.energy = 5.0
    sun.data.angle = math.radians(15)
    
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
    sun = bpy.context.object
    sun.data.energy = 5.0
    sun.data.angle = math.radians(15)

    bpy.ops.object.light_add(type='AREA', location=(-4, 4, 3))
    area = bpy.context.object
    area.data.energy = 1000
    area.data.size = 5
    area.rotation_euler = (math.radians(60), 0, math.radians(45))

    bpy.ops.object.light_add(type='POINT', location=(0, -2, 3))
    backlight = bpy.context.object
    backlight.data.energy = 300
    backlight.data.shadow_soft_size = 0.5

# ===== КАМЕРА + АНИМАЦИЯ =====
def setup_camera(output):
    for obj in list(bpy.data.objects):
        if obj.type in {'CAMERA', 'EMPTY'}:
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
    empty = bpy.context.object
    empty.name = "CameraPivot"

    bpy.ops.object.camera_add(location=(0, -4.5, 1.5))
    camera = bpy.context.object
    camera.name = "MainCamera"
    camera.data.lens = 35
    camera.data.clip_start = 0.1
    camera.data.clip_end = 100
    camera.parent = empty

    track = camera.constraints.new(type='TRACK_TO')
    track.target = empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    empty.rotation_euler = (0, 0, 0)
    empty.keyframe_insert(data_path="rotation_euler", frame=1)

    empty.rotation_euler = (0, 0, math.radians(360))
    empty.keyframe_insert(data_path="rotation_euler", frame=120)

    scene.camera = camera
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 30

    scene.render.filepath = output
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

# ===== ФОН И КАЧЕСТВО =====
def setup_render_quality():
    scene.render.engine = 'BLENDER_EEVEE_NEXT'  # Или 'BLENDER_EEVEE' если нужна скорость
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.2, 0.2, 0.2, 1)
    bg.inputs[1].default_value = 1.0

import sys
# Получаем путь для сохранения из аргументов
try:
    args = sys.argv[sys.argv.index("--") + 1:]
    output_path = args[0]
except:
    output_path = r"D:\project\VirtuFit\video\render_output.mp4"

# ===== МАСШТАБ КОСТЕЙ =====
armature_name = "Armature"
armature = bpy.data.objects.get(armature_name)

if armature and armature.type == 'ARMATURE':
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    
    bones_to_scale = {
        "Грудь в обхвате": (float(args[2]), 1, float(args[2])),
        "длина плечь1": (float(args[5]), 1, float(args[5])),
        "длина плечь2": (float(args[5]), 1, float(args[5])),
        "Правое бедро": (float(args[4]), 0.8, float(args[4])),
        "Левое бедро": (float(args[4]), 0.8, float(args[4])),
        "Талия": (float(args[3]), 1, float(args[3]))
    }
    
    for bone_name, scale in bones_to_scale.items():
        pose_bone = armature.pose.bones.get(bone_name)
        if pose_bone:
            pose_bone.scale = scale
    
    bpy.ops.object.mode_set(mode='OBJECT')


# ===== ЗАПУСК =====
setup_lighting()
setup_camera(output_path)
setup_render_quality()

# ===== РЕНДЕР =====
if scene.camera:
    bpy.ops.render.render(animation=True)
else:
    print("Ошибка: Камера не назначена!")
