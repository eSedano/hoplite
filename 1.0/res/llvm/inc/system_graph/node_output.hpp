/**
  OUTPUT Node
  node_output.hpp
  Purpose: Base class for output node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_OUTPUT_HPP
#define HOPLITE_NODE_OUTPUT_HPP

#include "node.hpp"

namespace hoplite {

  class node_output : public node {
  public:
    node_output(unsigned id);
    virtual ~node_output();

    NODE_OPCODE get_opcode();
  };

}

#endif
