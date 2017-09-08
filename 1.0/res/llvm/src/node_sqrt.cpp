#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_sqrt.hpp"

namespace hoplite {

  node_sqrt::node_sqrt(unsigned id) : node(id){
  }

  node_sqrt::~node_sqrt(){
  }

  NODE_OPCODE
  node_sqrt::get_opcode(){
    return SQRT;
  }

}
