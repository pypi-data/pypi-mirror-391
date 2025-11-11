import os
from typing import (
    List
)
from vdutils.resources import resource_filename


__sep__ = '\t'
__encoding__: str = 'utf-8'
__index__: bool = False

def _get_folder_names(
    library_name: str,
    base_folder_path: str
) -> List[str]:
    resource_path = resource_filename(library_name, base_folder_path)
    return [f.name for f in os.scandir(resource_path) if f.is_dir()]