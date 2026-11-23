"""Optional full-version fixtures for cross-release tests."""
from pathlib import Path


def legacy_source(test, name, *, root=None, sibling=False):
    base=Path(root) if root is not None else Path(__file__).resolve().parent
    path=(base.parent if sibling else base)/name
    try:
        path.stat()
    except FileNotFoundError:
        test.skipTest(f'Optional historical source missing: {name}')
    if not path.is_dir():
        test.fail(f'Historical source is not a directory: {path}')
    return path
