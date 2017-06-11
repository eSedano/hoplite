#!/usr/bin/env python

#  @author  Enrique Sedano
#  @version  0.14.11
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

# -----------------------------------------------------------------
# Required imports
#
import os
import sys

sys.dont_write_bytecode = True

import copy
import time
import uuid
import shutil
import argparse
import hoplite_utils

from input_interfaces import input_llvm
from input_interfaces import input_xml

from models import model_pce
from models import model_pce_cond
from models import model_megpc
from models import model_megpc_mt
from models import model_montecarlo

from partitioners import partitioner_random
from partitioners import partitioner_ordered
from partitioners import partitioner_hierfm

from searches import search_max_minus_one

# -----------------------------------------------------------------
# Check if current version of interpreter is new enough.
#
hoplite_utils.check_version()

# -----------------------------------------------------------------
# Parse arguments from input and configure help info.
#
parser = argparse.ArgumentParser()
parser.add_argument('source', type=str,
                      help='Absolute path to the source definition of the function to analyze.')
parser.add_argument('-i', "--input", type=str, choices=['llvm', 'xml'], 
                      help='Input tool that will generate the system graph. Overwrites the value stored in the configuration file.')
parser.add_argument('-k', "--keep", action='store_true',
                      help='Keeps the intermediate generated files, if any.')
parser.add_argument('-o', '--output', type=str,
                      help='Path to the destination folder.')
parser.add_argument('-m', "--model", type=str, choices=['pce', 'pce_cond', 'megpc', 'montecarlo', 'megpc_mt'], 
                      help='Analytical or simulation model for the system. Overwrites the value stored in the configuration file.')
parser.add_argument('-p', "--partitioner", type=str, choices=['random', 'ordered', 'hierfm'], 
                      help='Indicates the type of partitioner, if needed, the system will use.')
args = parser.parse_args()

# -----------------------------------------------------------------
# Read configuration file.
#
f = open('config.hop','r')
config = eval(f.read())
f.close()

# Expand input and output paths.
source = os.path.abspath(args.source)
if args.output is None:
  # Create a subfolder in the destination path for the
  #  current process with a random name.
  output = os.path.abspath(os.path.join(os.getcwd(), "tmp", str(uuid.uuid4().get_hex())))
else:
  output = os.path.abspath(args.output)

if not os.path.exists(output): os.makedirs(output)

# Get auxiliary configuration file for input function.
abspath_list = source.split('/')
source_filename = abspath_list[-1].split('.')[0]
source_hop = os.path.abspath(source.replace(abspath_list[-1],'') + source_filename + '.hop')

# Read function configuration file.
if not os.path.isfile(source_hop):
  sys.exit("No configuration file for the function to study was provided.")
f = open(source_hop,'r')
source_config = eval(f.read())

# -----------------------------------------------------------------
# Check the input tool is in place and configured.
#
input_tool = config.get('input_tool', None)
if args.input != None:
  input_tool = args.input
if input_tool == None:
  sys.exit('HOPLITE ERROR: No input tool has been defined.')

# -----------------------------------------------------------------
# Extract system graph from the input.
#

if input_tool == 'llvm':
  input_object = input_llvm.input_llvm(config, source, output)
elif input_tool == 'xml':
  input_object = input_xml.input_xml(config, source, output)
# elif input_tool == ...
#   input_object = ...
#
else: # Default case: No valid input tool.
  exit("Input tool " + input_tool + "not recognized.")

if os.path.isfile(os.path.join(output, 'system_graph_desc.hop')):
  with open(os.path.join(output, 'system_graph_desc.hop'), 'r') as sf:
    system_graph = eval(sf.read())
else:
  start_time = time.time()
  system_graph = input_object.get()
  exeution_time = time.time() - start_time
  print("Loading SG: %s seconds" % exeution_time)  

# -----------------------------------------------------------------
# Get the partitioner tool.
#
partition_tool = args.partitioner

# -----------------------------------------------------------------
# Create the partitioner object.
#
partition_object = None
if partition_tool == None:
  pass # No partition tool? No problem!
elif partition_tool == 'random':
  partition_object = partitioner_random.partitioner_random()
elif partition_tool == 'ordered':
  partition_object = partitioner_ordered.partitioner_ordered()
elif partition_tool == 'hierfm':
  partition_object = partitioner_hierfm.partitioner_hierfm()
# elif partition_tool == ...
#   partition_object = ...
#
else: # Default case: No valid partitioning tool.
  exit("Partitioning tool " + partition_tool + "not recognized.")

# -----------------------------------------------------------------
# Check the signal and noise model.
#
model = config.get('model', None)
if args.model != None:
  model = args.model
if model == None:
  sys.exit('HOPLITE ERROR: No signal/noise model has been defined.')

# -----------------------------------------------------------------
# Instantiate the signal/noise model.
# 
if model == 'pce':
  model_object = model_pce.model_pce(config, source_config, system_graph, output, partition_object)
elif model == 'pce_cond':
  model_object = model_pce_cond.model_pce_cond(config, source_config, system_graph, output, partition_object)
elif model == 'megpc':
  model_object = model_megpc.model_megpc(config, source_config, system_graph, output, partition_object)
elif model == 'megpc_mt':
  model_object = model_megpc_mt.model_megpc_mt(config, source_config, system_graph, output, partition_object)
elif model == 'montecarlo':
  model_object = model_montecarlo.model_montecarlo(config, system_graph, output, partition_object)
# if model == ...:
#   model_object = ...
#
else: # Default case: No valid signal/noise model.
  exit("Signal/noise model " + model + "not recognized.")

search_object = search_max_minus_one.search_max_minus_one(source_config, model_object)

start_time = time.time()

model_object.compute()

exeution_time = time.time() - start_time
print("Modelling: %s seconds" % exeution_time)

start_time = time.time()

search_object.run()

exeution_time = time.time() - start_time
print("Search: %s seconds" % exeution_time)

# Busqueda.

print "Process finished."
# Delete all intermediate files if not specified otherwise.
if not args.keep: shutil.rmtree(output)
