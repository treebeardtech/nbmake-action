import subprocess
import sys
from traceback import format_exc

if __name__ == "__main__":
    try:
        subprocess.check_output(["treebeard", "run", "--watch"])
        sys.exit(1)
    except Exception as ex:
        print(format_exc())
        sys.exit(0)
