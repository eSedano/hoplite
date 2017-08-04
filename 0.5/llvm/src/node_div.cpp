#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_div.hpp"

namespace hoplite {

  node_div::node_div(unsigned id) : node(id){
  }

  node_div::~node_div(){
  }

  NODE_OPCODE
  node_div::get_opcode(){
    return DIV;
  }

}



