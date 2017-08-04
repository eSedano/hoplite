#include "llvm/Transforms/hoplite_llvm_graph_extractor/hoplite_utilities.hpp"

namespace hoplite {

  void
  error(const char* message){
    printf("HOPLITE error: ");
    printf("%s", message);
    printf("\n");
    exit(1);
  }

  void
  warning(const char* message){
    printf("HOPLITE warning: ");
    printf("%s", message);
    printf("\n");
  }

  void
  debug(const char* message){
//  #ifdef HOPLITE_DEBUG
    printf("HOPLITE debug: ");
    printf("%s", message);
    printf("\n");
//  #endif
  }

}
