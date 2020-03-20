# Making a Reddit Mentions Tracker and Chrome Extension

Pull data from Reddit API and serve analysis in a Google Chrome Extension

Notebook is in `notebook/main.ipynb`  
Contents:

1. Setting up a Reddit API wrapper and querying Reddit
2. Extracting names from Reddit submission titles with SpaCy
3. Saving the results as a dataframe
4. Counting the top mentioned names and plotting them with Plotly
5. Saving the outputs

To run the notebook, `cd notebook` then `pipenv install`

An example python script is in my_script.py  
Remember if you want to run it on a cloud server, the requirements and the AWS command line interface will need to be installed with your credentials for it to work.

To load, go to `chrome://extensions/` in your Google Chrome browser.  
Enable Developer Mode in the top right.  
Click on “Load unpacked extension…” and select the `chrome_extension` directory.  
The extension should appear.  
Keep that tab open as when you make changes you should reload the extension there.
