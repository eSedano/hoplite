#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/system_graph.hpp"

namespace hoplite {

  system_graph::system_graph(){
    f = new factory();
  }

  system_graph::system_graph(std::set<node*>* to_copy, node* send_to_output){
    f = new factory();

    std::map<int, int>* original_to_new;
    original_to_new = generate_new_nodes(to_copy);
    relate_new_nodes(to_copy, original_to_new);

    if (send_to_output != NULL){
      relate_nodes((*original_to_new)[send_to_output->get_id()], new_node(OUTPUT));
    }

    declutter();
  }

  std::map<int, int>*
  system_graph::generate_new_nodes(std::set<node*>* to_copy){
    std::map<int, int>* to_return = new std::map<int, int>();
    std::set<node*>::iterator it;
    for (it = to_copy->begin(); it != to_copy->end(); ++it){
      switch ((*it)->get_opcode()){
        case CMP:
          (*to_return)[(*it)->get_id()] = new_node(CMP, ((node_cmp*)(*it))->get_cmp_type());
          break;
        case CONST:
          (*to_return)[(*it)->get_id()] = new_node(CONST, ((node_const*)(*it))->get_value());
          break;
        case PHI:
        case BR:
          error("Unsupported type of operation for this constructor");
        default:
          (*to_return)[(*it)->get_id()] = new_node((*it)->get_opcode());
          break;
      }
    }
    return to_return;
  }

  void
  system_graph::relate_new_nodes(std::set<node*>* to_copy, std::map<int, int>* original_to_new){
    std::set<node*>::iterator it;
    for (it = to_copy->begin(); it != to_copy->end(); ++it){
      s_it s = (*it)->s_begin();
      for (; s != (*it)->s_end(); ++s){
        if (to_copy->find((node*)(*s)) != to_copy->end())
          relate_nodes((*original_to_new)[(*it)->get_id()], (*original_to_new)[((node*)(*s))->get_id()]);
      }
    }
  }

  system_graph::~system_graph(){
  }

  unsigned
  system_graph::new_node(NODE_OPCODE opcode, unsigned basic_block_id){
    node* to_add = f->new_node(opcode);
    switch (opcode){
      case INPUT: inputs.push_back(to_add); break;
      case OUTPUT: outputs.push_back(to_add); break;
      default: break;
    }
    nodes.insert(to_add);
    id_to_node[to_add->get_id()] = to_add;
    unsigned node_id = to_add->get_id();
    register_node_to_basic_block(node_id, basic_block_id);
    return node_id;
  }

  unsigned
  system_graph::new_node(NODE_OPCODE opcode, CMP_TYPE comparison, unsigned basic_block_id){
    node* to_add = f->new_node(opcode, comparison);
    nodes.insert(to_add);
    id_to_node[to_add->get_id()] = to_add;
    unsigned node_id = to_add->get_id();
    register_node_to_basic_block(node_id, basic_block_id);
    return node_id;
  }

  unsigned
  system_graph::new_node(NODE_OPCODE opcode, double value, unsigned basic_block_id){
    node* to_add = f->new_node(opcode, value);
    nodes.insert(to_add);
    id_to_node[to_add->get_id()] = to_add;
    unsigned node_id = to_add->get_id();
    register_node_to_basic_block(node_id, basic_block_id);
    return node_id;
  }

  void
  system_graph::relate_nodes(unsigned id_from, unsigned id_to){
    node* node_from = id_to_node[id_from];
    node* node_to = id_to_node[id_to];

    node_from->add_successor(node_to);
    node_to->add_predecessor(node_from);
  }

  void
  system_graph::relate_nodes(unsigned id_from, unsigned bbid_from, unsigned id_to){
    node* node_from = id_to_node[id_from];
    node* node_to = id_to_node[id_to];

    if (node_to->get_opcode() != PHI)
      error("Trying to link non-PHI node as PHI node.");

    node_from->add_successor(node_to);
    ((node_phi*)node_to)->add_predecessor_with_bb(node_from, bbid_from);
    printf("Linking PHI node! Adding predecessor %u with bb %u\n", id_from, bbid_from);
  }

  void
  system_graph::unrelate_nodes(unsigned id_from, unsigned id_to){
    node* node_from = id_to_node[id_from];
    node* node_to = id_to_node[id_to];

    node_from->remove_successor(node_to);
    node_to->remove_predecessor(node_from);
  }

  void
  system_graph::relate_branch(unsigned branch_node_id, unsigned destination_bb_id){
    node* node_from = id_to_node[branch_node_id];
    basic_block* bb_to = id_to_basic_block[destination_bb_id];

    node_from->add_successor(bb_to);

    std::set<basic_block*>::iterator it;
    for (it = basic_blocks.begin(); it != basic_blocks.end(); ++it){
      if ((*it)->find(node_from) != (*it)->end()){
        (*it)->add_successor(bb_to);
        bb_to->add_predecessor(*it);
      }
    }
  }

  void
  system_graph::print(){
    printf("System graph basic blocks:\n");
    for (std::set<basic_block*>::iterator i = basic_blocks.begin(); i != basic_blocks.end(); ++i){
      (*i)->print();
    }
    printf("\nSystem graph nodes:\n");

    for (std::set<node*>::iterator i = nodes.begin(); i != nodes.end(); ++i){
      (*i)->print();
    }
    printf("\n");
  }

  void
  system_graph::set_factory(factory* to_set){
    f = to_set;
  }

  void
  system_graph::declutter(){
    debug("Decluttering system graph.");
    delete_virtual_nodes();
    delete_unconnected_nodes();
  }

