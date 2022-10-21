function c = CrochetTorus(N, R, r)
  t = 1:N;
  th = t*pi/N;
  r_ = R - r*cos(th);
  c = round(abs(2*pi*r_));
endfunction
