% Upper partition function

upper([],_,[]).
upper([H|T], V, [H|Rest]) :- H > V, upper(T, V, Rest).
upper([H|T], V, Rest) :- H =< V, upper(T, V, Rest).

lower([],_,[]).
lower([H|T], V, [H|Rest]) :- H < V, lower(T, V, Rest).
lower([H|T], V, Rest) :- H >= V, lower(T, V, Rest).

append(X,Y,Z,T) :- append(X,Y,Temp),append(Temp,Z,T).

equal([],_,[]).
equal([H|T], V, [H|Rest]) :- H =:= V, equal(T, V, Rest).
equal([H|T], V, Rest) :- H =\= V, equal(T, V, Rest).

qsort([], []).
qsort([V|Rest],Sorted) :- 
  lower(Rest,V,Lower),
  equal([V|Rest],V,Equal),
  upper(Rest,V,Upper),
  qsort(Lower,SortedLower),
  qsort(Upper,SortedUpper),
  append(SortedLower,Equal,Temp),
  append(Temp, SortedUpper, Sorted).
