/**
  LLVM I/O Interface
  io_interface_llvm.hpp
  Purpose: Implements the base class io_interface for interfacing with the LLVM compiler framework.
    Extracts the DFG from the LLVM-IR and maps the output wordlengths in the metadata of
    each instruction.

  @author  Enrique Sedano
  @version  0.13.09

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_IO_INTERFACE_LLVM_HPP
#define HOPLITE_IO_INTERFACE_LLVM_HPP

#include "llvm/Value.h"
#include "llvm/Function.h"
#include "llvm/Instruction.h"
#include "llvm/Instructions.h"
#include "llvm/Intrinsics.h"
#include "llvm/IntrinsicInst.h"

#include "llvm/DerivedTypes.h"

#include "llvm/ADT/ValueMap.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/InstIterator.h"

#include "io_interface.hpp"
#include "../hoplite_utilities.hpp"

namespace hoplite {

  // extra definitions
  #define llvm_const_op_iterator llvm::User::const_op_iterator
  #define llvm_arg_iterator llvm::Function::const_arg_iterator
  #define llvm_inst_iterator llvm::inst_iterator

  class io_interface_llvm : public io_interface {
  public:
    io_interface_llvm();
    ~io_interface_llvm();

    void initialize(llvm::Function &F);

    void read_system_graph(system_graph* destination);

  private:
    /**
      LLVM function to interact with.
    */
    llvm::Function* llvm_function;

    /**
      Equivalent DFG node ID for each LLVM instruction.
    */
    std::map<llvm::Value*, unsigned> llvm_instructions_to_node_ids;

    /**
      Equivalent LLVM instruction for each DFG node.
      The inverse of llvm_instructions_to_nodes.
    */
    std::map<unsigned, llvm::Value*> node_ids_to_llvm_instructions;

    std::map<llvm::BasicBlock*, unsigned> basic_blocks_to_bbid;

    void read_inputs_and_outputs(system_graph* destination);
    void read_intermediate_nodes(system_graph* destination);

    void read_and_register_io_node(llvm::Value* to_read, system_graph* destination);
    unsigned read_io_node(llvm::Value* to_read, system_graph* destination);
    void register_node(llvm::Value* llvm_instruction, unsigned id);

    void read_and_register_node(llvm::Value* to_read, system_graph* destination);
    unsigned read_node(llvm::Value* to_read, system_graph* destination);

    void link_node_in_graph(llvm::Value* llvm_instruction, system_graph* destination);

    double get_const_value(llvm::Value* instruction);
    CMP_TYPE get_comparison_type(llvm::Value* instruction);

    NODE_OPCODE get_opcode_from_instruction(llvm::Value* instruction);

    std::list<llvm::Value*>* build_operators_list(llvm::Instruction* instruction);

    void read_and_register_constant(llvm::Value* to_read, system_graph* destination, unsigned bb_id);

    unsigned read_constant(llvm::Value* to_read, system_graph* destination, unsigned bb_id);
  
    void link_store_operation(llvm::Value* llvm_instruction, system_graph* destination);
    void link_branch_operation(llvm::Value* llvm_instruction, system_graph* destination);
    void link_phi_operation(llvm::Value* llvm_instruction, system_graph* destination);
    void link_regular_operation(llvm::Value* llvm_instruction, system_graph* destination);

    unsigned get_id_for_basic_block(llvm::BasicBlock* bb);
  };

}
#endif
