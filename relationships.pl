:- dynamic parent/2.
:- dynamic male/1.
:- dynamic female/1.
:- dynamic uncle/2.

/* parents */
father(F,C)        :- parent(F,C), male(F).
mother(M,C)        :- parent(M,C), female(M).

/* children */
child(C,P)         :- parent(P,C).
son(S,P)           :- child(S,P),   male(S).
daughter(D,P)      :- child(D,P),   female(D).

/* siblings pwede half */
sibling(X,Y)       :- parent(P,X), parent(P,Y), X \= Y.

brother(B,Sib)     :- sibling(B,Sib), male(B).
sister(S,Sib)      :- sibling(S,Sib), female(S).

/* grand */
grandparent(GP,C)  :- parent(GP,P), parent(P,C).
grandfather(GF,C)  :- grandparent(GF,C), male(GF).
grandmother(GM,C)  :- grandparent(GM,C), female(GM).

/* relatives like ancestor or descendant */
ancestor(A,D)      :- parent(A,D).
ancestor(A,D)      :- parent(A,X), ancestor(X,D).
descendant(D,A)    :- parent(A,D).
descendant(D,A)    :- parent(A,X), descendant(D,X).

/* tito tita by BLOOD no marriage rules.... */
uncle(U,N)         :- parent(P,N), sibling(U,P), male(U).
aunt(A,N)          :- parent(P,N), sibling(A,P), female(A).

/* are x and y the parents of this child */
parents_of(P1,P2,C) :- parent(P1,C), parent(P2,C), P1 \= P2.

/* relative relationships */
relative(R1,R2)    :- ancestor(R1, R2); descendant(R1, R2); ((ancestor(R1, X), ancestor(R2, X)); (descendant(R1, X), descendant(R2, X))), R1 \= R2.
