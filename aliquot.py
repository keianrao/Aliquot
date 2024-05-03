#!/usr/bin/env python3

import sqlite3;
import os.path;

aliquot_data = dict();
dbconn = None;
dbcursor = None;

def startup_db():
    is_new = not os.path.isfile("aliquot.sqlite");
    global dbconn, dbcursor;
    dbconn = sqlite3.connect("aliquot.sqlite");
    dbcursor = dbconn.cursor();
    if is_new:
        dbcursor.execute("""
            CREATE
            TABLE Aliquot
            (integer, factors, successor, type,
            UNIQUE(integer));""");
        dbconn.commit();

def shutdown_db():
    global dbconn, dbcursor;
    dbcursor.close();
    dbconn.close();
    dbcursor = None;
    dbconn = None;

def update_aliquot_type(integer, new_type):
    assert dbconn;
    dbcursor.execute("""
        UPDATE Aliquot
        SET type = ?
        WHERE integer = ?;""",
        [new_type, integer]);
    dbconn.commit();

def save_aliquot(integer, factors, successor, type):
    assert dbconn;
    factors_str = ",".join(map(str, factors));
    dbcursor.execute("""
        INSERT
        INTO Aliquot
        VALUES (?, ?, ?, ?);""",
        [integer, factors_str, successor, type]);
    dbconn.commit();

def aliquot_computed(integer):
    results = dbcursor.execute("""
        SELECT 'T'
        FROM Aliquot
        WHERE integer = ?;""",
        [integer]);
    return bool(results.fetchone());

def get_predecessors(integer):
    sql = """
        SELECT integer
        FROM Aliquot
        WHERE successor = ?""";
    returnee = set();
    while True:
        results = dbcursor.execute(sql, [integer]);
        line = results.fetchone();
        if not line: break;
        [predecessor] = line;
        prev_len = len(returnee);
        returnee.add(predecessor);
        if len(returnee) == prev_len: break;
        integer = predecessor;
    return returnee;

def get_successors(integer):
    sql = """
        SELECT successor
        FROM Aliquot
        WHERE integer = ?;""";
    original = integer;
    returnee = [];
    while True:
        results = dbcursor.execute(sql, [integer]);
        line = results.fetchone();
        if not line: break;
        [successor] = line;
        if successor == integer: break;
        if successor in returnee: break;
        if successor == original: break;
        returnee.append(successor);
        integer = successor;
    return returnee;

def get_aliquot(integer):
    assert dbconn;
    results = dbcursor.execute("""
        SELECT *
        FROM Aliquot
        WHERE integer = ?;""",
        [integer]);
    line = results.fetchone();
    if not line: return line;
    line = list(line);
    factors_str = line[1];
    factors = list(map(int, factors_str.split(",")));
    line[1] = factors;
    return line;


def factor(integer):
    returnee = set([1]);
    for n in range(2, (integer // 2) + 1):
        if not integer % n == 0: continue;
        n2 = integer // n;
        if n2 < n: break;
        returnee.add(n);
        returnee.add(n2);
    return returnee;


def populate_aliquot_sequence(integer, prog_callback=None):
    trace = [];
    while True:
        # Recursion by loop to allow more than 900 iterations.
        try:
            if aliquot_computed(integer): break;
            if prog_callback: prog_callback(integer, trace);
    
            factors = factor(integer);
            aliquot = sum(factors);
            predecessors = get_predecessors(integer);
        
            type = None;
            if aliquot in predecessors:
                if len(predecessors) == 1: type = "Amicable";
                else: type = "Sociable";
            elif aliquot < integer: type = "Deficient";
            elif aliquot > integer: type = "Abundant";
            else: type = "Perfect";
    
            if type == "Amicable" or type == "Sociable":
                for prev_integer in predecessors:
                    update_aliquot_type(prev_integer, type);
            if type == "Perfect" and not aliquot == 1:
                for prev_integer in predecessors:
                    update_aliquot_type(prev_integer, "Aspiring");
            save_aliquot(integer, factors, aliquot, type);
        
            trace.append(integer);
            if type == "Perfect": break;
            elif type == "Amicable": break;
            elif type == "Sociable": break;
            else: integer = aliquot;
        except KeyboardInterrupt: break;
    return trace;


if __name__ == "__main__":
    from sys import argv;
    from time import time;
    def prog_callback(integer, trace):
        print(
            "{}Computing".format("\b" * 40), integer,
            "after", len(trace), "numbers.",
            end="", flush=True);
    def print_aliquot_data(integer):
        [integer, factors, successor, type] = get_aliquot(integer);
        print(integer, factors, successor, type, sep=" % ");
    startup_db();
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
            print_aliquot_data(int(arg));
            for integer in get_successors(int(arg)):
                print_aliquot_data(integer);
        except ValueError: continue;
    shutdown_db();

