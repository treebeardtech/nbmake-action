

def log(content: str, filename="treebeard.log"):
    """Manually log your custom content to a local file
    The file is saved at the end of the run and uploaded as an output
    then fetched by the notification function
    Logged content will be presented in the Treebeard admin page,
    and sent via Slack

    Params: content, custom string used in a command from a notebook
    """
    with open(filename, "a+") as f:
        f.write("\n")
        f.write(content)
