def cleanup_old_images():
    from django.conf import settings
    import os
    import glob
    import time

    media_root = settings.MEDIA_ROOT
    image_pattern = os.path.join(media_root, "*.png")

    for image_file in glob.glob(image_pattern):
        if os.path.getmtime(image_file) < time.time() - 3600:
            os.remove(image_file)
