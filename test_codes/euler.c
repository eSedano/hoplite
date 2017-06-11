// inputs: a, nx, ny, drhoe, drhovn, vx, vy
double euler(double a, double nx, double ny, double drhovx,  double drhovy, double drhoe, double vx, double vy, double h, double drho){
    double pR089 = nx * drhovx;
    double pR090 = ny * drhovy;
    double drhovn = pR089 + pR090;
    
    double pR103 = vx * vx;
    double pR104 = vy * vy;
    double vv = pR103 + pR104;
    double pR107 = nx * vx;
    double pR108 = ny * vy;
    double vn = pR107 + pR108;

    double pR113 = vx * drhovx;
    double pR114 = vy * drhovy;
    double vdrhov = pR113 + pR114;
    double pR117 = h - vv;
    double pR118 = drho * pR117;
    double pR119 = pR118 - drhoe;
    double tmp0 = pR119 + vdrhov; 
    double pR120 = tmp0 * 0.4;
    double wave2_0 = pR120 / a;
    double pR121 = vn * drho;
    double tmp1 = drhovn - pR121;
    double tmp2 = wave2_0 - drho;
    double pR122 = tmp1 / a;
    double pR123 = pR122 - tmp2;
    double a3 = 0.5 * pR123;
    double vna = vn * a;
    double pR124 = h - vna;
    double wave1_0 = tmp2 - a3;
    double wave1_1 = wave1_0 * pR124;

    return wave1_1;
}