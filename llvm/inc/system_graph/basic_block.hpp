/**
  Basic Block
  basic_block.hpp
  Purpose: Base class for basic blocks in a system graph.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_BASIC_BLOCK_HPP
#define HOPLITE_BASIC_BLOCK_HPP

#include <set>
#include <algorithm>
#include <stdio.h>

#include "element.hpp"
#include "node.hpp"

namespace hoplite {

  typedef std::set<node*>::iterator bbnodes_it;

  class basic_block : public element {
  public:
    basic_block(unsigned id);
    virtual ~basic_block();

    unsigned get_id();
    virtual void print();
    void add_node(node* to_add);
    void remove_node(node* to_remove);

    bbnodes_it begin();
    bbnodes_it end();
    bbnodes_it find(node* to_find);

  protected:
    unsigned id;
    std::set<node*> content;
  };

}
#endif
