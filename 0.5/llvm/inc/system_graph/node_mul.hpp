/**
  MUL Node
  node_mul.hpp
  Purpose: Base class for multiplication node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_MUL_HPP
#define HOPLITE_NODE_MUL_HPP

#include "node.hpp"

namespace hoplite {

  class node_mul : public node {
  public:
    node_mul(unsigned id);
    virtual ~node_mul();

    NODE_OPCODE get_opcode();
  };

}

#endif
