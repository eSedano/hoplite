#!/usr/bin/env python

#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import re
import os
import sys
import time
import sympy
import argparse
import subprocess

from models.lib import c_matrix

# check_version()
#
# Check the Python interpreter is version 2.7 or above.
#
def check_version():
  req_version = (2,7)
  if sys.version_info < req_version:
    sys.exit("Your Python interpreter is too old. Please consider upgrading to Python 2.7 or above.")

# get_execution_order(source)
#
# Generate a list of the order of execution of the nodes inside
#  the system graph.
#
# Beware: This function works only for linear graphs (no loops) 
#
def get_execution_order(source):
  execution_order = []

  dependencies = {x: len(source[x]['preds']) for x in source}
  dependent   = [x for x in dependencies if dependencies[x] >  0]
  independent = [x for x in dependencies if dependencies[x] == 0]

  while dependent:
    for node in independent:
      execution_order.append(node)
      for succ in source[node]['succs']:
        dependencies[succ] = dependencies[succ] - 1
      del dependencies[node]
    dependent   = [x for x in dependencies if dependencies[x] >  0]
    independent = [x for x in dependencies if dependencies[x] == 0]
  else:
    for node in independent:
      execution_order.append(node)

  return execution_order

# generateCmatrix(n_vars, order)
#
# Generates a C matrix of the given dimensions and stores it
#  in the preloads directory.
def generateCmatrix(n_vars, order):
  vars = [sympy.Symbol('v'+str(i)) for i in range(n_vars)]
  print '========== HOPLITE utils =========='
  print 'Generating C matrix:'
  print ' - Dimension:', n_vars
  print ' - Order:', order
  
  start_time = time.time()
  c = c_matrix.c_matrix(vars,order)
  exeution_time = time.time() - start_time
  print ('C matrix successfully generated (%s seconds).' % exeution_time)
  print '===================================' 

def directCmatrix(n_vars, order):
  vars = [sympy.Symbol('v'+str(i)) for i in range(n_vars)]
  print '========== HOPLITE utils =========='
  print 'Generating C matrix the old way:'
  print ' - Dimension:', n_vars
  print ' - Order:', order
  
  start_time = time.time()
  c = c_matrix.c_matrix_direct(vars,order)
  exeution_time = time.time() - start_time
  print ('C matrix successfully generated (%s seconds).' % exeution_time)
  print '==================================='

def generateBase(n_vars, order):
  vars = [sympy.Symbol('v'+str(i)) for i in range(n_vars)]
  print '========== HOPLITE utils =========='
  print 'Generating PCE base:'
  print ' - Dimension:', n_vars
  print ' - Order:', order
  
  start_time = time.time()
  base = c_matrix.allAboutTheBase(vars,order)
  # c = c_matrix.c_matrix_direct(vars,order)
  exeution_time = time.time() - start_time
  print ('PCE base successfully generated (%s seconds).' % exeution_time)
  print '===================================' 

def informationCmatrix(n_vars, order):
  vars = [sympy.Symbol('v'+str(i)) for i in range(n_vars)]
  print '========== HOPLITE utils =========='
  print 'Information on C matrix:'
  print ' - Dimension:', n_vars
  print ' - Order:', order
  
  c = c_matrix.c_matrix(vars,order)

  base = c.base
  matrix = c.matrix

  print 'Base length: {}'.format(str(len(base)))
  print 'Total matrix size: {}'.format(str(len(base)**3))
  print 'Non-zero elements: {}'.format(str(len(matrix)))
  print 'Non-zero ratio: {} %'.format(str(100 * float(len(matrix))/(len(base)**3)))
  print '===================================' 

# The hoplite_utils file can be executed as a standalone script too, in order to
#  run some independent utilities that also belong to the hoplite framework.
if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('--genC', type=int, nargs=2, metavar=('n_vars', 'order'),
                      help='Generates a C matrix of the given dimensions and stores is in the preloads directory.')
  parser.add_argument('--infoC', type=int, nargs=2, metavar=('n_vars', 'order'),
                      help='Provides comprehensive information about the requested C matrix.')
  parser.add_argument('--oldC', type=int, nargs=2, metavar=('n_vars', 'order'),
                      help='Generates a C matrix the old way.')
  parser.add_argument('--base', type=int, nargs=2, metavar=('n_vars', 'order'),
                      help='Generates a PCE base.')
  args = parser.parse_args()

  if not args.genC is None:
    n_vars = args.genC[0]
    order  = args.genC[1]
    generateCmatrix(n_vars, order)

  if not args.infoC is None:
    n_vars = args.infoC[0]
    order  = args.infoC[1]
    informationCmatrix(n_vars, order)

  if not args.oldC is None:
    n_vars = args.oldC[0]
    order  = args.oldC[1]
    directCmatrix(n_vars, order)

  if not args.base is None:
    n_vars = args.base[0]
    order  = args.base[1]
    generateBase(n_vars, order)
