let scene, camera, renderer, model;

function init3DViewer() {
    // 1. Создаем сцену
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    
    // 2. Настраиваем камеру
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;
    
    // 3. Создаем рендерер
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(document.getElementById('model-container').clientWidth, 
                    document.getElementById('model-container').clientHeight);
    document.getElementById('model-container').appendChild(renderer.domElement);
    
    // 4. Добавляем освещение
    const light = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(light);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 1, 1);
    scene.add(directionalLight);
    
    // 5. Добавляем OrbitControls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    // 6. Загрузка модели
    const loader = new THREE.GLTFLoader();
    loader.load(
        '/static/models/your-model.gltf', // Путь к вашей модели
        function (gltf) {
            model = gltf.scene;
            scene.add(model);
            
            // Центрируем модель
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            model.position.sub(center);
        },
        undefined,
        function (error) {
            console.error('Ошибка загрузки модели:', error);
        }
    );
    
    // 7. Анимация
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
    
    // 8. Реакция на изменение размера окна
    window.addEventListener('resize', function() {
        camera.aspect = document.getElementById('model-container').clientWidth / 
                        document.getElementById('model-container').clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(document.getElementById('model-container').clientWidth, 
                        document.getElementById('model-container').clientHeight);
    });
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', init3DViewer);