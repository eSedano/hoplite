/**
  CMP Node
  node_cmp.hpp
  Purpose: Base class for comparison node.

  @author  Enrique Sedano
  @version  0.14.02

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_CMP_HPP
#define HOPLITE_NODE_CMP_HPP

#include "node.hpp"

namespace hoplite {

  class node_cmp : public node {
  public:
    node_cmp(unsigned id, CMP_TYPE comparison);
    virtual ~node_cmp();

    NODE_OPCODE get_opcode();
    CMP_TYPE get_cmp_type();

  protected:
    CMP_TYPE comparison;
  };

}

#endif
