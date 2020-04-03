import subprocess
import sys
from traceback import format_exc

if __name__ == "__main__":
    process = subprocess.Popen(
        ["treebeard", "run", "--watch", "--local", "--confirm"], stdout=subprocess.PIPE
    )
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip().decode())  # type: ignore
    retval = process.poll()
    assert retval == 1
