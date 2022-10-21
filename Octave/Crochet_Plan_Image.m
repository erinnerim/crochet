clc; clear;
H = [7, 17, 13, 17, 19]

L = zeros(2, H(1));
size_L = size(L)
r = 10*(1:5)
start = 1;

for i=1:2

N = H(i);
t = 1:N;
th = (2*pi/N)*t;


L(1,start:N+start-1) = r(i)*cos(th);
L(2,start:N+start-1) = r(i)*sin(th);

start = start + N;


endfor
plot(L(1,:), L(2,:))
hold on;

%use for first point of 11-gon
L

C = zeros(2,2)

mn = 1000000
h = 0;
D = L(:,8) - L(:,1:7)

K = zeros(7,1);
for i=1:7
K(i) = norm(D(:,i));
endfor
K
[h, ih] = min(K)

C(:,1) = L(:,8);
C(:,2) = L(:,ih);
C



plot(C(1,:), C(2,:))

axis("square")
