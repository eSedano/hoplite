/**
  INPUT Node
  node_input.hpp
  Purpose: Base class for input node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_INPUT_HPP
#define HOPLITE_NODE_INPUT_HPP

#include "node.hpp"

namespace hoplite {

  class node_input : public node {
  public:
    node_input(unsigned id, unsigned input_index);
    virtual ~node_input();

    NODE_OPCODE get_opcode();

    unsigned get_input_index();

  protected:
    unsigned input_index;
  };

}

#endif
