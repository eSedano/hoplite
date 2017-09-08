#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_noise.hpp"

namespace hoplite {

  node_noise::node_noise(unsigned id, unsigned input_index, unsigned noise_index) : node(id){
    this->input_index = input_index;
    this->noise_index = noise_index;
  }

  node_noise::~node_noise(){
  }

  NODE_OPCODE
  node_noise::get_opcode(){
    return NOISE;
  }

  unsigned
  node_noise::get_input_index(){
    return input_index;
  }

  unsigned
  node_noise::get_noise_index(){
    return noise_index;
  }

}
