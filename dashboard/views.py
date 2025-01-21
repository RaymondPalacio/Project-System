import base64
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.utils.timezone import now

# Dashboard view to render the camera page
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

# Camera dashboard view
def camera_dashboard(request):
    return render(request, 'dashboard/camera_dashboard.html') 

# View to handle image capture and upload
@csrf_exempt  # Disable CSRF for this view (use caution in production)
def save_image(request):
    if request.method == 'POST':
        # Check if the image is captured from the camera
        if 'image' in request.body.decode('utf-8'):
            data = request.body.decode('utf-8')  # Get the image data
            image_data = data.split(',')[1]  # Strip out the metadata part
            image_file = ContentFile(base64.b64decode(image_data), name=f"{now().strftime('%Y%m%d%H%M%S')}.png")

            # Define the path where the image will be saved
            save_path = os.path.join(settings.MEDIA_ROOT, 'captured_images', image_file.name)

            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the image
            with open(save_path, 'wb') as f:
                f.write(image_file.read())

            # Return success response with the image file name
            return JsonResponse({'message': 'Captured image saved successfully', 'filename': image_file.name})

        # Check if the image is uploaded via the form
        elif 'imageUpload' in request.FILES:
            uploaded_image = request.FILES['imageUpload']
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images', uploaded_image.name)

            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the uploaded image
            with open(save_path, 'wb') as f:
                for chunk in uploaded_image.chunks():
                    f.write(chunk)

            # Return success response with the uploaded image file name
            return JsonResponse({'message': 'Uploaded image saved successfully', 'filename': uploaded_image.name})

    return JsonResponse({'message': 'Invalid request'}, status=400)
