#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/node.hpp"

namespace hoplite {

  node::node(unsigned id) : element() {
    (*this).id = id;
  }

  node::~node(){
  }

  unsigned
  node::get_id(){
    return id;
  }

  void
  node::print(){
    printf("Node ID: %u\n", id);
    p_it p_i = (*this).p_begin();
    printf("\tPredecessors:\n");
    if (p_i != (*this).p_end()){
      printf("\t%u", ((node*)(*p_i))->get_id());
      ++p_i;
      for (; p_i != (*this).p_end(); ++p_i)
        printf(", %u", ((node*)(*p_i))->get_id());
    } else
      printf("\tNone");
    printf("\n");

    s_it s_i = (*this).s_begin();
    printf("\tSuccessors:\n");
    if (s_i != (*this).s_end()){
      printf("\t%u", ((node*)(*s_i))->get_id());
      ++s_i;
      for (; s_i != (*this).s_end(); ++s_i)
        printf(", %u", ((node*)(*s_i))->get_id());
    } else
      printf("\tNone");

    printf("\n\n");
  }

}
