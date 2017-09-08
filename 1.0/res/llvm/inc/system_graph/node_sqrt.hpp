/**
  SQRT Node
  node_sqrt.hpp
  Purpose: Base class for square root node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_SQRT_HPP
#define HOPLITE_NODE_SQRT_HPP

#include "node.hpp"

namespace hoplite {

  class node_sqrt : public node {
  public:
    node_sqrt(unsigned id);
    virtual ~node_sqrt();

    NODE_OPCODE get_opcode();
  };

}

#endif
