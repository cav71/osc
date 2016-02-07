# Simple plugin example

# this will be imported (as is a module)
import os

# this will be imported (as is a module)
from os import path

# this won't be imported
X = 123


# this will be imported (as it is a function in the current module)
def hello(name): # this function will be loaded 
    print('Hello', name)

