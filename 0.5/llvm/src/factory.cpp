#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/factory.hpp"

namespace hoplite {

  factory::factory(){
    number_of_nodes = 0;
    number_of_inputs = 0;
    number_of_noises = 0;
  }

  factory::~factory(){
  }

  node*
  factory::new_node(NODE_OPCODE opcode){
    unsigned id_to_assign = number_of_nodes;
    node* to_return = NULL;
    switch (opcode){
      case ABS:
        to_return = new node_abs(id_to_assign);
        break;
      case ADD:
        to_return = new node_add(id_to_assign);
        break;
      case BR:
        to_return = new node_br(id_to_assign);
        break;
      case CMP:
        error("Not enough arguments for CMP node instantiation.");
        break;
      case CONST:
        error("Not enough arguments for CONST node instantiation.");
        break;
      case DIV:
        to_return = new node_div(id_to_assign);
        break;
      case INPUT:
        to_return = new node_input(id_to_assign, number_of_inputs);
        number_of_inputs++;
        break;
      case MUL:
        to_return = new node_mul(id_to_assign);
        break;
      case OUTPUT:
        to_return = new node_output(id_to_assign);
        break;
      case PHI:
        to_return = new node_phi(id_to_assign);
        break;
      case SQRT:
        to_return = new node_sqrt(id_to_assign);
        break;
      case SUB:
        to_return = new node_sub(id_to_assign);
        break;
      case VIRTUAL:
        to_return = new node_virtual(id_to_assign);
        break;
      case NOISE:
        to_return = new node_noise(id_to_assign, number_of_inputs, number_of_noises);
        number_of_inputs++;
        number_of_noises++;
        break;
      case TRIM:
        to_return = new node_trim(id_to_assign);
        break;
      default:
        error("Unrecognized opcode.");
    }
    number_of_nodes++;
    return to_return;
  }

  node*
  factory::new_node(NODE_OPCODE opcode, CMP_TYPE comparison){
    unsigned id_to_assign = number_of_nodes;
    node* to_return = NULL;
    switch (opcode){
      case CMP:
        to_return = new node_cmp(id_to_assign, comparison);
        break;
      default:
        error("Too many arguments in function.");
    }
    number_of_nodes++;
    return to_return;
  }

  node*
  factory::new_node(NODE_OPCODE opcode, double value){
    unsigned id_to_assign = number_of_nodes;
    node* to_return = NULL;
    switch (opcode){
      case CONST:
        to_return = new node_const(id_to_assign, value);
        break;
      default:
        error("Too many arguments in function.");
    }
    number_of_nodes++;
    return to_return;
  }

  void
  factory::reset(){
    number_of_nodes = 0;
  }

}





