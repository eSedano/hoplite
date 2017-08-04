#include "llvm/Transforms/hoplite_llvm_graph_extractor/python/python_graph_extractor.hpp"

namespace hoplite {
  void
  python_graph_extractor::extract(system_graph* sg, std::string d){
    source = sg;
    destination = d;

    std::ofstream file;
    file.open(destination.c_str());
    file << "{\n";
    file.close();

    extract_bbs();
    file.open(destination.c_str(), std::ios::app);
    file << ",\n\n";
    file.close();
    extract_nodes();
    file.open(destination.c_str(), std::ios::app);
    file << ",\n\n";
    file.close();
    extract_inputs();
    file.open(destination.c_str(), std::ios::app);
    file << ",\n\n";
    file.close();
    extract_outputs();

    file.open(destination.c_str(), std::ios::app);
    file << "\n}";
    file.close();   
  }

  void
  python_graph_extractor::extract_bbs(){
    std::ofstream file;
    file.open(destination.c_str(), std::ios::app);
    file << "'bbs': {\n";
    file.close();

    for (bb_it i = source->bb_begin(); i != source->bb_end(); ++i){
      extract_bb((basic_block*)(*i));
    }

    file.open(destination.c_str(), std::ios::app);
    file << "\n}";
    file.close();
  }

  void
  python_graph_extractor::extract_nodes(){
    std::ofstream file;
    file.open(destination.c_str(), std::ios::app);
    file << "'nodes': {\n";
    file.close();

    for (node_it i = source->begin(); i != source->end(); ++i){
      extract_node((node*)(*i));
    }

    file.open(destination.c_str(), std::ios::app);
    file << "}";
    file.close();
  }

  void
  python_graph_extractor::extract_inputs(){
    std::ofstream file;
    file.open(destination.c_str(), std::ios::app);
    file << "'inputs': [\n";

    for (in_it i = source->in_begin(); i != source->in_end(); ++i){
      file << ((node*)(*i))->get_id() << ", ";
    }

    file << "\n]";
    file.close();
  }

  void
  python_graph_extractor::extract_outputs(){
    std::ofstream file;
    file.open(destination.c_str(), std::ios::app);
    file << "'outputs': [\n";

    for (out_it i = source->out_begin(); i != source->out_end(); ++i){
      file << ((node*)(*i))->get_id() << ", ";  
    }

    file << "\n]";
    file.close();
  }

  void
  python_graph_extractor::extract_node(node* n){
    std::ofstream file;
    file.open(destination.c_str(), std::ios::app);
    file << n->get_id() << ": {\n";

    file << "'op': " << op_to_str(n->get_opcode()) << ", \n";

    if (n->get_opcode() == PHI) {
      file << "'preds': [";
      for (p_it i = n->p_begin(); i != n->p_end(); ++i){
        unsigned pred_id = ((node*)(*i))->get_id();
        file << "(" << ((node_phi*)n)->get_basic_block_for_node_id(pred_id) << ", "<< pred_id << "), ";
      }
      file << "],\n";      
    } else {
      file << "'preds': [";
      for (p_it i = n->p_begin(); i != n->p_end(); ++i)
        file << ((node*)(*i))->get_id() << ", ";
      file << "],\n";
    }

    file << "'succs': [";
    for (s_it i = n->s_begin(); i != n->s_end(); ++i)
      file << ((node*)(*i))->get_id() << ", ";
    file << "],\n";

    if (n->get_opcode() == CMP) {
      file << "'cmp': " << cmp_to_str(((node_cmp*)n)->get_cmp_type()) << ",\n";
    }

    if (n->get_opcode() == CONST){
      file << "'value': " << ((node_const*)n)->get_value() << ",\n";
    }

    file << "},\n";
    file.close();     
  }

  void
  python_graph_extractor::extract_bb(basic_block* bb){
    std::ofstream file;
    file.open(destination.c_str(), std::ios::app);
    file << bb->get_id() << ": {\n";

    file << "'nodes': [";
    for (bbnodes_it i = bb->begin(); i != bb->end(); ++i)
      file << ((node*)(*i))->get_id() << ", ";
    file << "],\n";
    
    file << "'preds': [";
    for (p_it i = bb->p_begin(); i != bb->p_end(); ++i)
      file << ((basic_block*)(*i))->get_id() << ", ";
    file << "],\n";
    
    file << "'succs': [";
    for (s_it i = bb->s_begin(); i != bb->s_end(); ++i)
      file << ((basic_block*)(*i))->get_id() << ", ";
    file << "],\n";

    file << "\n}, ";
    file.close();  
  }

  std::string
  python_graph_extractor::op_to_str(NODE_OPCODE op){
    switch (op) {
      case ADD:    return "'add'";
      case SUB:    return "'sub'";
      case MUL:    return "'mul'";
      case DIV:    return "'div'";
      case CONST:  return "'const'";
      case PHI:    return "'phi'";
      case ABS:    return "'abs'";
      case SQRT:   return "'sqrt'";
      case CMP:    return "'cmp'";
      case BR:     return "'br'";
      case INPUT:  return "'input'";
      case OUTPUT: return "'output'";
      default: error("Unrecognized opcode.");
    }
    return ""; // Keep the compiler happy.
  }

  std::string
  python_graph_extractor::cmp_to_str(CMP_TYPE cmp){
    switch (cmp) {
      case CMP_TRUE:  return "'TRUE'";
      case CMP_FALSE: return "'FALSE'";
      case LT:        return "'LT'";
      case LTE:       return "'LTE'";
      case EQ:        return "'EQ'";
      case NEQ:       return "'NEQ'";
      case GTE:       return "'GTE'";
      case GT:        return "'GT'";
      default: error("Unrecognized comparison.");
    }
    return ""; // Keep the compiler happy.
  }
}
