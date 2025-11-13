import os
from tempfile import NamedTemporaryFile
from typing import Literal

import pillow_avif  # type: ignore
from PIL import Image


class _image:
    @staticmethod
    def to_jpg(
            image_file_path: str,
            /,
            jpg_file_path: str | None = None,
            quality: int = 100,
            keep_original: bool = False
    ) -> str | None:
        try:
            with open(image_file_path, "rb") as file:
                prefix_text = file.read(3).hex()
                n = 2
                file.seek(-n, 2)
                suffix_text = file.read(n).hex()
                text = prefix_text + suffix_text

            image_file_path = os.path.abspath(image_file_path)
            if jpg_file_path is not None:
                jpg_file_path = os.path.abspath(jpg_file_path)
            else:
                jpg_file_path = os.path.splitext(image_file_path)[0] + os.path.extsep + "jpg"

            if image_file_path == jpg_file_path and text == "ffd8ffffd9":
                return jpg_file_path

            jpg_dir_path = os.path.dirname(jpg_file_path)
            os.makedirs(jpg_dir_path, exist_ok=True)

            with Image.open(image_file_path) as image:
                if image.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode == "P":
                    image.seek(0)  # image.n_frames
                    image = image.convert("RGB")
                elif image.mode == "RGB":
                    pass
                else:
                    return None

                with NamedTemporaryFile(suffix=os.path.extsep + "jpg", delete=False, dir=jpg_dir_path) as ntf:
                    temp_file_path = ntf.name
                    image.save(temp_file_path, "JPEG", quality=quality)
                os.replace(temp_file_path, jpg_file_path)

            if not keep_original:
                from pathlib import Path
                if (p := Path(image_file_path)).exists() and str(p.resolve()) == str(p.absolute()):
                    os.remove(image_file_path)

            return jpg_file_path
        except Exception as e:  # noqa
            return None

    @staticmethod
    def concat(
            input_image_file_paths: list[str],
            output_image_file_path: str,
            orientation: Literal["vertical", "horizontal"] = "vertical",
            output_image_vertical_width: int | float | None = None,
            output_image_horizontal_height: int | float | None = None
    ) -> bool:
        try:
            input_images = [Image.open(i) for i in input_image_file_paths]

            if orientation == "vertical":
                if output_image_vertical_width is None:
                    output_image_vertical_width = min(i.width for i in input_images)

                resized_images = [
                    i.resize((output_image_vertical_width, int(i.height * output_image_vertical_width / i.width)))
                    for i in input_images
                ]

                output_image_height = sum(i.height for i in resized_images)

                output_image = Image.new("RGB", (output_image_vertical_width, output_image_height), "white")

                y_offset = 0
                for image in resized_images:
                    output_image.paste(image, (0, y_offset))
                    y_offset += image.height

                output_image.save(output_image_file_path)

            elif orientation == "horizontal":
                if output_image_horizontal_height is None:
                    output_image_horizontal_height = min(i.height for i in input_images)

                resized_images = [
                    i.resize((int(i.width * output_image_horizontal_height / i.height), output_image_horizontal_height))
                    for i in input_images
                ]

                output_image_width = sum(i.width for i in resized_images)

                output_image = Image.new("RGB", (output_image_width, output_image_horizontal_height), "white")

                x_offset = 0
                for image in resized_images:
                    output_image.paste(image, (x_offset, 0))
                    x_offset += image.width

                output_image.save(output_image_file_path)

            else:
                return False
        except Exception as e:  # noqa
            return False
        else:
            return True


__all__ = [
    "_image"
]
