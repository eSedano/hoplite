/**
  HOPLITE utilities.
  hoplite.hpp
  Purpose: Implements auxiliar utilities for the HOPLITE framework.

  @author  Enrique Sedano
  @version  0.13.08

  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
*/

#ifndef HOPLITE_HOPLITE_UTILITIES_HPP
#define HOPLITE_HOPLITE_UTILITIES_HPP

#include <string>
#include <stdio.h>
#include <cstdlib>

namespace hoplite {
  void error(const char* message);

  void warning(const char* message);

  void debug(const char* message);
}
#endif
