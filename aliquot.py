#!/usr/bin/env python3

def factor(integer):
    returnee = set([1]);
    for n in range(2, (integer // 2) + 1):
        if not integer % n == 0: continue;
        n2 = integer / n;
        if n2 <= n: break;
        returnee.add(n);
        returnee.add(n2);
    return returnee;

def populate_aliquot(integer):
    factors = factor(integer);
    aliquot = sum(factors);
    type = None;
    if aliquot == integer: type = "Perfect";
    elif aliquot > integer: type = "Abundant";
    elif aliquot < integer: type = "Deficient";
    save_aliquot(integer, factors, aliquot, type);
    return aliquot;

def populate_aliquots(first_integer):
    integer = first_integer;

def save_aliquot(integer, factors, successor, type):
    pass

print(list(factor(124)));

