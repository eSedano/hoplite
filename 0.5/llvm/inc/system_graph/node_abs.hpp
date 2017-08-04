/**
  ABS Node
  node_abs.hpp
  Purpose: Base class for absolute value node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_ABS_HPP
#define HOPLITE_NODE_ABS_HPP

#include "node.hpp"

namespace hoplite {

  class node_abs : public node {
  public:
    node_abs(unsigned id);
    virtual ~node_abs();

    NODE_OPCODE get_opcode();
  };

}

#endif
