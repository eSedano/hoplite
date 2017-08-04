double casoCuatro(double a, double b, double c){
  double f;
  double d = (a * b) + 5;
  f = a + (d * c);
  double r = b * b;
  double k = r - f;
  double s = k + b;
  if (r > f) {
    r = r  + f;
  } else {
    r = r * 2.75;
    f++;
    if (s > 5 * b) {
      r = r  + f;
    } else {
      r = r * 2.75;
      f--;
    }
  }
  return f * k + r;
}