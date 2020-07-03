import os


def generate_propic_upload_location(instance, filename):
    _, ext = os.path.splitext(filename)
    return f'profile_pictures/{instance.username}/propic{ext}'


def generate_cv_upload_location(instance, filename):
    _, ext = os.path.splitext(filename)
    return f'cvs/{instance.username}/cv{ext}'
