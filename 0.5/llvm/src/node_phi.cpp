#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node_phi.hpp"

namespace hoplite {

  node_phi::node_phi(unsigned id) : node(id){
  }

  node_phi::~node_phi(){
  }

  NODE_OPCODE
  node_phi::get_opcode(){
    return PHI;
  }

  void
  node_phi::add_predecessor_with_bb(node* to_add, unsigned related_bbid){
    predecessors.push_back(to_add);
    bb_from_to_node[related_bbid] = to_add;
    node_to_bb_from[to_add] = related_bbid;
    node_id_to_bb[to_add->get_id()] = related_bbid;
  }

  unsigned
  node_phi::get_basic_block_for_node_id(unsigned node_id){
    return node_id_to_bb[node_id];
  }

  void
  node_phi::print(){
    printf("Node ID: %u\n", id);
    p_it p_i = (*this).p_begin();
    printf("\tPredecessors:\n");
    if (p_i != (*this).p_end()){
      printf("\t%u [%u]", ((node*)(*p_i))->get_id(), node_to_bb_from[(node*)(*p_i)]);
      ++p_i;
      for (; p_i != (*this).p_end(); ++p_i)
        printf(", %u [%u]", ((node*)(*p_i))->get_id(), node_to_bb_from[(node*)(*p_i)]);
    } else
      printf("\tNone");
    printf("\n");

    s_it s_i = (*this).s_begin();
    printf("\tSuccessors:\n");
    if (s_i != (*this).s_end()){
      printf("\t%u ", ((node*)(*s_i))->get_id());
      ++s_i;
      for (; s_i != (*this).s_end(); ++s_i)
        printf(", %u", ((node*)(*s_i))->get_id());
    } else
      printf("\tNone");

    printf("\n\n");
  }
}
