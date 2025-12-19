from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uuid
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
import random
import string
import os

app = FastAPI(title="Image Rotation App - Вариант 6")

# Настройка статических файлов и шаблонов
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Директории
UPLOAD_DIR = Path("../uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR = Path("../results")
RESULTS_DIR.mkdir(exist_ok=True)

sessions = {}

# ========== CAPTCHA ==========
def generate_captcha():
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    width, height = 200, 80
    image = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)

    for _ in range(1000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(100,200), random.randint(100,200), random.randint(100,200)))

    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    for i, char in enumerate(text):
        x = 20 + i*30 + random.randint(-5,5)
        y = 20 + random.randint(-10,10)
        draw.text((x, y), char, font=font, fill=(random.randint(0,100),random.randint(0,100),random.randint(0,100)))

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return text, f"data:image/png;base64,{img_str}"

def verify_captcha(user_input: str, captcha_text: str) -> bool:
    return user_input.strip().upper() == captcha_text.upper()

# ========== IMAGE PROCESSING ==========
def rotate_image(input_path: str, output_path: str, angle: float):
    with Image.open(input_path) as img:
        if img.mode in ('RGBA','LA','P'):
            rgb_img = Image.new('RGB', img.size, (255,255,255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode=='RGBA' else None)
            img = rgb_img
        rotated = img.rotate(angle, expand=True, fillcolor=(255,255,255))
        rotated.save(output_path, "JPEG")
    return output_path

def generate_color_histogram(image_path: str):
    """Гистограмма для изображения"""
    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)

        fig, axes = plt.subplots(1,3, figsize=(18,6))  # крупная фигура
        colors = ['red','green','blue']
        names = ['Красный','Зелёный','Синий']

        for i, color in enumerate(colors):
            axes[i].hist(img_array[:,:,i].ravel(), bins=256, color=color, alpha=0.7, density=True)
            axes[i].set_title(f'Канал {names[i]}')
            axes[i].set_xlim([0,256])
            axes[i].set_ylim([0,0.03])

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)  # высокое разрешение
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

# ========== ROUTES ==========
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    captcha_text, captcha_image = generate_captcha()
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"captcha": captcha_text}
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "session_id": session_id,
                                                     "captcha_image": captcha_image})

@app.post("/process")
async def process_image(request: Request,
                        session_id: str = Form(...),
                        captcha_input: str = Form(...),
                        angle: str = Form(...),
                        image: UploadFile = File(...)):
    try:
        angle_float = float(angle)
        if session_id not in sessions or not verify_captcha(captcha_input, sessions[session_id]["captcha"]):
            return JSONResponse({"error":"Неверная CAPTCHA"}, status_code=400)

        file_location = UPLOAD_DIR / f"{uuid.uuid4()}_{image.filename}"
        with open(file_location, "wb+") as f:
            content = await image.read()
            if not content:
                return JSONResponse({"error":"Пустой файл"}, status_code=400)
            f.write(content)

        try:
            with Image.open(file_location) as img:
                img.verify()
        except:
            file_location.unlink()
            return JSONResponse({"error":"Некорректный файл изображения"}, status_code=400)

        rotated_path = RESULTS_DIR / f"rotated_{file_location.name}"
        rotate_image(str(file_location), str(rotated_path), angle_float)

        # только оригинальная гистограмма
        original_hist = generate_color_histogram(str(file_location))

        file_location.unlink()

        return {
            "original_histogram": original_hist,
            "rotated_image": f"/results/{rotated_path.name}",
            "angle": angle_float,
            "filename": rotated_path.name
        }

    except ValueError:
        return JSONResponse({"error":"Неверный формат угла поворота"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error":f"Ошибка обработки: {str(e)}"}, status_code=500)

@app.get("/results/{filename}")
async def get_result(filename: str):
    file_path = RESULTS_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    return JSONResponse({"error":"Файл не найден"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
