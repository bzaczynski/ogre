import StringIO


class FakeFileObject(StringIO.StringIO):
    """Amalgam of StringIO and the "with" statement."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
