/**
  SUB Node
  node_sub.hpp
  Purpose: Base class for substraction node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_SUB_HPP
#define HOPLITE_NODE_SUB_HPP

#include "node.hpp"

namespace hoplite {

  class node_sub : public node {
  public:
    node_sub(unsigned id);
    virtual ~node_sub();

    NODE_OPCODE get_opcode();
  };

}

#endif
