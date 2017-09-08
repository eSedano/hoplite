#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_add.hpp"

namespace hoplite {

  node_add::node_add(unsigned id) : node(id){
  }

  node_add::~node_add(){
  }

  NODE_OPCODE
  node_add::get_opcode(){
    return ADD;
  }

}
