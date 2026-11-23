"""Optional full-version fixtures for cross-release tests."""
import os
from pathlib import Path


def legacy_source(test, name, *, root=None, sibling=False):
    configured=os.environ.get('TOP_ANTRENORU_TEST_ARCHIVE')
    if configured:
        archive=Path(configured)
        if not archive.is_absolute():
            test.fail('TOP_ANTRENORU_TEST_ARCHIVE must be an absolute path')
        path=archive/name
    else:
        base=Path(root) if root is not None else Path(__file__).resolve().parent
        path=(base.parent if sibling else base)/name
    try:
        path.stat()
    except FileNotFoundError:
        if configured:
            test.fail(f'Configured historical source is missing: {path}')
        test.skipTest(f'Optional historical source missing: {name}')
    if not path.is_dir():
        test.fail(f'Historical source is not a directory: {path}')
    return path
