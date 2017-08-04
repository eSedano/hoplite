#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_trim.hpp"

namespace hoplite {

  node_trim::node_trim(unsigned id) : node(id){
  }

  node_trim::~node_trim(){
  }

  NODE_OPCODE
  node_trim::get_opcode(){
    return TRIM;
  }

}
