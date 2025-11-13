import os

def get_dir_size_MB(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it's a symlink
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total / (1024 ** 2) # Convert bytes to MB