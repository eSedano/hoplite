import os
import uuid
import itertools
import pickle
import time
import sympy
from math import factorial
from collections import OrderedDict
from sympy import integrate
from sympy.abc import x

class c_matrix:
  def __init__(self, vars, order):
    self.vars  = vars
    self.order = order

    preload_name = os.path.join(os.getcwd(),'preloads','d'+str(len(vars))+'o'+str(order)+'.pkl')
    if os.path.isfile(preload_name):
      tmp_var = ['___'+str(x)+'___' for x in range(len(vars))]
      with open(preload_name, 'rb') as preload:
        c_struct = pickle.load(preload)
      # tmp_tuples = [(c_struct['vars'][i], tmp_var[i]) for i in range(len(vars))]
      # tmp_base = [b.subs(tmp_tuples) for b in c_struct['base']]
      # tmp_expectances = {x.subs(tmp_tuples): c_struct['expectances'][x] for x in c_struct['expectances']}
      # tmp_matrix = {tuple([x[0].subs(tmp_tuples), x[1].subs(tmp_tuples), x[2].subs(tmp_tuples)]): c_struct['matrix'][x] for x in c_struct['matrix']}

      # var_tuples = [(tmp_var[i], self.vars[i]) for i in range(len(vars))]
      # self.base = [b.subs(var_tuples) for b in tmp_base]
      # self.expectances = {x.subs(var_tuples): tmp_expectances[x] for x in tmp_expectances}
      # self.matrix = {tuple([x[0].subs(var_tuples), x[1].subs(var_tuples), x[2].subs(var_tuples)]): tmp_matrix[x] for x in tmp_matrix}
      self.base = c_struct['base']
      self.matrix = c_struct['matrix']
      self.expectances = c_struct['expectances']
    else:
      self.matrix, self.base, self.expectances = self.generate_c_matrix(self.vars, self.order)

      c_struct = {'vars': self.vars, 'base': self.base, 'expectances': self.expectances, 'matrix': self.matrix}
      save_file = open(preload_name, 'wb')
      pickle.dump(c_struct, save_file)
      save_file.close()

  # Generates the Legendre polynomials for variable x up to the given order.
  # var is expected to be a symbolic value from sympy.abc
  # order is expected to be an integer value between 0 and 10
  
  def get_legendres(self, order, var):
    coeffs = [[sympy.S(1.0)], [sympy.S(0.0), sympy.S(1.0)], [sympy.S(-1.0/2), sympy.S(0.0), sympy.S(3.0/2)], [sympy.S(0.0), sympy.S(-3.0/2), sympy.S(0.0), sympy.S(5.0/2)], \
    [sympy.S(3.0/8), sympy.S(0.0), sympy.S(-30.0/8), sympy.S(0.0), sympy.S(35.0/8)], [sympy.S(0.0), sympy.S(15.0/8), sympy.S(0.0), sympy.S(-70.0/8), sympy.S(0.0), sympy.S(63.0/8)], \
    [sympy.S(-5.0/16), sympy.S(0.0), sympy.S(105.0/16), sympy.S(0.0), sympy.S(-315.0/16), sympy.S(0.0), sympy.S(231.0/16)], \
    [sympy.S(0.0), sympy.S(-35.0/16), sympy.S(0.0), sympy.S(315.0/16), sympy.S(0.0), sympy.S(-693.0/16), sympy.S(0.0), sympy.S(429.0/16)], \
    [sympy.S(35.0/128), sympy.S(0.0), sympy.S(-1260.0/128), sympy.S(0.0), sympy.S(6930.0/128), sympy.S(0.0), sympy.S(-12012.0/128), sympy.S(0.0), sympy.S(6435.0/128)], \
    [sympy.S(0.0), sympy.S(315.0/128), sympy.S(0.0), sympy.S(-4620.0/128), sympy.S(0.0), sympy.S(18018.0/128), sympy.S(0.0), sympy.S(-25740.0/128), sympy.S(0.0), sympy.S(12155.0/128)], \
    [sympy.S(-63.0/256), sympy.S(0.0), sympy.S(3465.0/256), sympy.S(0.0), sympy.S(-30030.0/256), sympy.S(0.0), sympy.S(90090.0/256), sympy.S(0.0), sympy.S(-109395.0/256), sympy.S(0.0), sympy.S(46189.0/256)]]

    pows = [sympy.S(1.0)]
    for i in (range(order+1))[1:]:
      pows.append(var**i)

    legendres = []
    for i in range(order+1):
      tuples = zip(pows, coeffs[i])
      current = []
      for j in tuples:
        current.append(j[0]*j[1])
      legendres.append(sum(current))

    return legendres

  # Generates a list of tuples with the order of each polynome in every 
  # element of the base  
  def get_orders_for_base(self, dim, order):
    # Get all combinations for the orders.
    valid = []
    # Iteratively choose increasing sums or orders.
    for i in range(order+1):
      for j in itertools.product(range(order+1), repeat=dim):
        if sum(j) == i:
          valid.append(j)
    return valid

  # Returns the size of the base
  def get_base_size(self, dim, order):
    return (factorial(dim+order)/(factorial(dim)*factorial(order)))

  # Generates a struct with the base for a given set of variables with the
  # specified order.
  def generate_base(self, variables, order):
    vars = variables[::-1]
    base_orders = self.get_orders_for_base(len(vars), order)
    all_legendres = []
    for var in vars:
      all_legendres.append(self.get_legendres(order,var))

    base = []
    for i in base_orders:
      current = 1.0
      for j in range(len(i)):
        current = current * all_legendres[j][i[j]]
      base.append(current)
    return {"Base": base, "Orders": base_orders}

  def generate_c_matrix(self, vars, order):
    print "Generating base (%dx%d)" % (len(vars), order)
    base_struct = self.generate_base(vars, order)
    base = base_struct["Base"]
    base_orders = base_struct["Orders"]

    x_legendre = self.get_legendres(order, x)
    indexes_3x3 = list(itertools.product(range(order+1), repeat=3))
    all_indexes_expected = list(OrderedDict.fromkeys(indexes_3x3))
    for i in range(len(indexes_3x3)):
      indexes_3x3[i] = tuple(sorted(indexes_3x3[i]))
    unique_indexes_3x3 = list(OrderedDict.fromkeys(indexes_3x3))

    print "Calculating Expected Three-way Products"
    expected = {}
    for i in unique_indexes_3x3:
      value = (1.0/2)*(integrate(x_legendre[i[0]]*x_legendre[i[1]]*x_legendre[i[2]], (x, -1, 1)))
      if value != 0:
        expected[i] = value

    # Calculate Expected Base Squares
    print "Calculating Expected Base Squares"
    expected_base_squares = []
    for i in range(len(base)):
      if i % 100 == 0:
        print "Value %d in %d" % (i, len(base))
      expected_base_square = base[i]*base[i]
      for n in vars:
        expected_base_square = (1.0/2)*(integrate(expected_base_square, (n, -1, 1)))
      expected_base_squares.append(expected_base_square)

    print "Populating C Matrix"
    c_matrix = {}
    iters = 1
    for i in itertools.combinations_with_replacement(range(len(base)), 3):
      if iters % 1000 == 0:
        print "Value %d" % (iters)
      iters += 1
      calculated_value = 1.0
      for j in range(len(vars)):
        if sum([base_orders[i[0]][j], base_orders[i[1]][j], base_orders[i[2]][j]]) % 2 == 1:
          break
        t = tuple(sorted((base_orders[i[0]][j], base_orders[i[1]][j], base_orders[i[2]][j])))
        calculated_value *= expected.get(t, 0.0)
        if calculated_value == 0.0:
          break
      else:
        perms = list(OrderedDict.fromkeys(list(itertools.permutations([i[0],i[1],i[2]]))))
        for p in perms:
          c_key = (base[p[0]], base[p[1]], base[p[2]])
          c_matrix[c_key] = calculated_value / expected_base_squares[p[2]]

    sqr_base_expectances = {}
    for i in range(len(base)):
      sqr_base_expectances[base[i]] = expected_base_squares[i]

    return c_matrix, base, sqr_base_expectances

