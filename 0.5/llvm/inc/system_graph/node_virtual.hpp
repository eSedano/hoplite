/**
  VIRTUAL Node
  node_virtual.hpp
  Purpose: Base class for virtual node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_VIRTUAL_HPP
#define HOPLITE_NODE_VIRTUAL_HPP

#include "node.hpp"

namespace hoplite {

  class node_virtual : public node {
  public:
    node_virtual(unsigned id);
    virtual ~node_virtual();

    NODE_OPCODE get_opcode();
  };

}

#endif
