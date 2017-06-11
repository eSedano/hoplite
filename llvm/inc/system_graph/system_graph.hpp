/**
  System Graph
  system_graph.hpp
  Purpose: Basic structure and functionality for the graph representation of the algorithm.

  @author  Enrique Sedano
  @version  0.14.07

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_SYSTEM_GRAPH_HPP
#define HOPLITE_SYSTEM_GRAPH_HPP

#include <set>
#include <list>
#include <map>
#include <vector>
#include <algorithm>

#include "../hoplite_utilities.hpp"
#include "factory.hpp"
#include "element.hpp"
#include "basic_block.hpp"

namespace hoplite {

  typedef std::set<node*>::iterator node_it;
  typedef std::vector<node*>::iterator in_it;
  typedef std::vector<node*>::iterator out_it;
  typedef std::set<basic_block*>::iterator bb_it;

  class system_graph : public element {
  public:

    system_graph();

    /**
      Creates new graph from a subset of nodes from another graph. In the generated graph,
      nodes will only be linked between them if they are in the input set. If a node is
      passed as second argument, a new output will be created linked to that element.

      WARNING: This constructor only works for linear sub-graphs. An error is triggered if
               a jump-related instruction is part of the input set.
     */
    system_graph(std::set<node*>* to_copy, node* send_to_output = NULL);
    virtual ~system_graph();

    unsigned new_node(NODE_OPCODE opcode, unsigned basic_block_id = 0);
    unsigned new_node(NODE_OPCODE opcode, CMP_TYPE comparison, unsigned basic_block_id = 0);
    unsigned new_node(NODE_OPCODE opcode, double value, unsigned basic_block_id = 0);

    void relate_nodes(unsigned id_from, unsigned id_to);
    void relate_nodes(unsigned id_from, unsigned bbid_from, unsigned id_to);
    void unrelate_nodes(unsigned id_from, unsigned id_to);

    void relate_branch(unsigned branch_node_id, unsigned destination_bb_id);

    virtual void print();

    void declutter();

    void delete_node(unsigned to_remove);

    unsigned get_size();
    unsigned get_inputs_size();
    unsigned get_outputs_size();

    void set_factory(factory* to_set);

    void link_basic_blocks();

    node_it begin();
    node_it end();

    in_it in_begin();
    in_it in_end();

    out_it out_begin();
    out_it out_end();

    bb_it bb_begin();
    bb_it bb_end();

  protected:
    std::set<node*> nodes;
    std::vector<node*> inputs;
    std::vector<node*> outputs;
    std::map<unsigned, node*> id_to_node;
    std::set<basic_block*> basic_blocks;
    std::map<unsigned, basic_block*> id_to_basic_block;
    std::map<unsigned, unsigned> node_id_to_bb_id;

    factory* f;

    void delete_unconnected_nodes();
    void delete_node(node* to_delete);

    void remove_from_nodes(node* to_remove);
    void remove_from_inputs(node* to_remove);
    void remove_from_outputs(node* to_remove);
    void remove_from_id_to_node(node* to_remove);
    void remove_from_basic_block(node* to_remove);

    void delete_virtual_nodes();
    void bypass_and_delete_nodes(std::vector<node*>* to_delete);
    void bypass_node(node* to_bypass);
    std::vector<node*>* get_virtual_nodes();
    void register_node_to_basic_block(unsigned node_id, unsigned bb_id);

  private:
    std::map<int, int>* generate_new_nodes(std::set<node*>* to_copy);
    void relate_new_nodes(std::set<node*>* to_copy, std::map<int, int>* original_to_new);
  };

}
#endif
