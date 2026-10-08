import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "static/certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_certificate_image(recipient_name: str, course_name: str, output_path: str):
    width, height = 1200, 800
    image = Image.new("RGB", (width, height), color="#FAF7F2")
    draw = ImageDraw.Draw(image)

    # Decorative borders
    draw.rectangle([30, 30, width - 30, height - 30], outline="#1A365D", width=8)
    draw.rectangle([45, 45, width - 45, height - 45], outline="#C5A880", width=3)

    try:
        title_font = ImageFont.truetype("arial.ttf", 46)
        name_font = ImageFont.truetype("arial.ttf", 52)
        text_font = ImageFont.truetype("arial.ttf", 26)
    except IOError:
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    draw.text((width / 2, 170), "CERTIFICATE OF COMPLETION", fill="#1A365D", anchor="mm", font=title_font)
    draw.text((width / 2, 260), "This is proudly presented to", fill="#555555", anchor="mm", font=text_font)
    draw.text((width / 2, 360), recipient_name, fill="#0F172A", anchor="mm", font=name_font)
    draw.text((width / 2, 460), "for successfully completing the course:", fill="#555555", anchor="mm", font=text_font)
    draw.text((width / 2, 530), course_name, fill="#1E3A8A", anchor="mm", font=title_font)

    image.save(output_path, "PNG")