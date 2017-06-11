/**
  CONST Node
  node_const.hpp
  Purpose: Base class for constant value node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_CONST_HPP
#define HOPLITE_NODE_CONST_HPP

#include "node.hpp"

namespace hoplite {

  class node_const : public node {
  public:
    node_const(unsigned id, double value);
    virtual ~node_const();

    NODE_OPCODE get_opcode();

    double get_value();

  protected:
    double const_value;
  };

}

#endif
