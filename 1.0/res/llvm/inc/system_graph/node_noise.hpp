/**
  NOISE Node
  node_noise.hpp
  Purpose: Base class for noise node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_NOISE_HPP
#define HOPLITE_NODE_NOISE_HPP

#include "node.hpp"

namespace hoplite {

  class node_noise : public node {
  public:
    node_noise(unsigned id, unsigned input_index, unsigned noise_index);
    virtual ~node_noise();

    NODE_OPCODE get_opcode();

    unsigned get_input_index();
    unsigned get_noise_index();

  protected:
    unsigned input_index;
    unsigned noise_index;
  };

}

#endif
