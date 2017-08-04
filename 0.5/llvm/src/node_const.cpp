#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_const.hpp"

namespace hoplite {

  node_const::node_const(unsigned id, double value) : node(id){
    const_value = value;
  }

  node_const::~node_const(){
  }

  NODE_OPCODE
  node_const::get_opcode(){
    return CONST;
  }

  double
  node_const::get_value(){
    return const_value;
  }

}
