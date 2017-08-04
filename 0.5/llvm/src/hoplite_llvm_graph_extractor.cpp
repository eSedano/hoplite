//===- hoplite_llvm_graph_extractor.cpp - Graph extractor utility for the HOPLITE framework ---------------===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===------------------------------------------------------------------------------------------------------===//
//
//
//===------------------------------------------------------------------------------------------------------===//

#include "llvm/Function.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"

#include "llvm/Transforms/hoplite_llvm_graph_extractor/io_interface/io_interface_llvm.hpp"
#include "llvm/Transforms/hoplite_llvm_graph_extractor/hoplite_utilities.hpp"
#include "llvm/Transforms/hoplite_llvm_graph_extractor/system_graph/system_graph.hpp"
#include "llvm/Transforms/hoplite_llvm_graph_extractor/python/python_graph_extractor.hpp"

using namespace llvm;

namespace {
  struct hoplite_llvm_graph_extractor : public FunctionPass {
    static char ID;
    hoplite::io_interface_llvm*     ioi;
    hoplite::system_graph*           sg;
    hoplite::python_graph_extractor* gx;

    hoplite_llvm_graph_extractor() : FunctionPass(ID) {
      ioi = new hoplite::io_interface_llvm();
      sg =  new hoplite::system_graph();
      gx =  new hoplite::python_graph_extractor();
    }

    virtual bool runOnFunction(Function &F) {
      ioi->initialize(F);
      ioi->read_system_graph(sg);
      sg->link_basic_blocks();
      gx->extract(sg, "system_graph_desc.hop");
      return false;
    }

  };
}

char hoplite_llvm_graph_extractor::ID = 0;
static RegisterPass<hoplite_llvm_graph_extractor> X("hoplite_gx", "HOPLITE graph extractor utility.");
