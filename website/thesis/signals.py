import os


def generate_and_save_hash(sender, instance, **kwargs):
    if not instance.md5hash:
        h = instance.generate_hash()
        instance.md5hash = h
        instance.save()


def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
