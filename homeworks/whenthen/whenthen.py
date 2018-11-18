from functools import wraps

def whenthen(func):
    func.all_when = []
    func.all_then =[]
    func.when = when
    func.then = then

    @wraps(func)
    def wrapped(*args, **kwargs):
        all_when = func.all_when
        all_then = func.all_then
        if len(all_when) != len(all_then):
            raise Exception(f"There are no @{func.__qualname__}.then after last @{func.__qualname__}.when")

        when_then = dict(zip(all_when, all_then))

        for condition in when_then:
            if condition(*args, **kwargs):
                complete_func = when_then[condition]
                break
        else:
            complete_func = func
        return complete_func(*args, **kwargs)

    return wrapped


def when(func):
    base_func = globals()[func.__qualname__]
    if len(base_func.all_when) != len(base_func.all_then):
        raise Exception(f"There are no @{func.__qualname__}.then before previous @{func.__qualname__}.when")
    base_func.all_when.append(func)
    return base_func


def then(func):
    base_func = globals()[func.__qualname__]
    if len(base_func.all_when) - 1 != len(base_func.all_then):
        raise Exception(f"There are no @{func.__qualname__}.when before this @{func.__qualname__}.then")
    base_func.all_then.append(func)
    return base_func
