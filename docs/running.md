# Running notebooks

When you are inside a directory containing a `treebeard.yaml` you can start cloud runs.

`treebeard run` kicks off a cloud run and gives you a link to view the outputs.

In this example we pass the `--daily` option to specify that once built, this notebook will run at midnight.

```bash
examples/nationalgrid on  master [$!?] via 🌲 0.0.56
➜ treebeard run --daily
⠙ 🌲  Compressing Repo

  Including
  Including .gitignore
  Including .ipynb_checkpoints
  ...
  Including README.rst
  Including daily-wind-availability.csv
  Including main.ipynb
  Including requirements.txt
  Including treebeard.yaml
✨  Run has been accepted! https://treebeard.io/admin/d8a0c5b6c9/nationalgrid/8fdaaf48-a45b-4013-8c75-3f95dccc4fb8
```

Use `treebeard status` to check recent runs and any schedule configuration.

```bash
➜ treebeard status
🌲  Recent runs:

  ⏳  1 minute ago via CLI -- https://treebeard.io/admin/d8a0c5b6c9/nationalgrid/8fdaaf48-a45b-4013-8c75-3f95dccc4fb8

  📅  Schedule: daily
```

`treebeard cancel` stops any run in progress and removes any schedule

```bash
examples/nationalgrid on  master [$!?] via 🌲 0.0.56
➜ treebeard cancel
🌲  Cancelling nationalgrid
🛑 Done!
```
