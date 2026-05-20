from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CompressedFile
from .utils import compress_image, compress_video, compress_pdf, compress_generic
from django.core.files.base import ContentFile
import os
import uuid
from django.conf import settings

def home(request):
    return render(request, 'compressor/index.html')

def image_compress(request):
    context = {'type': 'image', 'title': 'Rasm Siqish', 'accept': 'image/*'}
    return render(request, 'compressor/compress_page.html', context)

def video_compress(request):
    context = {'type': 'video', 'title': 'Video Siqish', 'accept': 'video/*'}
    return render(request, 'compressor/compress_page.html', context)

def file_compress(request):
    context = {'type': 'file', 'title': 'Fayl Siqish', 'accept': '.pdf,.zip,.docx,.txt,.xlsx'}
    return render(request, 'compressor/compress_page.html', context)

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        filename = file_obj.name
        ext = filename.split('.')[-1].lower()
        file_size = file_obj.size

        # Save original temporarily
        comp_file = CompressedFile.objects.create(
            original_file=file_obj,
            original_size=file_size,
            file_type=ext
        )

        input_path = comp_file.original_file.path
        
        # Decide compression based on extension
        image_exts = ['jpg', 'jpeg', 'png', 'webp', 'bmp']
        video_exts = ['mp4', 'avi', 'mov', 'mkv', 'webm']
        
        compressed = False
        new_filename = f"{uuid.uuid4().hex[:8]}_compressed"

        if ext in image_exts:
            compressed_content = compress_image(file_obj, filename)
            if compressed_content:
                output_filename = f"{new_filename}.webp"
                comp_file.compressed_file.save(output_filename, compressed_content, save=False)
                compressed = True
        
        else:
            # For non-images, we need an output path on disk
            media_compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
            os.makedirs(media_compressed_dir, exist_ok=True)
            
            if ext in video_exts:
                output_filename = f"{new_filename}.mp4"
                output_path = os.path.join(media_compressed_dir, output_filename)
                compressed = compress_video(input_path, output_path)
            
            elif ext == 'pdf':
                output_filename = f"{new_filename}.pdf"
                output_path = os.path.join(media_compressed_dir, output_filename)
                compressed = compress_pdf(input_path, output_path)
                
            else:
                output_filename = f"{new_filename}.zip"
                output_path = os.path.join(media_compressed_dir, output_filename)
                compressed = compress_generic(input_path, output_path)

            if compressed and os.path.exists(output_path):
                # Save the created file back to the model
                with open(output_path, 'rb') as f:
                    comp_file.compressed_file.save(output_filename, ContentFile(f.read()), save=False)
                os.remove(output_path) # Clean up temp compressed file

        if compressed and comp_file.compressed_file:
            comp_file.compressed_size = comp_file.compressed_file.size
            comp_file.save()

            return JsonResponse({
                'success': True,
                'original_size': comp_file.original_size,
                'compressed_size': comp_file.compressed_size,
                'savings_percentage': comp_file.savings_percentage,
                'download_url': comp_file.compressed_file.url,
                'filename': os.path.basename(comp_file.compressed_file.name)
            })
        else:
            comp_file.delete()
            return JsonResponse({'success': False, 'error': 'Compression failed.'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
