# Hello Treebeard!
Hello world with Treebeard command line deployment

Let's get started:
1. Clone this repository if you haven't already:
```
git clone https://github.com/treebeardtech/hello_treebeard.git && cd hello_treebeard
```

2. Install the requirements:
```
pipenv install -r requirements.txt
```
or 
```
pip install -r requirements.txt
```

3. Run the notebook (if you want - or skip ahead)
```
jupyter notebook
```

4. Set up treebeard ([register for an account first](treebeard.io))
```
treebeard configure
```

5. Schedule your notebook run
```
treebeard deploy --daily
```

6. Give it a sec - the outputs will appear on your admin page on your schedule!

All done, pat on the back.
