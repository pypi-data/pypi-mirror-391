import os

def ipathy(p):
    """
    Cross-platform path normalizer.
    Cleans slashes, resolves ../, and expands ~
    """
    p = os.path.expanduser(p)
    p = p.replace('\\', '/')
    parts = []
    for part in p.split('/'):
        if part == '..' and parts:
            parts.pop()
        elif part and part != '.':
            parts.append(part)
    return '/'.join(parts)
