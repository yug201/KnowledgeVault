from imagekitio import ImageKit

from app.core.config import (
    IMAGEKIT_PRIVATE_KEY,
)


imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY
)


async def upload_file(
    file_data: bytes,
    file_name: str
):
    response = imagekit.files.upload(
        file=file_data,
        file_name=file_name
    )

    return response