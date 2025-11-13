import os

def pathy(*parts):
    """Join paths cleanly, cross-platform."""
    return os.path.normpath(os.path.join(*parts))