  void
  system_graph::delete_unconnected_nodes(){
    std::vector<node*> nodes_to_remove;
    for (std::set<node*>::iterator i = nodes.begin(); i != nodes.end(); ++i){
      if ((*i)->get_predecessors_size() == 0 && (*i)->get_successors_size() == 0){
        debug("Unconnected node found. It will be removed.");
        nodes_to_remove.push_back(*i);
      }
    }
    while (!nodes_to_remove.empty()){
      delete_node(nodes_to_remove.back());
      nodes_to_remove.pop_back();
    }
  }

  void
  system_graph::delete_node(node* to_delete){
    remove_from_nodes(to_delete);
    remove_from_inputs(to_delete);
    remove_from_outputs(to_delete);
    remove_from_id_to_node(to_delete);
    remove_from_basic_block(to_delete);
    delete to_delete;
  }

  void
  system_graph::delete_node(unsigned to_delete){
    delete_node(id_to_node[to_delete]);
  }

  void
  system_graph::remove_from_nodes(node* to_remove){
    nodes.erase(to_remove);
  }

  void
  system_graph::remove_from_inputs(node* to_remove){
    std::vector<node*>::iterator it = std::find(inputs.begin(), inputs.end(), to_remove);
    if (it != inputs.end())
      inputs.erase(it);
  }

  void
  system_graph::remove_from_outputs(node* to_remove){
    std::vector<node*>::iterator it = std::find(outputs.begin(), outputs.end(), to_remove);
    if (it != outputs.end())
      outputs.erase(it);
  }

  void
  system_graph::remove_from_id_to_node(node* to_remove){
    std::map<unsigned, node*>::iterator it = id_to_node.find(to_remove->get_id());
    id_to_node.erase(it);
  }

  void
  system_graph::remove_from_basic_block(node* to_remove){
    std::set<basic_block*>::iterator it;
    for (it = basic_blocks.begin(); it != basic_blocks.end(); ++it){
      if ((*it)->find(to_remove) != (*it)->end())
        (*it)->remove_node(to_remove);
    }
  }

  void
  system_graph::delete_virtual_nodes(){
    std::vector<node*>* to_delete = get_virtual_nodes();
    bypass_and_delete_nodes(to_delete);
    delete to_delete;
  }

  void
  system_graph::bypass_and_delete_nodes(std::vector<node*>* to_delete){
    for (std::vector<node*>::iterator i = to_delete->begin(); i != to_delete->end(); ++i){
      bypass_node(*i);
      delete_node(*i);
    }
  }

  void
  system_graph::bypass_node(node* to_bypass){
    for (p_it it = to_bypass->p_begin(); it != to_bypass->p_end(); ++it){
      (*it)->expand_and_remove_successor(to_bypass);
    }

    for (s_it it = to_bypass->s_begin(); it != to_bypass->s_end(); ++it){
      (*it)->expand_and_remove_predecessor(to_bypass);  
    }
  }

  std::vector<node*>*
  system_graph::get_virtual_nodes(){
    std::vector<node*>* to_return = new std::vector<node*>();

    for (std::set<node*>::iterator it = nodes.begin(); it != nodes.end(); ++it){
      if ((*it)->get_opcode() == VIRTUAL){
        to_return->push_back(*it);
      }
    }
    return to_return;
  }

  void
  system_graph::register_node_to_basic_block(unsigned node_id, unsigned bb_id){
    std::map<unsigned, basic_block*>::iterator it = id_to_basic_block.find(bb_id);
    // If the BB hasn't been registered before, create a new one now.
    if (it == id_to_basic_block.end()){
        basic_block* to_add = new basic_block(bb_id);
        basic_blocks.insert(to_add);
        id_to_basic_block[bb_id] = to_add;
    }

    (id_to_basic_block[bb_id])->add_node(id_to_node[node_id]);
    node_id_to_bb_id[node_id] = bb_id;
  }

  void
  system_graph::link_basic_blocks(){
    basic_block* bb_0 = id_to_basic_block[0];
    std::set<unsigned> destination_bbs;
    std::set<unsigned> source_bbs;
    for (bbnodes_it i = bb_0->begin(); i != bb_0->end(); ++i){
      for (s_it j = (*i)->s_begin(); j != (*i)->s_end(); ++j){
        destination_bbs.insert(node_id_to_bb_id[((node*)(*j))->get_id()]);
      }
      for (p_it j = (*i)->p_begin(); j != (*i)->p_end(); ++j){
        source_bbs.insert(node_id_to_bb_id[((node*)(*j))->get_id()]);
      }
    }
    for (std::set<unsigned>::iterator i = destination_bbs.begin(); i != destination_bbs.end(); ++i){
      basic_block* destination_bb = id_to_basic_block[*i];
      bb_0->add_successor(destination_bb);
      destination_bb->add_predecessor(bb_0);
    }
    for (std::set<unsigned>::iterator i = source_bbs.begin(); i != source_bbs.end(); ++i){
      basic_block* source_bb = id_to_basic_block[*i];
      bb_0->add_predecessor(source_bb);
      source_bb->add_successor(bb_0);
    }
  }

  unsigned
  system_graph::get_outputs_size(){
    return outputs.size();
  }

  node_it
  system_graph::begin(){
    return nodes.begin();
  }
  node_it
  system_graph::end(){
    return nodes.end();
  }

  in_it
  system_graph::in_begin(){
    return inputs.begin();
  }

  in_it
  system_graph::in_end(){
    return inputs.end();
  }

  out_it
  system_graph::out_begin(){
    return outputs.begin();
  }

  out_it
  system_graph::out_end(){
    return outputs.end();
  }

  bb_it
  system_graph::bb_begin(){
    return basic_blocks.begin();
  }

  bb_it
  system_graph::bb_end(){
    return basic_blocks.end();
  }

}
