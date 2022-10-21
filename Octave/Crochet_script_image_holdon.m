clc; clear;
H = CrochetTorus(22,22,11)  
MAX = max(H);
r = 70 + 10*(0:size(H)(2)-1);

XY = Concentric(H, r);
XY(:,:,5);

for i=1:size(H)(2)
  range = 1:H(i);
  %plot(XY(1,range,i), XY(2,range,i), "pk");
  hold on;
endfor

%for XY(:,1,2)
MNIS = zeros(MAX, size(H)(2)-1);
for ring = 2:size(H)(2)
for ind = 1:MAX
  MNIS(ind, ring-1) = MinNorm(XY,ind,ring);
endfor
endfor
MNIS

for ring=2:size(H)(2)
for i=1:H(ring)
  C = [XY(:,i,ring), XY(:,MNIS(i,ring-1),ring-1)];
  plot(C(1,:), C(2,:),"k");
endfor
endfor


axis("square");
hold off;