# -----------------------------------------------------------------
# PCE operations
# -----------------------------------------------------------------
from collections import Counter
# -----------------------------------------------------------------
# Propagate two PCE polynomials through an ADD operator
#
def add(a, b):
  # c = Counter(a) + Counter(b)
  c = {}
  for i in a.keys() + b.keys():
    c.update({i: a.get(i,0.0) + b.get(i,0.0)})

  return {k: v for k, v in c.iteritems() if v != 0.0}

# -----------------------------------------------------------------
# Propagate two PCE polynomials through an SUB operator
#
def sub(a, b):
  # c = Counter(a.copy())
  # c.subtract(b)
  c = {}
  for i in a.keys() + b.keys():
    c.update({i: a.get(i,0.0) - b.get(i,0.0)})
  return {k: v for k, v in c.iteritems() if v != 0.0}

# -----------------------------------------------------------------
# Propagate two PCE polynomials through an MUL operator
#
def mul(a, b, c_matrix):
  c = {}
  tuples = [(i, j, k)
        for i in a.keys()
        for j in b.keys()
        for k in c_matrix.base]
  for t in tuples:
    c.update({t[2]: c.get(t[2], 0.0) + (a[t[0]]*b[t[1]]*c_matrix.matrix.get(t,0.0))})
  for k in c.keys(): # Allow some rounding so the system is not too overloaded. 
    if c[k] is float:
      if c[k] <= 1e-13: c[k] = 0.0

  return {k: v for k, v in c.iteritems() if v != 0.0}