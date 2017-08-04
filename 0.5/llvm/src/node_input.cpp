#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_input.hpp"

namespace hoplite {

  node_input::node_input(unsigned id, unsigned input_index) : node(id){
    this->input_index = input_index;
  }

  node_input::~node_input(){
  }

  NODE_OPCODE
  node_input::get_opcode(){
    return INPUT;
  }

  unsigned
  node_input::get_input_index(){
    return input_index;
  }

}
