#include "llvm/Transforms/hoplite_llvm_graph_extractor/io_interface/io_interface_llvm.hpp"

namespace hoplite {
  io_interface_llvm::io_interface_llvm(){
  }

  io_interface_llvm::~io_interface_llvm(){

  }

  void
  io_interface_llvm::initialize(llvm::Function &F){
    llvm_function = &F;
  }

  void
  io_interface_llvm::read_system_graph(system_graph* destination){
    read_inputs_and_outputs(destination);
    read_intermediate_nodes(destination);
    destination->declutter();
  }

  void
  io_interface_llvm::read_inputs_and_outputs(system_graph* destination){
    llvm_arg_iterator it;
    llvm_arg_iterator limit = llvm_function->arg_end();

    for (it = llvm_function->arg_begin(); it != limit; ++it){
      read_and_register_io_node(const_cast<llvm::Argument*>(&*it),destination);
    }
  }

  void
  io_interface_llvm::read_and_register_io_node(llvm::Value* to_read, system_graph* destination){
    debug("Read and register I/O node.");
    unsigned new_node_id;
    new_node_id = read_io_node(to_read, destination);
    //printf("Node ID: %u\n", new_node_id);
    llvm::errs() << "(" << new_node_id << ")" << *to_read << "\n";
    register_node(to_read, new_node_id);
  }

  unsigned
  io_interface_llvm::read_io_node(llvm::Value* to_read, system_graph* destination){
    debug("Reading I/O node.");
    // If isPointerTy, argument is an output. Otherwise it is an input.
    NODE_OPCODE opcode = (to_read->getType()->isPointerTy()) ? OUTPUT : INPUT;
    // llvm::errs() << "I/O value: " << *to_read << "\n";
    return destination->new_node(opcode);
  }

  void
  io_interface_llvm::register_node(llvm::Value* llvm_instruction, unsigned id){
    debug("Registering node.");
    llvm_instructions_to_node_ids[llvm_instruction] = id;
    node_ids_to_llvm_instructions[id] = llvm_instruction;
  }

  void
  io_interface_llvm::read_intermediate_nodes(system_graph* destination){
    llvm_inst_iterator it;
    llvm_inst_iterator limit = llvm::inst_end(llvm_function);

    for (it = llvm::inst_begin(llvm_function); it != limit; ++it){
      read_and_register_node((&*it),destination);
    }
    for (it = llvm::inst_begin(llvm_function); it != limit; ++it){
        link_node_in_graph(&*it,destination);
    }
  }

  void
  io_interface_llvm::read_and_register_node(llvm::Value* to_read, system_graph* destination){
    debug(" ");
    debug("Read and register node.");
    unsigned new_node_id;
    new_node_id = read_node(to_read, destination);
    register_node(to_read, new_node_id);
  }
  
  unsigned
  io_interface_llvm::read_node(llvm::Value* to_read, system_graph* destination){
    debug("Reading node.");

    CMP_TYPE comparison;
    unsigned id;

    NODE_OPCODE opcode = get_opcode_from_instruction(to_read);
    unsigned bb_id = get_id_for_basic_block(((llvm::Instruction*)(to_read))->getParent());
    switch (opcode){
      case CMP:
        comparison = get_comparison_type(to_read);
        id = destination->new_node(opcode, comparison, bb_id);
        break;
      case OUTPUT: // Inputs and outputs are always kept in BB 0.
        id = destination->new_node(opcode);
        break;
      default:
        id = destination->new_node(opcode, bb_id);
        break;
    }
    llvm::errs() << "(" << id << ")" << *to_read << "\n";
    return id;
  }

  void
  io_interface_llvm::read_and_register_constant(llvm::Value* to_read, system_graph* destination, unsigned bb_id){
    debug("Read and register constant.");
    unsigned new_node_id;
    new_node_id = read_constant(to_read, destination, bb_id);
    register_node(to_read, new_node_id);
  }

  unsigned
  io_interface_llvm::read_constant(llvm::Value* to_read, system_graph* destination, unsigned bb_id){
    debug("Reading constant.");

    double const_value;
    const_value = get_const_value(to_read);
    return destination->new_node(CONST, const_value, bb_id);
  }

  void
  io_interface_llvm::link_node_in_graph(llvm::Value* llvm_instruction, system_graph* destination){
    debug("Linking node.");

    switch (((llvm::Instruction*)llvm_instruction)->getOpcode()){
      case llvm::Instruction::Store:
        link_store_operation(llvm_instruction, destination);
        break;
      case llvm::Instruction::Br:
        link_branch_operation(llvm_instruction, destination);
        break;
      case llvm::Instruction::PHI:
        link_phi_operation(llvm_instruction, destination);
        break;
      default:
        link_regular_operation(llvm_instruction, destination);
    }
    return;
  }

