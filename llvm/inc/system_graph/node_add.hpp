/**
  ADD Node
  node_add.hpp
  Purpose: Base class for addition node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_ADD_HPP
#define HOPLITE_NODE_ADD_HPP

#include "node.hpp"

namespace hoplite {

  class node_add : public node {
  public:
    node_add(unsigned id);
    virtual ~node_add();

    NODE_OPCODE get_opcode();
  };

}

#endif
