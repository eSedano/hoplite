#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import os
import sys
import shutil
import subprocess

class input_llvm:
  def __init__(self, config, source, destination):
    self.tool_path   = os.path.join(config['llvm_path'], 'Release+Asserts', 'lib', 'hoplite_llvm_graph_extractor.so')
    self.source      = source
    self.destination = destination

    try:
      open(self.tool_path, 'r')
    except IOError:
      print "hoplite_llvm_graph_extractor library not found in LLVM. Attempting to compile it."
      retval = os.getcwd()
      os.chdir(os.path.join(config['llvm_path'], 'lib', 'Transforms', 'hoplite_llvm_graph_extractor'))
      subprocess.call("make")
      os.chdir(retval)
      try:
        open(self.tool_path, 'r')
      except IOError:
        print "hoplite_llvm_graph_extractor library cannot be found nor compiled."
        sys.exit("Please read the documentation to see how to set up the environment.")

  def get(self):
    if not os.path.exists(self.source):
      sys.exit("Cannot find source file. Please specify a valid source.")

    source_extension = self.source.split(".")[-1] # Warning: This piece of code is untested.
    if source_extension == "c" or source_extension == "cpp":
      print "Building code..."
      name_string = self.source.split(".")[:-1]
      name_string.append("bc")
      compile_name = ".".join(name_string)
      try:
      	s = subprocess.Popen(["clang", "-O3", "-emit-llvm", self.source, "-c", "-o", compile_name])
      	s.communicate()
      except OSError:
      	sys.exit("Source file cannot be built. Please install CLANG or load a compiled .bc file.")
      self.source = compile_name

    # Call the LLVM tool to generate the system graph.
    source_f = open(self.source)
    s = subprocess.Popen(["opt", "-load", self.tool_path, "-hoplite_gx"], stdin=source_f)
    s.communicate()

    # The call generates a system_graph_desc.hop file.
    try:
      open('system_graph_desc.hop', 'r')
    except IOError:
      sys.exit("There was an error generating the system graph.")

    f = open('system_graph_desc.hop','r')
    system_graph = eval(f.read())
    f.close()
    
    shutil.move('system_graph_desc.hop', self.destination)

    return system_graph