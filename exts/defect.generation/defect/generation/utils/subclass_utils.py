import glob
import importlib
import os


def get_subclasses(cls):
    subclasses = set()
    for subclass in cls.__subclasses__():
        subclasses.add(subclass)

    return subclasses


def import_directory_classes(directory):
    # Get the list of Python files in the directory
    python_files = glob.glob(os.path.join(directory, '*.py'))

    directory = directory.replace('/', '.')
    # Dynamically import all classes from the Python files
    for file in python_files:
        module_name = os.path.basename(file)[:-3]  # remove the '.py' extension
        module = importlib.import_module(f'{directory}.{module_name}')
        classes = [cls for cls in module.__dict__.values() if isinstance(cls, type)]
        for cls in classes:
            globals()[cls.__name__] = cls
