# Example 4: Poetry as dependency manager

Poetry is a python dependency manager: https://github.com/python-poetry/poetry
Install poetry:
`curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`

Using system python 3.71.

1. In top level directory create new poetry project (that generated this readme file):
`poetry new example_4`

2. cd into example_4 and add a dependency
`poetry add pendulum`
`poetry add jupyter`
`poetry add pandas`
`poetry add matplotlib`
`poetry add seaborn`

3. enter poetry virtualenvironment
`poetry shell`

4. run jupyter and explore notebook (n.b. again, VSCode terminal not happy, try other terminal)
`jupyter notebook`