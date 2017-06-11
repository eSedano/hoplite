/**
  BR Node
  node_br.hpp
  Purpose: Base class for branch node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_BR_HPP
#define HOPLITE_NODE_BR_HPP

#include "node.hpp"
#include "basic_block.hpp"

namespace hoplite {

  class node_br : public node {
  public:
    node_br(unsigned id);
    virtual ~node_br();

    NODE_OPCODE get_opcode();

    virtual void print();
  };

}

#endif