  void
  io_interface_llvm::link_store_operation(llvm::Value* llvm_instruction, system_graph* destination){
    std::list<llvm::Value*>* llvm_predecessors = build_operators_list((llvm::Instruction*)llvm_instruction);
    // Store operations have two operators: STORE _from_ _to_.
    // If treated regularly, both _from_ and _to_ would appear as
    // predecessors of the STORE operation, and no successors
    // would be found. Being _to_ an OUTPUT slot, here the
    // _from_ instruction and the _to_ slot are directly connected.
    unsigned id_from = llvm_instructions_to_node_ids[const_cast<llvm::Value*>(llvm_predecessors->front())];
    unsigned id_to = llvm_instructions_to_node_ids[const_cast<llvm::Value*>(llvm_predecessors->back())];
    destination->relate_nodes(id_from, id_to);
  }

  void
  io_interface_llvm::link_branch_operation(llvm::Value* llvm_instruction, system_graph* destination){
    unsigned number_of_successors = ((llvm::BranchInst*)llvm_instruction)->getNumSuccessors();
    unsigned node_id = llvm_instructions_to_node_ids[llvm_instruction];

    unsigned bb_id;
    for (unsigned i = 0; i < number_of_successors; ++i){
      bb_id = get_id_for_basic_block(((llvm::BranchInst*)llvm_instruction)->getSuccessor(i));
      destination->relate_branch(node_id, bb_id);
    }

    unsigned predecessor_id;
    if (((llvm::BranchInst*)llvm_instruction)->isConditional()){
      predecessor_id = llvm_instructions_to_node_ids[((llvm::BranchInst*)llvm_instruction)->getCondition()];
      destination->relate_nodes(predecessor_id, node_id);
    } else {
      bb_id = basic_blocks_to_bbid[((llvm::Instruction*)(llvm_instruction))->getParent()];
      unsigned new_id = destination->new_node(CMP, CMP_TRUE, bb_id);
      destination->relate_nodes(new_id, node_id);
    }
  }

  void
  io_interface_llvm::link_phi_operation(llvm::Value* llvm_instruction, system_graph* destination){
    unsigned number_of_predecessors = ((llvm::PHINode*)llvm_instruction)->getNumIncomingValues();

    llvm::Value* from;
    unsigned id_from;
    unsigned bbid_from;
    unsigned id_to = llvm_instructions_to_node_ids[llvm_instruction];
    unsigned bbid_to = get_id_for_basic_block(((llvm::Instruction*)llvm_instruction)->getParent());

    for (unsigned i = 0; i < number_of_predecessors; ++i){
        from = ((llvm::PHINode*)llvm_instruction)->getIncomingValue(i);
        if (llvm::isa<llvm::Constant>(from)){
          if (((from)->getName() != "fabs") && ((from)->getName() != "sqrt")){
            // A constant value is found. Thus, a new node has to be created.
            read_and_register_constant(from, destination, bbid_to);
            id_from = llvm_instructions_to_node_ids[from];
          }
        }
        id_from = llvm_instructions_to_node_ids[from];
        bbid_from = basic_blocks_to_bbid[((llvm::PHINode*)llvm_instruction)->getIncomingBlock(i)];
        destination->relate_nodes(id_from, bbid_from, id_to);
    }
  }

  void
  io_interface_llvm::link_regular_operation(llvm::Value* llvm_instruction, system_graph* destination){
    std::list<llvm::Value*>* llvm_predecessors = build_operators_list((llvm::Instruction*)llvm_instruction);

    unsigned id_from;
    unsigned id_to = llvm_instructions_to_node_ids[llvm_instruction];
    unsigned bbid_from = get_id_for_basic_block(((llvm::Instruction*)llvm_instruction)->getParent());

    std::list<llvm::Value*>::iterator it;
    std::list<llvm::Value*>::iterator limit = llvm_predecessors->end();

    for (it = llvm_predecessors->begin(); it != limit; ++it){
      if (llvm::isa<llvm::Constant>(*it)){
        if (((*it)->getName() != "fabs") && ((*it)->getName() != "sqrt")){
          // A constant value is found. Thus, a new node has to be created.
          read_and_register_constant(*it, destination, bbid_from);
          id_from = llvm_instructions_to_node_ids[*it];
          destination->relate_nodes(id_from, id_to);
        }
      } else {
        id_from = llvm_instructions_to_node_ids[*it];
        //printf("%u\n", id_from);
        destination->relate_nodes(id_from, id_to);
      }
    }
  }

  std::list<llvm::Value*>*
  io_interface_llvm::build_operators_list(llvm::Instruction* instruction){
    std::list<llvm::Value*>* operators_list = new std::list<llvm::Value*>();
    llvm_const_op_iterator it;
    llvm_const_op_iterator limit = instruction->op_end();
    for (it = instruction->op_begin(); it != limit; ++it) {
      operators_list->push_back(*it);
    }
    return operators_list;
  }

  double
  io_interface_llvm::get_const_value(llvm::Value* instruction){
    double value = 0;
    // TODO: Get constant value from node.
    if (llvm::isa<llvm::ConstantFP>(*instruction)){
      const llvm::APFloat *floating_constant_value = &llvm::cast<llvm::ConstantFP>(instruction)->getValueAPF();
      value = floating_constant_value->convertToDouble();
    } else if (llvm::isa<llvm::ConstantInt>(*instruction)){
      const llvm::APInt *integer_constant_value = &llvm::cast<llvm::ConstantInt>(instruction)->getValue();
      value = integer_constant_value->roundToDouble();
      printf("%lf\n", value);
    } else {
      error("Unsupported constant value type.");
    }
    return value;
  }

