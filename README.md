# Prerequisites

- Python 3.9 or 3.10 (tested with 3.9.6 and 3.9.12 and 3.10.10)
- OpenGL 3.3.0 or higher

# Installation

Clone the repository with `git clone --recursive https://github.com/marcuscastelo/cg-trab`

## Install dependencies

### Linux

`make install-deps`

### Windows (or without make)

`pip install -r requirements.txt`
`cd vendor`
`pip install -e utils`
`pip install -e dpgext`


# Run the game

`make run` 

or

`python src/main.py`