class c_matrix_direct:
  def __init__(self, vars, order):
    self.vars  = vars
    self.order = order

    print "Generating base"
    base_struct = self.generate_base(vars, order)
    base = base_struct["Base"]

    print "Populating C Matrix"
    self.matrix = [[[0.0 for k in range(len(base))] for j in range(len(base))] for i in range(len(base))]
    for i in range(len(base)):
      for j in range(len(base)):
        for k in range(len(base)):
          value = base[i]*base[j]*base[k]
          b_sq = base[k]*base[k]
          start_time = time.time()
          for d in self.vars:
            value = (1.0/2)*(integrate(value, (d, -1, 1)))
            b_sq = (1.0/2)*(integrate(b_sq, (d, -1, 1)))
          self.matrix[i][j][k] = value / b_sq
          print "It took me %s to compute this fucking value!" % (str(time.time() - start_time))

  def generate_base(self, variables, order):
    vars = variables[::-1]
    base_orders = self.get_orders_for_base(len(vars), order)
    all_legendres = []
    for var in vars:
      all_legendres.append(self.get_legendres(order,var))

    base = []
    for i in base_orders:
      current = 1.0
      for j in range(len(i)):
        current = current * all_legendres[j][i[j]]
      base.append(current)
    return {"Base": base, "Orders": base_orders}

  def get_legendres(self, order, var):
    coeffs = [[sympy.S(1.0)], [sympy.S(0.0), sympy.S(1.0)], [sympy.S(-1.0/2), sympy.S(0.0), sympy.S(3.0/2)], [sympy.S(0.0), sympy.S(-3.0/2), sympy.S(0.0), sympy.S(5.0/2)], \
    [sympy.S(3.0/8), sympy.S(0.0), sympy.S(-30.0/8), sympy.S(0.0), sympy.S(35.0/8)], [sympy.S(0.0), sympy.S(15.0/8), sympy.S(0.0), sympy.S(-70.0/8), sympy.S(0.0), sympy.S(63.0/8)], \
    [sympy.S(-5.0/16), sympy.S(0.0), sympy.S(105.0/16), sympy.S(0.0), sympy.S(-315.0/16), sympy.S(0.0), sympy.S(231.0/16)], \
    [sympy.S(0.0), sympy.S(-35.0/16), sympy.S(0.0), sympy.S(315.0/16), sympy.S(0.0), sympy.S(-693.0/16), sympy.S(0.0), sympy.S(429.0/16)], \
    [sympy.S(35.0/128), sympy.S(0.0), sympy.S(-1260.0/128), sympy.S(0.0), sympy.S(6930.0/128), sympy.S(0.0), sympy.S(-12012.0/128), sympy.S(0.0), sympy.S(6435.0/128)], \
    [sympy.S(0.0), sympy.S(315.0/128), sympy.S(0.0), sympy.S(-4620.0/128), sympy.S(0.0), sympy.S(18018.0/128), sympy.S(0.0), sympy.S(-25740.0/128), sympy.S(0.0), sympy.S(12155.0/128)], \
    [sympy.S(-63.0/256), sympy.S(0.0), sympy.S(3465.0/256), sympy.S(0.0), sympy.S(-30030.0/256), sympy.S(0.0), sympy.S(90090.0/256), sympy.S(0.0), sympy.S(-109395.0/256), sympy.S(0.0), sympy.S(46189.0/256)]]

    pows = [sympy.S(1.0)]
    for i in (range(order+1))[1:]:
      pows.append(var**i)

    legendres = []
    for i in range(order+1):
      tuples = zip(pows, coeffs[i])
      current = []
      for j in tuples:
        current.append(j[0]*j[1])
      legendres.append(sum(current))

    return legendres

  def get_orders_for_base(self, dim, order):
    # Get all combinations for the orders.
    valid = []
    # Iteratively choose increasing sums or orders.
    for i in range(order+1):
      for j in itertools.product(range(order+1), repeat=dim):
        if sum(j) == i:
          valid.append(j)
    return valid

  # Returns the size of the base
  def get_base_size(self, dim, order):
    return (factorial(dim+order)/(factorial(dim)*factorial(order)))

