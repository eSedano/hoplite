#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/element.hpp"

namespace hoplite {

  element::~element(){
  }

  void
  element::add_successor(element* to_add){
    successors.push_back(to_add);
  }

  void
  element::add_predecessor(element* to_add){
    predecessors.push_back(to_add);
  }

  void
  element::remove_successor(element* to_remove){
    s_it it = std::find(successors.begin(), successors.end(), to_remove);
    if (it != successors.end())
      successors.erase(it);
  }

  void
  element::remove_predecessor(element* to_remove){
    p_it it = std::find(predecessors.begin(), predecessors.end(), to_remove);
    if (it != predecessors.end())
      predecessors.erase(it);
  }

  void
  element::expand_and_remove_successor(element* to_remove){
    s_it position_to_replace = std::find(s_begin(), s_end(), to_remove);
    if (position_to_replace == s_end())
      error("Element is not a successors.");
    successors.insert(position_to_replace, to_remove->s_begin(), to_remove->s_end());
    successors.erase(position_to_replace); 
  }

  void
  element::expand_and_remove_predecessor(element* to_remove){
    p_it position_to_replace = std::find(p_begin(), p_end(), to_remove);
    if (position_to_replace == p_end())
      error("Element is not a predecessor.");
    predecessors.insert(position_to_replace, to_remove->p_begin(), to_remove->p_end());
    predecessors.erase(position_to_replace);
  }

  unsigned
  element::get_successors_size(){
    return successors.size();
  }

  unsigned
  element::get_predecessors_size(){
    return predecessors.size();
  }

  p_it
  element::p_begin(){
    return predecessors.begin();
  }

  p_it
  element::p_end(){
    return predecessors.end();
  }

  p_it
  element::p_find(element* e){
    p_it i;
    for (i = p_begin(); i != p_end(); ++i)
      if ((*i) == e)
        return i;
  }

  s_it
  element::s_begin(){
    return successors.begin();
  }

  s_it
  element::s_end(){
    return successors.end();
  }

  s_it
  element::s_find(element* e){
    s_it i;
    for (i = s_begin(); i != s_end(); ++i)
      if ((*i) == e)
        return i;
  }

}
