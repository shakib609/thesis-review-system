import os
from uuid import uuid4


def generate_upload_location(instance, filename):
    _, ext = os.path.splitext(filename)
    return f'{instance.unique_id}/{uuid4().hex[:10]}{ext}'
