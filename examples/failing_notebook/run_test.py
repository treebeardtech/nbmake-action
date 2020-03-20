import subprocess
import sys

if __name__ == "__main__":
    try:
        subprocess.check_output(["treebeard", "run", "--watch"])
        sys.exit(1)
    except Exception as ex:
        print(ex)
        sys.exit(0)
