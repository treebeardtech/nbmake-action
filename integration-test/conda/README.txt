# Example 3

1. Create conda environment in local directory
`conda create --name env_3 python=3.7 jupyter scipy astroid babel -y`
activate with :
`conda activate env_3`

**NB this did not play well in VSCode - kept using system python.**

2. Load up jupyter
`jupyter notebook`

3. Export environment
`conda env export --no-builds > environment.yml`

Notebook will download or create several figures and text files and save locally:
FigCCDF.eps, FigD.eps, FigPDF.eps, blackouts.txt, worm.txt, FigCCDFmax.eps, FigLognormal.eps, words.txt
Last cell output of notebook should be: 'End of the notebook'