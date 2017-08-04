#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_sub.hpp"

namespace hoplite {

  node_sub::node_sub(unsigned id) : node(id){
  }

  node_sub::~node_sub(){
  }

  NODE_OPCODE
  node_sub::get_opcode(){
    return SUB;
  }

}