  CMP_TYPE
  io_interface_llvm::get_comparison_type(llvm::Value* instruction){
    llvm::CmpInst::Predicate comparison = ((llvm::CmpInst*)instruction)->getPredicate();
    CMP_TYPE to_return = EQ;

    switch (comparison){
      case llvm::CmpInst::ICMP_EQ:
      case llvm::CmpInst::FCMP_OEQ:
      case llvm::CmpInst::FCMP_UEQ:
        to_return = EQ;
        break;

      case llvm::CmpInst::ICMP_NE:
      case llvm::CmpInst::FCMP_ONE:
      case llvm::CmpInst::FCMP_UNE:
        to_return = NEQ;
        break;

      case llvm::CmpInst::ICMP_UGT:
      case llvm::CmpInst::ICMP_SGT:
      case llvm::CmpInst::FCMP_OGT:
      case llvm::CmpInst::FCMP_UGT:
        to_return = GT;
        break;

      case llvm::CmpInst::ICMP_UGE:
      case llvm::CmpInst::ICMP_SGE:
      case llvm::CmpInst::FCMP_OGE:
      case llvm::CmpInst::FCMP_UGE:
        to_return = GTE;
        break;

      case llvm::CmpInst::ICMP_ULT:
      case llvm::CmpInst::ICMP_SLT:
      case llvm::CmpInst::FCMP_OLT:
      case llvm::CmpInst::FCMP_ULT:
        to_return = LT;
        break;

      case llvm::CmpInst::ICMP_ULE:
      case llvm::CmpInst::ICMP_SLE:
      case llvm::CmpInst::FCMP_OLE:
      case llvm::CmpInst::FCMP_ULE:
        to_return = LTE;
        break;

      case llvm::CmpInst::FCMP_FALSE:
        to_return = CMP_FALSE;
        break;

      case llvm::CmpInst::FCMP_TRUE:
        to_return = CMP_TRUE;
        break;

      default:
        error("Comparison type not recognized.");
    }
    return to_return;
  }

  NODE_OPCODE
  io_interface_llvm::get_opcode_from_instruction(llvm::Value* instruction){
    llvm::Function *called_function;
    NODE_OPCODE to_return = VIRTUAL;

    switch(((llvm::Instruction*)instruction)->getOpcode()) {
      case llvm::Instruction::FAdd:
      case llvm::Instruction::Add:
        to_return = ADD;
        break;

      case llvm::Instruction::FSub:
      case llvm::Instruction::Sub:
        to_return = SUB;
        break;

      case llvm::Instruction::FMul:
      case llvm::Instruction::Mul:
        to_return = MUL;
        break;

      case llvm::Instruction::FDiv:
      case llvm::Instruction::UDiv:
      case llvm::Instruction::SDiv:
        to_return = DIV;
        break;

      case llvm::Instruction::FCmp:
      case llvm::Instruction::ICmp:
        to_return = CMP;
        break;

      case llvm::Instruction::Select:
        to_return = SEL;
        break;

      case llvm::Instruction::Call: {
        called_function = llvm::cast<llvm::CallInst>(*instruction).getCalledFunction();
        if ((called_function->getIntrinsicID() == llvm::Intrinsic::sqrt) || (called_function->getName() == "sqrt")){
          to_return = SQRT;
        } else if (called_function->getName() == "fabs") {
          to_return = ABS;
        }
      }
        break;

      case llvm::Instruction::Store:
      case llvm::Instruction::Ret:
        to_return = OUTPUT;
        break;

      case llvm::Instruction::ZExt:
      case llvm::Instruction::SExt:
      case llvm::Instruction::Trunc:
      case llvm::Instruction::FPTrunc:
      case llvm::Instruction::FPExt:
      case llvm::Instruction::FPToUI:
      case llvm::Instruction::FPToSI:
      case llvm::Instruction::UIToFP:
      case llvm::Instruction::SIToFP:
        to_return = VIRTUAL;
        break;

      case llvm::Instruction::Br:
        to_return = BR;
        break;

      case llvm::Instruction::PHI:
        to_return = PHI;
        break;

      case llvm::Instruction::GetElementPtr:
        to_return = GET_ELEMENT_PTR;
        break;

      case llvm::Instruction::Load:
        to_return = LOAD;
        break;

      case llvm::Instruction::Switch:
        to_return = SWITCH;
        break;

      default:
        error("Instruction not supported. Please check bitcode file.\n");
      }
      return to_return;
  }

  unsigned
  io_interface_llvm::get_id_for_basic_block(llvm::BasicBlock* bb){
    unsigned size = basic_blocks_to_bbid.size();
    std::map<llvm::BasicBlock*, unsigned>::iterator it = basic_blocks_to_bbid.find(bb);

    // If the BB hasn't been registered before, register it now.
    if (it == basic_blocks_to_bbid.end())
      basic_blocks_to_bbid[bb] = size+1;

    return basic_blocks_to_bbid[bb];
  }

}
