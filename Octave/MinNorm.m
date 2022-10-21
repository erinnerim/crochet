function mni = MinNorm(XY, point, ind);
  D = XY(:,point,ind) - XY(:,:,ind-1);
  Del = zeros(size(XY)(2),1);
  for i=1:size(XY)(2)
    Del(i)=norm(D(:,i));
  endfor
  [mn, mni] = min(Del);
endfunction
