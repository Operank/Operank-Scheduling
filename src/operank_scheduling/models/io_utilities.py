from pathlib import Path


def find_project_root() -> Path:
    file_parts = list(Path(__file__).parts)
    root_idx = file_parts.index("operank-scheduling")
    return Path(*file_parts[:root_idx + 1])
