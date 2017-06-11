/**
  TRIM Node
  node_trim.hpp
  Purpose: Base class for trim node.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_TRIM_HPP
#define HOPLITE_NODE_TRIM_HPP

#include "node.hpp"

namespace hoplite {

  class node_trim : public node {
  public:
    node_trim(unsigned id);
    virtual ~node_trim();

    NODE_OPCODE get_opcode();
  };

}

#endif
