import subprocess

if __name__ == "__main__":
    print("Test local failure fails")
    process = subprocess.Popen(
        "treebeard run --watch --local --confirm", shell=True, stdout=subprocess.PIPE
    )
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip().decode())  # type: ignore
    retval = process.poll()
    print(f"Process exited with status {retval}")
    assert retval == 1

    print("Test remote failure fails")
    process = subprocess.Popen(
        "treebeard run --watch --confirm", shell=True, stdout=subprocess.PIPE
    )
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip().decode())  # type: ignore
    retval = process.poll()
    print(f"Process exited with status {retval}")
    assert retval == 1
