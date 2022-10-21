function XY = Concentric(H,r)

  XY = zeros(2, max(H), size(H)(2));

  size_XY = size(XY)

  for i=1:size(H)(2)
    N = H(i);
    t = 1:N;
    th = t*(2*pi/N)+pi*i;

    XY(1, (1:N), i) = r(i)*cos(th);
    XY(2, (1:N), i) = r(i)*sin(th);
  endfor
endfunction
