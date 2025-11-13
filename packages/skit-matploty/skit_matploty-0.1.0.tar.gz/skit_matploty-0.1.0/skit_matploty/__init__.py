
"""
skit-matploty: A package to print ML code snippets.
"""

# Import the code strings from snippets.py
from .snippets import (
    EX1_EDA,
    EX2_PREPROCESSING,
    EX3_LINEAR_REGRESSION,
    EX4_CLASSIFICATION_PIPELINE,
    EX5_NAIVE_BAYES,
    EX6_RF_REGRESSOR
)

# Define the public functions
__all__ = [
    "print_ex1",
    "print_ex2",
    "print_ex3",
    "print_ex4",
    "print_ex5",
    "print_ex6",
    "print_all"
]

def print_ex1():
    """Prints the snippet for EX-1 (EDA)."""
    print(EX1_EDA)

def print_ex2():
    """Prints the snippet for EX-2 (Preprocessing)."""
    print(EX2_PREPROCESSING)

def print_ex3():
    """Prints the snippet for EX-3 (Linear Regression)."""
    print(EX3_LINEAR_REGRESSION)

def print_ex4():
    """Prints the snippet for EX-4 (Classification Pipeline)."""
    print(EX4_CLASSIFICATION_PIPELINE)

def print_ex5():
    """Prints the snippet for EX-5 (Naive Bayes)."""
    print(EX5_NAIVE_BAYES)

def print_ex6():
    """Prints the snippet for EX-6 (Random Forest Regressor)."""
    print(EX6_RF_REGRESSOR)

def print_all():
    """Prints all available code snippets."""
    print_ex1()
    print("\n" + "="*80 + "\n")
    print_ex2()
    print("\n" + "="*80 + "\n")
    print_ex3()
    print("\n" + "="*80 + "\n")
    print_ex4()
    print("\n" + "="*80 + "\n")
    print_ex5()
    print("\n" + "="*80 + "\n")
    print_ex6()
