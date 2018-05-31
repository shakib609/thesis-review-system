from . import models


def remove_studentgroup_if_empty(sender, instance, **kwargs):
    if instance.id:
        old_user = models.User.objects.get(pk=instance.id)
        if old_user.studentgroup:
            old_s = old_user.studentgroup
            if old_s.students.count() == 1:
                if old_s != instance.studentgroup:
                    old_s.delete()
