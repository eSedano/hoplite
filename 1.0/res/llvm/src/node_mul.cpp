#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_mul.hpp"

namespace hoplite {

  node_mul::node_mul(unsigned id) : node(id){
  }

  node_mul::~node_mul(){
  }

  NODE_OPCODE
  node_mul::get_opcode(){
    return MUL;
  }

}
