double casoDos(double a, double b, double c){
	double f;
	double d = (a * b) + 5;
	f = a + (d * c);
	double r = b * b;
	if (r > f) {
		r = r  + f;
	} else {
		r = r * 2.75;
		f++;
	}
	double k = r - f;
	return k * k;
}