import datetime
import time
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
import os
import gradio as gr

import concurrent.futures

import logging

logging.basicConfig(level=logging.DEBUG)


class ImageProcessor:

    def __init__(self):
        self.input_dir = ""

        self.output_images = []
        self.page_number = 0

        self.config = {
            'quality': 80,
            'is_resize': True,
            'max_width': 3000,
            'max_height': 3000,
        }

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

    def convert_to_optimized_jpeg(self, input_path, output_path):

        img = Image.open(input_path)

        if self.config['is_resize']:
            img = self.resize_image(img, self.config['max_width'], self.config['max_height'])

        fill_color = (0, 0, 0)
        if input_path.endswith('.png'):
            img = self.png_add_background(img, fill_color)

        img.save(
            output_path,
            'jpeg',
            quality=self.config['quality'],
            optimize=True,
        )

        img.close()

    def convert(self, dir, quality, is_resize, max_width, max_height, progress=gr.Progress()):

        self.input_dir = dir

        if not os.path.exists(self.input_dir):
            return
            # os.makedirs(output_dir)

        input_dir = Path(self.input_dir)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        output_dir = input_dir / f"out/{now_time}/"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_images = []

        images_inout = []

        self.config['quality'] = quality
        self.config['is_resize'] = is_resize
        self.config['max_width'] = max_width
        self.config['max_height'] = max_height

        for filename in os.listdir(input_dir):

            if not filename.endswith('.jpg') and not filename.endswith('.jpeg') and not filename.endswith('.png'):
                continue

            input_img_dir = os.path.join(input_dir, filename)
            new_filename = filename.replace('.png', '.jpg')
            output_img_dir = os.path.join(output_dir, new_filename)

            images_inout.append([input_img_dir, output_img_dir])

        completed = 0
        progress((0, len(images_inout)), desc="Starting")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.convert_to_optimized_jpeg, source, target) for [source, target] in
                       images_inout]
            for _ in concurrent.futures.as_completed(futures):
                completed = completed + 1
                progress((completed, len(futures)), desc=f"Processing")

        self.output_images = [image_inout[1] for image_inout in images_inout]
        self.page_number = 0

        return self.update_page('slider', 0)

    def get_page(self):
        start_index = self.page_number * 12
        end_index = start_index + 12
        return self.output_images[start_index:end_index]

    def prev_page(self):
        return self.update_page('prev', 0)

    def next_page(self):
        return self.update_page('next', 0)

    def slider_page(self, page_number):
        return self.update_page('slider', page_number)

    def update_page(self, type, page_number):

        total_page = len(self.output_images) // 12 + 1

        if type == 'prev':
            self.page_number = self.page_number - 1
        elif type == 'next':
            self.page_number = self.page_number + 1
        elif type == 'slider':
            if 0 <= page_number < total_page:
                self.page_number = page_number

        is_prev_disable = self.page_number == 0
        is_next_disable = self.page_number == total_page - 1

        return gr.update(interactive=not is_prev_disable), gr.update(value=self.page_number, maximum=total_page - 1,
                                                                     interactive=not is_prev_disable or not is_next_disable), gr.update(
            interactive=not is_next_disable), self.get_page()

    def start_ui(self):

        with gr.Blocks(css="#slider .default {display: none;}") as demo:
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
                    with gr.Row():
                        quality = gr.Slider(
                            label="质量",
                            value=self.config['quality'],
                            precision=0,
                        )
                    with gr.Row():
                        is_resize = gr.Checkbox(
                            label="是否缩放",
                            value=self.config['is_resize'],
                        )
                        max_width = gr.Number(
                            label="最大宽度",
                            value=self.config['max_width'],
                            precision=0,
                        )
                        max_height = gr.Number(
                            label="最大高度",
                            value=self.config['max_height'],
                            precision=0,
                        )
                    submit_btn = gr.Button(
                        "处理",
                        variant="primary"
                    )
                with gr.Column(min_width=600):
                    with gr.Row():
                        prev_btn = gr.Button(
                            "上一页",
                            interactive=False,
                        )
                        prev_btn.style(
                            size='sm'
                        )
                        page_number = gr.Slider(
                            label="页数",
                            elem_id='slider',
                            interactive=False,
                        )
                        next_btn = gr.Button(
                            "下一页",
                            interactive=False,
                        )

                    output = gr.Gallery(
                        show_label=False,
                    )
                    output.style(
                        grid=4,
                    )

            outputs = [
                prev_btn,
                page_number,
                next_btn,
                output,
            ]

            prev_btn.click(
                fn=self.prev_page,
                inputs=[],
                outputs=outputs,
                show_progress=False,
            )
            page_number.release(
                fn=self.slider_page,
                inputs=[
                    page_number,
                ],
                outputs=outputs,
                show_progress=False,
            )
            next_btn.click(
                fn=self.next_page,
                inputs=[],
                outputs=outputs,
                show_progress=False,
            )

            submit_btn.click(
                fn=self.convert,
                inputs=[
                    dir, quality, is_resize, max_width, max_height
                ],
                outputs=outputs,
                queue=True
            )

        demo.queue()
        demo.launch(
            server_name="0.0.0.0",
            inbrowser=True,
            debug=True,
            enable_queue=True,
            prevent_thread_lock=True,
            show_error=True
        )


input_dir = r'C:\Users\12727\Downloads\selected\grid-0000.png'
output_dir = r'C:\Users\12727\Downloads\selected\grid-0000.jpg'

if __name__ == '__main__':
    process = ImageProcessor()
    process.start_ui()
    # process.convert_to_optimized_jpeg(input_dir, output_dir)
