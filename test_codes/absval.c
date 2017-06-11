double absval(double x, double y){
  double f = (x * x) - y;
  if (f < 0) f = -f;

  return f;
}

