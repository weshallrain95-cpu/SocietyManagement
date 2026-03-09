from threading import local

_thread_locals = local()


def set_current_society(society):
    _thread_locals.society = society


def get_current_society():
    return getattr(_thread_locals, "society", None)
    