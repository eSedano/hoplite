/**
  DIV Node
  node_div.hpp
  Purpose: Base class for division node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_DIV_HPP
#define HOPLITE_NODE_DIV_HPP

#include "node.hpp"

namespace hoplite {

  class node_div : public node {
  public:
    node_div(unsigned id);
    virtual ~node_div();

    NODE_OPCODE get_opcode();
  };

}

#endif



