/**
  I/O interface
  io_interface.hpp
  Purpose: Base class for interfacing HOPLITE to external tools.

  @author  Enrique Sedano
  @version  0.14.01

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_IO_INTERFACE_HPP
#define HOPLITE_IO_INTERFACE_HPP

#include "../system_graph/system_graph.hpp"

namespace hoplite{

  class io_interface{

  public:
    virtual ~io_interface(){};
    virtual void read_system_graph(system_graph* destination) = 0;
  };

}
#endif
