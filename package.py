name = "python_editor"

version = "0.0.1"

authors = ["cundesi"]

description = \
    """
    python Editor
    """

private_build_requires = ['rez_build']

@early()
def current_folder():
    import sys
    import os
    if not sys.modules.get('__file__'):
        import inspect
        __file__ = os.path.abspath(inspect.getfile(inspect.currentframe()))
    return os.path.dirname(__file__).replace('\\', '/')


build_command = "rez_build {root}"

uuid = "cundesi.python_editor"


def commands():
    import os

    if "in_debug" in resolve:
        current_folder = this.current_folder
    else:
        current_folder = '{root}'

    env.PYTHONPATH.append(os.path.join(current_folder, "python"))
    env.PATH.append(os.path.join(current_folder, "bin"))