class allAboutTheBase(object):
  def __init__(self, variables, order):
    # self.variables = variables
    # self.order = order
    base = self.generate_base(variables, order)

  def generate_base(self, variables, order):
    vars = variables[::-1]
    base_orders = self.get_orders_for_base(len(vars), order)
    all_legendres = []
    for var in vars:
      all_legendres.append(self.get_legendres(order,var))

    base = []
    for i in base_orders:
      current = 1.0
      for j in range(len(i)):
        current = current * all_legendres[j][i[j]]
      base.append(current)
    return {"Base": base, "Orders": base_orders}

  def get_legendres(self, order, var):
    coeffs = [[sympy.S(1.0)], [sympy.S(0.0), sympy.S(1.0)], [sympy.S(-1.0/2), sympy.S(0.0), sympy.S(3.0/2)], [sympy.S(0.0), sympy.S(-3.0/2), sympy.S(0.0), sympy.S(5.0/2)], \
    [sympy.S(3.0/8), sympy.S(0.0), sympy.S(-30.0/8), sympy.S(0.0), sympy.S(35.0/8)], [sympy.S(0.0), sympy.S(15.0/8), sympy.S(0.0), sympy.S(-70.0/8), sympy.S(0.0), sympy.S(63.0/8)], \
    [sympy.S(-5.0/16), sympy.S(0.0), sympy.S(105.0/16), sympy.S(0.0), sympy.S(-315.0/16), sympy.S(0.0), sympy.S(231.0/16)], \
    [sympy.S(0.0), sympy.S(-35.0/16), sympy.S(0.0), sympy.S(315.0/16), sympy.S(0.0), sympy.S(-693.0/16), sympy.S(0.0), sympy.S(429.0/16)], \
    [sympy.S(35.0/128), sympy.S(0.0), sympy.S(-1260.0/128), sympy.S(0.0), sympy.S(6930.0/128), sympy.S(0.0), sympy.S(-12012.0/128), sympy.S(0.0), sympy.S(6435.0/128)], \
    [sympy.S(0.0), sympy.S(315.0/128), sympy.S(0.0), sympy.S(-4620.0/128), sympy.S(0.0), sympy.S(18018.0/128), sympy.S(0.0), sympy.S(-25740.0/128), sympy.S(0.0), sympy.S(12155.0/128)], \
    [sympy.S(-63.0/256), sympy.S(0.0), sympy.S(3465.0/256), sympy.S(0.0), sympy.S(-30030.0/256), sympy.S(0.0), sympy.S(90090.0/256), sympy.S(0.0), sympy.S(-109395.0/256), sympy.S(0.0), sympy.S(46189.0/256)]]

    pows = [sympy.S(1.0)]
    for i in (range(order+1))[1:]:
      pows.append(var**i)

    legendres = []
    for i in range(order+1):
      tuples = zip(pows, coeffs[i])
      current = []
      for j in tuples:
        current.append(j[0]*j[1])
      legendres.append(sum(current))

    return legendres

  def get_orders_for_base(self, dim, order):
    # Get all combinations for the orders.
    valid = []
    # Iteratively choose increasing sums or orders.
    for i in range(order+1):
      for j in itertools.product(range(order+1), repeat=dim):
        if sum(j) == i:
          valid.append(j)
    return valid

  # Returns the size of the base
  def get_base_size(self, dim, order):
    return (factorial(dim+order)/(factorial(dim)*factorial(order)))
    