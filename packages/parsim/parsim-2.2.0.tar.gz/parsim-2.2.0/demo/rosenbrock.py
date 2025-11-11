"""
Compute Rosenbrock function.
"""
from __future__ import print_function

def rb(x1, x2):
    return 100*(x2 - x1**2)**2 + (1 - x1)**2

# -----------------------------------
# Input data
# -----------------------------------

x1 = 1.5
x2 = 0.5

# -----------------------------------
# Calculation/simulation
# -----------------------------------

f = rb(x1, x2)

# -----------------------------------
# Results output
# -----------------------------------

print('x1', 'x2', 'f')
print(x1, x2, f)
