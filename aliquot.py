#!/usr/bin/env python3

def factor(integer):
    returnee = set([1]);
    for n in range(2, (integer // 2) + 1):
        if not integer % n == 0: continue;
        n2 = integer // n;
        if n2 < n: break;
        returnee.add(n);
        returnee.add(n2);
    return returnee;


aliquot_data = dict();

def populate_aliquot_sequence(integer, trace=[], prog_callback=None):
    if prog_callback: prog_callback(integer, trace);

    factors = factor(integer);
    aliquot = sum(factors);

    type = None;
    if aliquot in trace:
        if len(trace) == 1: type = "Amicable";
        else: type = "Sociable";
        for prev_integer in trace:
            update_aliquot_type(prev_integer, type);
    elif aliquot < integer: type = "Deficient";
    elif aliquot > integer: type = "Abundant";
    else:
        type = "Perfect";
        if aliquot != 1:
            for prev_integer in trace:
                update_aliquot_type(prev_integer, "Aspiring");

    save_aliquot(integer, factors, aliquot, type);

    trace.append(integer);
    if aliquot in aliquot_data: return trace;
    elif type == "Perfect": return trace;
    else: return populate_aliquot_sequence(aliquot, trace, prog_callback);


def update_aliquot_type(integer, new_type):
    aliquot_data[integer][2] = new_type;

def save_aliquot(integer, factors, successor, type):
    aliquot_data[integer] = [factors, successor, type];

def print_aliquot_data():
    for integer in aliquot_data:
        [factors, successor, type] = aliquot_data[integer];
        print(integer, factors, successor, type, sep=" %% ");


if __name__ == "__main__":
    from sys import argv;
    from time import time;
    def prog_calback(integer, trace):
        print(
            "{}Computing".format("\b" * 40), integer,
            "after", len(trace), "numbers.",
            end="", flush=True);
    for arg in argv[1:]:
        try:
            start = time();
            trace = populate_aliquot_sequence(
                int(arg), prog_callback=prog_callback);
            end = time();
            elapsed_ms = (end - start) / 1000;
            print(
                    "{}Elapsed".format("\b" * 40),
                    "{}ms".format(elapsed_ms),
                    "for", len(trace), "new numbers.");
        except ValueError: continue;
    print_aliquot_data();

