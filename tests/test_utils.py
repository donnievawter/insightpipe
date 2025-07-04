from insightpipe.utils import is_file_stable
import tempfile
import os

def test_file_stable():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test data")
        tmp.flush()
        path = tmp.name

    assert is_file_stable(path, interval=1) is True
    os.remove(path)
