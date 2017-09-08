#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_abs.hpp"

namespace hoplite {

  node_abs::node_abs(unsigned id) : node(id){
  }

  node_abs::~node_abs(){
  }

  NODE_OPCODE
  node_abs::get_opcode(){
    return ABS;
  }

}
