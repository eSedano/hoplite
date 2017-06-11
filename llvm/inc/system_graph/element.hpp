/**
  Element
  element.hpp
  Purpose: Base interface class for all system graph components.

  @author  Enrique Sedano
  @version  0.14.02

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_ELEMENT_HPP
#define HOPLITE_ELEMENT_HPP

#include <vector>
#include <string>
#include <algorithm>
#include <stdio.h>

#include "../hoplite_utilities.hpp"

namespace hoplite {

  class element;

  typedef std::vector<element*>::iterator s_it;
  typedef std::vector<element*>::iterator p_it;

  class element {
  public:
    virtual ~element();

    virtual void add_successor(element* to_add);
    virtual void add_predecessor(element* to_add);

    void remove_successor(element* to_remove);
    void remove_predecessor(element* to_remove);

    void expand_and_remove_successor(element* to_remove);
    void expand_and_remove_predecessor(element* to_remove);

    unsigned get_successors_size();
    unsigned get_predecessors_size();

    virtual void print() = 0;

    p_it p_begin();
    p_it p_end();
    p_it p_find(element* e);

    s_it s_begin();
    s_it s_end();
    s_it s_find(element* e);

  protected:
    std::vector<element*> predecessors;
    std::vector<element*> successors;
  };

}

#endif // HOPLITE_ELEMENT_HPP
