import os


def clean_log_file():
    """Empty logfile
    """
    if os.path.exists("treebeard.log"):
        os.remove("treebeard.log")
