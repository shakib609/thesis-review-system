def generate_and_save_hash(sender, instance, **kwargs):
    if not instance.md5hash:
        h = instance.generate_hash()
        instance.md5hash = h
        instance.save()
