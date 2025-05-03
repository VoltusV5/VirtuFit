import bpy
import os
import math

def import_model(output_path):
    # Очистка сцены
    bpy.ops.wm.read_homefile(use_empty=True)

    # Пути к файлам
    obj_path = r"D:\project\VirtuFit\models\mesh.obj"
    texture_path = r"D:\project\VirtuFit\textures\texture.png"

    # Проверка существования файлов
    if not all(os.path.exists(p) for p in [obj_path, texture_path]):
        raise FileNotFoundError("Файлы не найдены!")

    # Функция для получения контекста 3D View
    def get_context():
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    return {
                        'window': window,
                        'screen': window.screen,
                        'area': area,
                        'region': area.regions[-1]
                    }
        raise RuntimeError("3D View не найдена!")

    # Импорт модели
    try:
        ctx = get_context()
        with bpy.context.temp_override(**ctx):
            bpy.ops.wm.obj_import(
                filepath=obj_path,
                global_scale=1.0,
                forward_axis='NEGATIVE_Z',
                up_axis='Y'
            )
    except Exception as e:
        raise RuntimeError(f"Ошибка импорта: {str(e)}") from e

    # Получение объекта
    obj = next((o for o in bpy.data.objects if o.select_get()), None)
    if not obj:
        raise RuntimeError("Объект не найден!")

    # Создание и настройка материала
    mat = bpy.data.materials.new(name="TextureMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    tex_image = nodes.new('ShaderNodeTexImage')
    tex_image.image = bpy.data.images.load(texture_path)

    links = mat.node_tree.links
    links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Применение материала
    obj.data.materials.clear()
    obj.data.materials.append(mat)

    # Развертка UV
    with bpy.context.temp_override(**ctx):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

    print(f"Успех! Текстура применена к {obj.name}")

    # Настройка освещения
    light_data = bpy.data.lights.new(name="MainLight", type='POINT')
    light = bpy.data.objects.new(name="MainLight", object_data=light_data)
    light.location = (3, -3, 5)
    light.data.energy = 500.0
    bpy.context.collection.objects.link(light)

    # Создание пустого объекта для вращения камеры
    empty = bpy.data.objects.new("CameraTarget", None)
    empty.location = obj.location
    bpy.context.collection.objects.link(empty)

    # Создание и настройка камеры
    cam_data = bpy.data.cameras.new("MainCamera")
    cam = bpy.data.objects.new("MainCamera", cam_data)
    cam.location = (0, -5, 3)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Добавление трекинга к пустому объекту
    track_constraint = cam.constraints.new(type='TRACK_TO')
    track_constraint.target = empty
    track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    track_constraint.up_axis = 'UP_Y'

    # Анимация вращения камеры
    cam.parent = empty
    empty.rotation_euler = (0, 0, 0)
    empty.keyframe_insert(data_path="rotation_euler", frame=1)

    empty.rotation_euler = (0, 0, math.radians(360))
    empty.keyframe_insert(data_path="rotation_euler", frame=120)

    # Настройки рендеринга
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120  # 5 секунд при 24 FPS

    # Настройка фона (вариант 1 — серый)
    world = bpy.context.scene.world

    # Если мира нет - создаем новый
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    # Включаем ноды только если они еще не включены
    if not world.use_nodes:
        world.use_nodes = True

    # Получаем нод Background (он создается автоматически при use_nodes=True)
    bg = world.node_tree.nodes.get('Background')
    if bg is None:
        bg = world.node_tree.nodes.new('ShaderNodeBackground')

    # Устанавливаем цвет и силу фона
    bg.inputs[0].default_value = (0.9, 0.9, 0.9, 1)  # RGB + Alpha
    bg.inputs[1].default_value = 1.0  # Сила освещения
    
    bpy.context.scene.render.filepath = output_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Рендеринг анимации
    bpy.ops.render.render(animation=True)

    print(f"Видео сохранено: {output_path}")

if __name__ == "__main__":
    import sys
    #Получаем путь для сохранения из аргументов
    try:
        args = sys.argv[sys.argv.index("--") + 1:]
        output_path = args[0]
    except:
        output_path = r"D:\project\VirtuFit\video\render_output.mp4"
    import_model(output_path)