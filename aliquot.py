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

def save_aliquot(integer, factors, successor, type):
    assert dbconn;
    factors_str = ",".join(map(str, factors));
    dbcursor.execute("""
        INSERT OR REPLACE
        INTO Aliquot
        VALUES (?, ?, ?, ?);""",
        [integer, factors_str, successor, type]);

def aliquot_computed(integer):
    results = dbcursor.execute("""
        SELECT 'T'
        FROM Aliquot
        WHERE integer = ?;""",
        [integer]);
    return bool(results.fetchone());

def print_aliquot_data():
    assert dbconn;
    results = dbcursor.execute("""
        SELECT *
        FROM Aliquot;""");
    for line in results.fetchall():
        [integer, factors_str, successor, type] = line;
        factors = list(map(int, factors_str.split(",")));
        print(integer, factors, successor, type, sep = " % ");


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
    try:
        while True:
            # Recursion by loop to allow more than 900 iterations.
    
            if prog_callback: prog_callback(integer, trace);
    
            factors = factor(integer);
            aliquot = sum(factors);
        
            type = None;
            if aliquot in trace:
                if len(trace) == 1: type = "Amicable";
                else: type = "Sociable";
            elif aliquot < integer: type = "Deficient";
            elif aliquot > integer: type = "Abundant";
            else: type = "Perfect";
    
            if type == "Amicable" or type == "Sociable":
                for prev_integer in trace:
                    update_aliquot_type(prev_integer, type);
            if type == "Perfect" and not aliquot == 1:
                for prev_integer in trace:
                    update_aliquot_type(prev_integer, "Aspiring");
            save_aliquot(integer, factors, aliquot, type);
        
            trace.append(integer);
            if aliquot_computed(aliquot): return trace;
            elif type == "Amicable": return trace;
            elif type == "Sociable": return trace;
            elif type == "Perfect": return trace;
            else: integer = aliquot;
    except KeyboardInterrupt: return trace;


if __name__ == "__main__":
    from sys import argv;
    from time import time;
    def prog_callback(integer, trace):
        print(
            "{}Computing".format("\b" * 40), integer,
            "after", len(trace), "numbers.",
            end="", flush=True);
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
        except ValueError: continue;
    print_aliquot_data();
    shutdown_db();

