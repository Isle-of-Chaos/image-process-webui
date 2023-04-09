import datetime
from pathlib import Path

from PIL import Image
import os
import gradio as gr


class ImageProcessor:

    def __init__(self):
        self.input_dir = ""

    def png_add_background(self, img, fill_color):
        img = img.convert("RGBA")  # it had mode P after DL it from OP
        if img.mode in ('RGBA', 'LA'):
            background = Image.new(img.mode[:-1], img.size, fill_color)
            background.paste(img, img.split()[-1])  # omit transparency
            img = background

            img.convert("RGB")

        return img

    def resize_image(self, img, max_width, max_height):

        # 计算比例
        width, height = img.size
        ratio = min(max_width / width, max_height / height)

        # 缩放图片
        if ratio < 1:
            img = img.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)

        print(img.size)
        return img

    def png_to_jpg(self, dir):

        self.input_dir = dir

        if not os.path.exists(self.input_dir):
            return
            # os.makedirs(output_dir)

        input_dir = Path(self.input_dir)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        output_dir = input_dir / f"out/{now_time}/"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_images = []

        for filename in os.listdir(input_dir):

            if not filename.endswith('.jpg') and not filename.endswith('.jpeg') and not filename.endswith('.png'):
                continue

            img = Image.open(os.path.join(input_dir, filename))

            fill_color = (0, 0, 0)  # your new background color

            if filename.endswith('.png'):
                img = self.png_add_background(img, fill_color)

            img = self.resize_image(img, 3000, 3000)

            new_filename = filename.replace('.png', '.jpg')

            output_filename = os.path.join(output_dir, new_filename)
            img.save(output_filename, 'jpeg')
            output_images.append(output_filename)

            img.close()

        return output_images


    def start_ui(self):

        with gr.Blocks() as demo:
            gr.Markdown(
                """
            # 图片压缩
            """)


            with gr.Row():
                with gr.Column():
                    dir = gr.Textbox(
                        label="本地图片文件夹路径",
                        interactive=True,
                    )
                    submit_btn = gr.Button(
                        label="处理",
                        variant="primary"
                    )
                with gr.Column():
                    output = gr.Gallery(
                        show_label=False,
                    )
                    output.style(
                        grid=4,
                    )

            submit_btn.click(
                fn=self.png_to_jpg,
                inputs=[
                    dir
                ],
                outputs=output
            )

        demo.launch(
            server_name="0.0.0.0",
        )




input_dir = r'/Users/ciaochaos/Downloads/test_images'

if __name__ == '__main__':
    process = ImageProcessor()
    process.start_ui()

# from io import BytesIO
#
# from PIL import Image  # pip install pillow
# import mozjpeg_lossless_optimization
#
#
# def convert_to_optimized_jpeg(input_path, output_path):
#     jpeg_io = BytesIO()
#
#     with Image.open(input_path, "r") as image:
#         image.convert("RGB").save(jpeg_io, format="JPEG", quality=90)
#
#     jpeg_io.seek(0)
#     jpeg_bytes = jpeg_io.read()
#
#     optimized_jpeg_bytes = mozjpeg_lossless_optimization.optimize(jpeg_bytes)
#
#     with open(output_path, "wb") as output_file:
#         output_file.write(optimized_jpeg_bytes)
#
#
# convert_to_optimized_jpeg("input.png", "optimized.jpg")