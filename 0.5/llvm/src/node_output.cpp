#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_output.hpp"

namespace hoplite {

  node_output::node_output(unsigned id) : node(id){
  }

  node_output::~node_output(){
  }

  NODE_OPCODE
  node_output::get_opcode(){
    return OUTPUT;
  }

}
