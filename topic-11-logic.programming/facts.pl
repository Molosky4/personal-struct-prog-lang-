% define people

person(greg).
person(susan).

% define family relationships

son(greg,david).
son(david,jack).
son(david,almeda).

daughter(kim, david).
daughter(steph, david).

child(X,Y) :- son(X,Y).
child(X,Y) :- daughter(X,Y).

grandchild(greg,lois).

grandchild(X, Y) :- child(X, Z), child(Z, Y).

grandson(X, Y) :- son(X, Z), child(Z, Y).

grandson(X,Y) :- grandchild(X,Y), son(X,Z).
