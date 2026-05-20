import os
import zipfile
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import ffmpeg
import imageio_ffmpeg
from PyPDF2 import PdfReader, PdfWriter

def get_ffmpeg_path():
    """Returns the path to the ffmpeg binary provided by imageio-ffmpeg."""
    return imageio_ffmpeg.get_ffmpeg_exe()

def compress_image(file, filename):
    """
    Compresses an image using Pillow.
    Converts to WEBP or optimized JPEG.
    """
    try:
        img = Image.open(file)
        # Convert RGBA to RGB if saving as JPEG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        output_io = BytesIO()
        ext = filename.split('.')[-1].lower()
        new_filename = f"{uuid.uuid4().hex[:8]}_compressed.webp"
        
        # Save as optimized WebP for best compression
        img.save(output_io, format='WEBP', quality=70, optimize=True)
        output_io.seek(0)
        return ContentFile(output_io.read(), name=new_filename)
    except Exception as e:
        print(f"Image compression error: {e}")
        return None

def compress_video(input_path, output_path):
    """
    Compresses a video using ffmpeg-python and the imageio_ffmpeg binary.
    Reduces bitrate and uses H.264.
    """
    try:
        ffmpeg_cmd = get_ffmpeg_path()
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=28, preset='fast', acodec='aac')
        ffmpeg.run(stream, cmd=ffmpeg_cmd, overwrite_output=True, quiet=True)
        return True
    except Exception as e:
        print(f"Video compression error: {e}")
        return False

def compress_pdf(input_path, output_path):
    """
    Compresses a PDF using PyPDF2 by removing duplication and compressing streams.
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
        return True
    except Exception as e:
        print(f"PDF compression error: {e}")
        return False

def compress_generic(input_path, output_path):
    """
    Compresses generic files into a ZIP archive with ZIP_DEFLATED.
    """
    try:
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            zipf.write(input_path, arcname=os.path.basename(input_path))
        return True
    except Exception as e:
        print(f"Generic compression error: {e}")
        return False
