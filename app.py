import os
from flask import Flask, render_template, request, jsonify
import json
from flask import send_from_directory
from datetime import datetime

app = Flask(__name__)

# Создаем папку data, если она не существует
if not os.path.exists('data'):
    os.makedirs('data')

DATA_DIR = "data"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start_screen():
    return render_template('start-screen.html')

# Получение данных из формы
@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()
        print("Получены данные:", data)
        
        # Проверка обязательных полей
        required_fields = ['gender', 'chest', 'waist', 'hips', 'shoulders', 'height']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Поле {field} обязательно"}), 400
        
        filename = f"data/user_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Данные успешно сохранены",
            "filename": filename
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/static/models/<path:filename>')
def serve_model(filename):
    return send_from_directory('static/models', filename)

if __name__ == '__main__':
    app.run(debug=True)