/**
  PHI Node
  node_phi.hpp
  Purpose: Base class for PHI node.

  @author  Enrique Sedano
  @version  0.14.08

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_PHI_HPP
#define HOPLITE_NODE_PHI_HPP

#include <map>

#include "node.hpp"

namespace hoplite {

  class node_phi : public node {
  public:
    node_phi(unsigned id);
    virtual ~node_phi();

    NODE_OPCODE get_opcode();

    unsigned get_basic_block_for_node_id(unsigned node_id);

    void add_predecessor_with_bb(node* to_add, unsigned related_bbid);

    virtual void print();

  protected:
    std::map<unsigned, node*> bb_from_to_node;
    std::map<node*, unsigned> node_to_bb_from;
    std::map<unsigned, unsigned> node_id_to_bb;
  };

}

#endif
