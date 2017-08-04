/**
  Node
  node.hpp
  Purpose: Base class for nodes in a system graph.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_NODE_HPP
#define HOPLITE_NODE_HPP

#include <algorithm>
#include <stdio.h>
#include <string>

#include "element.hpp"

namespace hoplite {

  enum NODE_OPCODE { ADD, SUB, MUL, DIV, CONST, PHI, ABS, SQRT, CMP, BR, SEL, GET_ELEMENT_PTR, LOAD, SWITCH, INPUT, OUTPUT, VIRTUAL, NOISE, TRIM };
  enum CMP_TYPE {CMP_TRUE, CMP_FALSE, LT, LTE, EQ, NEQ, GTE, GT};

  class node : public element {
  public:
    node(unsigned id);
    virtual ~node();

    unsigned get_id();

    virtual NODE_OPCODE get_opcode() = 0;

    virtual void print();

  protected:
    unsigned id;
  };

}
#endif
