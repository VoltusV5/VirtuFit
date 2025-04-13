import bpy
import math
import os
import sys
from mathutils import Vector

def clear_scene():
    """Очищает сцену от всех объектов"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def load_asset(filepath, asset_type):
    """Загружает 3D модель или изображение"""
    try:
        if asset_type == 'model':
            # Выбор импортера в зависимости от формата
            file_ext = filepath.lower().split('.')[-1]
            if file_ext == 'obj':
                bpy.ops.import_scene.obj(filepath=filepath)
            elif file_ext == 'fbx':
                bpy.ops.import_scene.fbx(filepath=filepath)
            elif file_ext in ['glb', 'gltf']:
                bpy.ops.import_scene.gltf(filepath=filepath)
            return bpy.context.selected_objects[0]
            
        elif asset_type == 'texture':
            return bpy.data.images.load(filepath)
            
    except Exception as e:
        print(f"Ошибка загрузки {asset_type}: {str(e)}")
        return None

def setup_clothing_texture(image_path):
    """Создаёт плоскость с текстурой одежды"""
    try:
        # Создание плоскости и материала
        bpy.ops.mesh.primitive_plane_add(size=2)
        plane = bpy.context.object
        plane.name = "Clothing_Plane"
        
        # Настройка материала
        mat = bpy.data.materials.new(name="Clothing_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Очистка стандартных нод
        nodes.clear()
        
        # Создание нод
        tex_image = nodes.new('ShaderNodeTexImage')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        output = nodes.new('ShaderNodeOutputMaterial')
        
        # Загрузка изображения
        tex_image.image = load_asset(image_path, 'texture')
        
        # Соединение нод
        links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
        links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])
        
        # Применение материала
        plane.data.materials.append(mat)
        
        # Позиционирование
        plane.location.z = -1
        plane.rotation_euler.x = math.radians(90)
        plane.hide_render = False
        
        return plane
    except Exception as e:
        print(f"Ошибка создания текстуры: {str(e)}")
        return None

class FirstPersonOrbiter:
    def __init__(
        self,
        target_object,
        camera_name: str = "Camera",
        radius: float = 5.0,
        duration: float = 5.0,
        height_offset: float = 1.6,
        fps: int = 15,
        output_path: str = "//render_output.mp4",
        resolution: tuple = (1920, 1080)
    ):
        self.target = target_object
        self.camera_name = camera_name
        self.radius = radius
        self.duration = duration
        self.height_offset = height_offset
        self.fps = fps
        self.output_path = output_path
        self.resolution = resolution

        self.scene = bpy.context.scene
        self.camera = self.setup_camera()

        # Настройка временной шкалы
        self.scene.frame_start = 1
        self.scene.frame_end = int(duration * fps)
        self.scene.render.fps = fps

    def setup_camera(self) -> bpy.types.Object:
        """Создаёт и настраивает камеру"""
        # Создание или получение камеры
        if self.camera_name in bpy.data.objects:
            camera = bpy.data.objects[self.camera_name]
        else:
            bpy.ops.object.camera_add()
            camera = bpy.context.object
            camera.name = self.camera_name
        
        # Начальная позиция
        camera.location = (self.radius, 0, self.height_offset)
        camera.rotation_mode = 'XYZ'
        self.look_at_target(camera)
        
        # Настройки камеры
        camera.data.lens = 35
        camera.data.clip_start = 0.1
        camera.data.clip_end = 1000
        
        return camera

    def look_at_target(self, camera: bpy.types.Object) -> None:
        """Направляет камеру на цель"""
        if not self.target:
            return
        
        # Расчет ориентации
        direction = self.target.location - camera.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        camera.rotation_euler = rot_quat.to_euler()

    def calculate_orbit_position(self, angle: float) -> tuple:
        """Рассчитывает позицию на орбите"""
        x = math.cos(angle) * self.radius
        y = math.sin(angle) * self.radius
        return (x, y, self.height_offset)

    def animate(self) -> None:
        """Создаёт анимацию движения"""
        if not self.target:
            print("Цель не найдена!")
            return

        # Очистка предыдущей анимации
        self.camera.animation_data_clear()

        # Создание ключевых кадров
        for frame in range(self.scene.frame_start, self.scene.frame_end + 1):
            self.scene.frame_set(frame)
            progress = (frame - 1) / (self.scene.frame_end - 1)
            angle = progress * 2 * math.pi
            
            # Обновление позиции и поворота
            self.camera.location = self.calculate_orbit_position(angle)
            self.look_at_target(self.camera)
            
            # Вставка ключевых кадров
            self.camera.keyframe_insert(data_path="location", frame=frame)
            self.camera.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Настройка интерполяции
        self.set_smooth_interpolation()

    def set_smooth_interpolation(self) -> None:
        """Плавная интерполяция анимации"""
        if not self.camera.animation_data:
            return
            
        for fcurve in self.camera.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO'
                kp.handle_right_type = 'AUTO'

    def setup_render_settings(self):
        """Настройки рендеринга"""
        # Формат вывода
        self.scene.render.image_settings.file_format = 'FFMPEG'
        self.scene.render.ffmpeg.format = 'MPEG4'
        self.scene.render.ffmpeg.codec = 'H264'
        self.scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
        
        # Разрешение и качество
        self.scene.render.resolution_x = self.resolution[0]
        self.scene.render.resolution_y = self.resolution[1]
        self.scene.render.resolution_percentage = 100
        self.scene.render.film_transparent = False
        
        # Путь сохранения
        self.scene.render.filepath = bpy.path.abspath(self.output_path)

    def render_animation(self):
        """Запуск рендеринга"""
        print(f"Рендеринг начат, результат будет сохранён в: {self.scene.render.filepath}")
        bpy.ops.render.render(animation=True)

    def run(self):
        """Основной цикл выполнения"""
        self.animate()
        self.setup_render_settings()
        self.render_animation()
        print("Рендеринг успешно завершён!")

if __name__ == "__main__":
    # Инициализация путей
    base_dir = os.path.dirname(bpy.data.filepath)
    models_dir = os.path.join(base_dir, "models")
    photos_dir = os.path.join(base_dir, "photos")
    
    # Очистка сцены
    clear_scene()
    
    # Загрузка модели
    model = None
    if os.path.exists(models_dir):
        for f in sorted(os.listdir(models_dir)):
            filepath = os.path.join(models_dir, f)
            if os.path.isfile(filepath):
                model = load_asset(filepath, 'model')
                if model:
                    model.name = "Main_Model"
                    model.location = (0, 0, 0)
                    break

    # Создание куба по умолчанию
    if not model:
        bpy.ops.mesh.primitive_cube_add(size=2)
        model = bpy.context.object
        model.name = "Default_Cube"
    
    # Загрузка текстуры одежды
    if os.path.exists(photos_dir)):
        for f in sorted(os.listdir(photos_dir)):
            filepath = os.path.join(photos_dir, f)
            if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
                if setup_clothing_texture(filepath):
                    break
    
    # Настройка освещения
    bpy.ops.object.light_add(type='AREA', radius=3, location=(2, -2, 5))
    light = bpy.context.object
    light.data.energy = 750
    light.data.diffuse_factor = 1.5
    
    # Получение пути вывода
    try:
        output_path = sys.argv[sys.argv.index("--") + 1]
    except (ValueError, IndexError):
        output_path = os.path.join(base_dir, "render_output.mp4")
    
    # Запуск системы
    fp_orbit = FirstPersonOrbiter(
        target_object=model,
        radius=8.0,
        duration=5.0,
        height_offset=1.6,
        resolution=(1280, 720),
        output_path=output_path
    )
    fp_orbit.run()