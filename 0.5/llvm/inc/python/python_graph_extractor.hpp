/**
  Python System Graph Extractor
  python_graph_extractor.hpp
  Purpose: Reads a system graph and generates a Python dictionary with its spec.

  @author  Enrique Sedano
  @version  0.14.07

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_PYTHON_GRAPH_EXTRACTOR_HPP
#define HOPLITE_PYTHON_GRAPH_EXTRACTOR_HPP

#include <iostream>
#include <fstream>
#include <string>
// #include <map>
// #include <set>

#include "../hoplite_utilities.hpp"
#include "../system_graph/system_graph.hpp"

namespace hoplite {
  class python_graph_extractor {
  public:
    void extract(system_graph* sg, std::string d);

  private:
    system_graph* source;
    std::string   destination;

    void extract_bbs();
    void extract_nodes();
    void extract_inputs();
    void extract_outputs();

    void extract_node(node* n);
    void extract_bb(basic_block* bb);

    std::string op_to_str(NODE_OPCODE op);
    std::string cmp_to_str(CMP_TYPE cmp);
  };
}

#endif
