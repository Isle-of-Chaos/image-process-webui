from io import BytesIO

from PIL import Image  # pip install pillow
import mozjpeg_lossless_optimization

import concurrent.futures


def convert_to_optimized_jpeg(input_path, output_path):
    jpeg_io = BytesIO()

    with Image.open(input_path, "r") as image:
        image.convert("RGB").save(jpeg_io, format="JPEG", quality=90)

    jpeg_io.seek(0)
    jpeg_bytes = jpeg_io.read()

    optimized_jpeg_bytes = mozjpeg_lossless_optimization.optimize(jpeg_bytes)

    with open(output_path, "wb") as output_file:
        output_file.write(optimized_jpeg_bytes)



if __name__ == '__main__':
    images = [["/home/cpunisher/Image/" + str(i) + ".jpg", "./target/optimized" + str(i) + ".jpg"] for i in range(1, 11)];
    # 单进程，单线程
    # for [source, target] in images:
    #     convert_to_optimized_jpeg(source, target)

    # 多进程
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     for [source, target] in images:
    #         executor.submit(convert_to_optimized_jpeg, source, target)

    # 多线程
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for [source, target] in images:
            executor.submit(convert_to_optimized_jpeg, source, target)
