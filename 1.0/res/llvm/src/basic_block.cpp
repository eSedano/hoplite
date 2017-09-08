#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/basic_block.hpp"

namespace hoplite {

  basic_block::basic_block(unsigned id) : element() {
    (*this).id = id;
  }

  basic_block::~basic_block(){
  }

  unsigned
  basic_block::get_id(){
    return id;
  }

  void
  basic_block::print(){
    printf("Basic Block ID: %u\nNodes: ", id);
    bbnodes_it bbn_i = (*this).begin();
    p_it p_i = (*this).p_begin();
    if (bbn_i != (*this).end()){
      printf("\t%u", (*bbn_i)->get_id());
      ++bbn_i;
      for (; bbn_i != (*this).end(); ++bbn_i)
        printf(", %u", (*bbn_i)->get_id());
    } else
      printf("\tNone");
    printf("\n");/*
    printf("\tPredecessors:\n");
      if (p_i != (*this).p_end()){
        printf("\t%u", ((basic_block*)(*p_i))->get_id());
        ++p_i;
        for (; p_i != (*this).p_end(); ++p_i)
          printf(", %u", ((basic_block*)(*p_i))->get_id());
      } else
        printf("\tNone");
      printf("\n");

      s_it s_i = (*this).s_begin();
      printf("\tSuccessors:\n");
      if (s_i != (*this).s_end()){
        printf("\t%u", ((basic_block*)(*s_i))->get_id());
        ++s_i;
        for (; s_i != (*this).s_end(); ++s_i)
          printf(", %u", ((basic_block*)(*s_i))->get_id());
      } else
        printf("\tNone");
*/
      printf("Predecessors size: %u\n", get_predecessors_size());
      printf("Successors size: %u\n", get_successors_size());
      printf("\n\n");

  }

  bbnodes_it
  basic_block::begin(){
    return content.begin();
  }

  bbnodes_it
  basic_block::end(){
    return content.end();
  }

  bbnodes_it
  basic_block::find(node* to_find){
    return content.find(to_find);
  }

  void
  basic_block::add_node(node* to_add){
    content.insert(to_add);
  }

  void
  basic_block::remove_node(node* to_remove){
    content.erase(to_remove);
  }

}
