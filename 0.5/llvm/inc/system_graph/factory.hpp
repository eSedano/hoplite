/**
  Factory
  factory.hpp
  Purpose: Base class for instantiating new nodes.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_FACTORY_HPP
#define HOPLITE_FACTORY_HPP

#include <set>
#include <map>
#include "node.hpp"
#include "node_abs.hpp"
#include "node_add.hpp"
#include "node_br.hpp"
#include "node_cmp.hpp"
#include "node_const.hpp"
#include "node_div.hpp"
#include "node_input.hpp"
#include "node_mul.hpp"
#include "node_noise.hpp"
#include "node_output.hpp"
#include "node_phi.hpp"
#include "node_sqrt.hpp"
#include "node_sub.hpp"
#include "node_trim.hpp"
#include "node_virtual.hpp"

#include "../hoplite_utilities.hpp"

namespace hoplite {

  class factory {
  public:

    factory();
    virtual ~factory();

    virtual node* new_node(NODE_OPCODE opcode);
    virtual node* new_node(NODE_OPCODE opcode, CMP_TYPE comparison);
    virtual node* new_node(NODE_OPCODE opcode, double value);

    virtual void reset();

  protected:
    unsigned number_of_nodes;
    unsigned number_of_inputs;
    unsigned number_of_noises;
  };

}
#endif
