#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_cmp.hpp"

namespace hoplite {

  node_cmp::node_cmp(unsigned id, CMP_TYPE comparison) : node(id){
    (*this).comparison = comparison;
  }

  node_cmp::~node_cmp(){
  }

  NODE_OPCODE
  node_cmp::get_opcode(){
    return CMP;
  }

  CMP_TYPE
  node_cmp::get_cmp_type(){
    return comparison;
  }

}
