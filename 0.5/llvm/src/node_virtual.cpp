#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_virtual.hpp"

namespace hoplite {

  node_virtual::node_virtual(unsigned id) : node(id){
  }

  node_virtual::~node_virtual(){
  }

  NODE_OPCODE
  node_virtual::get_opcode(){
    return VIRTUAL;
  }

}
