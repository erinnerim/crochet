function c = CrochetSphere(N, R)
x=1:N;
t = x*pi/N;
r = R*sin(t);
c = round(abs(2*pi*r));
x = round(2*pi*R*cos(t));

endfunction