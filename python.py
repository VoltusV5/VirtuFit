from fastapi import FastAPI
from fastapi.responses import FileResponse
import subprocess

app = FastAPI()

@app.get("") #сюда надо вписать, часть ссылки с фронта
async def edit_params(bosom: float, waist: float): #грудь, талия
    '''Функция которая принимает размеры и возвращает объект с изменёнными размерами'''



    blender_script = f"""
    import bpy
    import os

    # Масштабирование
    obj = bpy.data.objects['Body']
    obj.scale = ({bosom}, {waist})
    bpy.ops.object.transform_apply(scale=True)

    # Экспорт
    bpy.ops.export_scene.glb(
        filepath=os.path.join(os.getcwd(), 'result.glb'),
        export_format='GLB'
    )
    """

    with open("resize_script.py", "w") as f:
        f.write(blender_script)

    subprocess.run(
        [
        "blender", 
        "--background", 
        "Модели/Slender_Man_Lores.blend", 
        "--python", 
        "resize_script.py"
    ])
    
    return FileResponse("result.glb")

if __name__=="__main__":
    