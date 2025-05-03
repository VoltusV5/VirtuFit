import bpy
import math
from mathutils import Vector
import os


def import_model():
    """Импортирует модель и применяет текстуру, возвращает имя объекта"""
    # Удаляем все существующие объекты
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Пути к файлам (проверьте пути!)
    obj_path = r"D:\project\VirtuFit\models\mesh.obj"
    texture_path = r"D:\project\VirtuFit\textures\texture.png"

    if not all(os.path.exists(p) for p in [obj_path, texture_path]):
        raise FileNotFoundError("Файлы не найдены!")

    # Импорт модели
    try:
        bpy.ops.import_scene.obj(filepath=obj_path)
    except Exception as e:
        raise RuntimeError(f"Ошибка импорта: {str(e)}") from e

    # Получаем импортированный объект
    obj = next((o for o in bpy.context.selected_objects if o.type == 'MESH'), None)
    if not obj:
        raise RuntimeError("Объект не найден!")
    obj.name = "ImportedModel"  # Переименовываем для удобства

    # Создаем материал с текстурой
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

    # Применяем материал
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Развертка UV
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"Модель '{obj.name}' готова!")
    return obj.name




class FirstPersonOrbiter:
    def __init__(
        self,
        target_name: str = "Cube",
        camera_name: str = "Camera",
        radius: float = 5.0,
        duration: float = 5.0,
        height_offset: float = 1.6,
        fps: int = 15,
        output_path: str = "//render_output.mp4",
        resolution: tuple = (1920, 1080)
    ):
        self.target_name = target_name
        self.camera_name = camera_name
        self.radius = radius
        self.duration = duration
        self.height_offset = height_offset
        self.fps = fps
        self.output_path = output_path
        self.resolution = resolution

        self.scene = bpy.context.scene
        self.target = bpy.data.objects.get(target_name)
        self.camera = self.setup_camera()

        # Настройка временной шкалы
        self.scene.frame_start = 1
        self.scene.frame_end = int(duration * fps)
        self.scene.render.fps = fps

    def setup_camera(self) -> bpy.types.Object:
        """Создаёт и настраивает камеру для первого лица"""
        if self.camera_name in bpy.data.objects:
            camera = bpy.data.objects[self.camera_name]
        else:
            bpy.ops.object.camera_add()
            camera = bpy.context.object
            camera.name = self.camera_name
        
        # Первоначальная позиция (сбоку от цели)
        camera.location = (self.radius, 0, self.height_offset)
        camera.rotation_mode = 'XYZ'
        
        # Направляем камеру на цель
        self.look_at_target(camera)
        return camera

    def look_at_target(self, camera: bpy.types.Object) -> None:
        """Рассчитывает поворот камеры для направления на цель"""
        if not self.target:
            return
        
        # Вектор от камеры к цели
        direction = self.target.location - camera.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        
        # Применяем поворот
        camera.rotation_euler = rot_quat.to_euler()

    def calculate_orbit_position(self, angle: float) -> tuple:
        """Рассчитывает позицию на круговой орбите с высотой"""
        x = math.cos(angle) * self.radius
        y = math.sin(angle) * self.radius
        return (x, y, self.height_offset)

    def animate(self) -> None:
        """Создаёт анимацию с плавным движением"""
        if not self.target:
            print(f"Цель '{self.target_name}' не найдена!")
            return

        # Очистка предыдущей анимации
        self.camera.animation_data_clear()

        # Рассчитываем ключевые кадры
        for frame in range(self.scene.frame_start, self.scene.frame_end + 1):
            self.scene.frame_set(frame)
            progress = (frame - 1) / (self.scene.frame_end - 1)
            angle = progress * 2 * math.pi
            
            # Новая позиция камеры
            self.camera.location = self.calculate_orbit_position(angle)
            
            # Поворот камеры для слежения за целью
            self.look_at_target(self.camera)
            
            # Вставка ключевых кадров
            self.camera.keyframe_insert(data_path="location", frame=frame)
            self.camera.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Настройка плавности анимации
        self.set_smooth_interpolation()

    def set_smooth_interpolation(self) -> None:
        """Настраивает плавную интерполяцию ключевых кадров"""
        if not self.camera.animation_data:
            return
            
        for fcurve in self.camera.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO'
                kp.handle_right_type = 'AUTO'

    def setup_render_settings(self):
        """Настраивает параметры рендеринга"""
        # Формат вывода
        self.scene.render.image_settings.file_format = 'FFMPEG'
        self.scene.render.ffmpeg.format = 'MPEG4'
        self.scene.render.ffmpeg.codec = 'H264'
        
        # Разрешение
        self.scene.render.resolution_x = self.resolution[0]
        self.scene.render.resolution_y = self.resolution[1]
        # Добавляем настройки рендера
        self.scene.render.engine = 'CYCLES'
        self.scene.cycles.samples = 64
        self.scene.cycles.device = 'CPU'
        self.scene.render.threads_mode = 'AUTO'
        self.scene.render.threads = 12
        self.scene.render.use_persistent_data = False
        
        # Путь сохранения (исправлено преобразование пути)
        self.scene.render.filepath = bpy.path.abspath(self.output_path)

    def render_animation(self):
        """Выполняет рендеринг анимации"""
        print(f"Начинаем рендеринг в: {self.scene.render.filepath}")
        bpy.ops.render.render(animation=True)

    def run(self):
        """Запускает систему"""
        self.animate()
        self.setup_render_settings()
        self.render_animation()
        print("Рендеринг завершен!")




# if __name__ == "__main__":
#     import sys
#     # Получаем путь для сохранения из аргументов
#     # try:
#     #     args = sys.argv[sys.argv.index("--") + 1:]
#     #     output_path = args[0]
#     # except:
#     output_path = r"D:\project\VirtuFit\video\render_output.mp4"

#     # Импортируем модель
#     try:
#         model_name = import_model()
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         sys.exit(1)

#     # Настраиваем и запускаем анимацию
#     fp_orbit = FirstPersonOrbiter(
#         target_name=model_name,
#         output_path=output_path,
#         radius=8.0,
#         duration=5.0,
#         height_offset=1.6,
#         resolution=(1280, 720)
#     )
#     fp_orbit.run()





# if __name__ == "__main__":
    
#     import sys
    
#     # Получаем путь для сохранения из аргументов
#     try:
#         args = sys.argv[sys.argv.index("--") + 1:]
#         output_path = args[0]
#     except:
#         output_path = "//default_output.mp4"

#     # Очистка предыдущей анимации
#     if "Camera" in bpy.data.objects:
#         camera = bpy.data.objects["Camera"]
#         camera.animation_data_clear()

#     # Создаем цель при необходимости
#     if "Cube" not in bpy.data.objects:
#         bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), size=2)
    
#     # Запускаем орбитер
#     fp_orbit = FirstPersonOrbiter(
#         output_path=output_path,
#         radius=8.0,
#         duration=5.0,
#         height_offset=1.6,
#         resolution=(1280, 720)
#     )
#     fp_orbit.run()