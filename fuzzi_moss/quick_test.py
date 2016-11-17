import inspect
import ast

import io

#file = open('example.py')

#result = ast.parse(source=file.read())

#print result.body[2].value.func.func.id
import random

def bob(duration, attention):
    threshold =  1.0 / (duration + 1) ** (1.0 / attention)
    print threshold

a = 50

bob(0, a)
bob(1, a)
bob(2, a)
bob(3, a)
bob(4, a)


#probability = random.uniform(0.0, 1.0)
#print probability
