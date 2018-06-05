from django.shortcuts import redirect


def is_student(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_teacher:
            return function(request, *args, **kwargs)
        else:
            return redirect('thesis:groups_home')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_teacher(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_teacher:
            return function(request, *args, **kwargs)
        else:
            return redirect('thesis:group_home')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def has_group(function):
    def wrap(request, *args, **kwargs):
        if request.user.studentgroup:
            return function(request, *args, **kwargs)
        else:
            return redirect('thesis:group_create_join')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
