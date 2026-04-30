import z3
from z3 import (Solver, Bool,Bools,Int,Ints, Or, Not, And, Implies, Xor, BitVec, BV2Int, Reals, Distinct, If)

"""
Suppose we want to find a satisfying assignment for the expression (a || !b) && (!a || c). That means we’re looking for values of a, b, and c that make the entire expression evaluate to true.

One way to approach this is by checking all possible combinations of truth values for a, b, and c. Since each variable can be either true or false, there are 2^3=8 possible combinations.

Can you list all 8 combinations of a, b, and c?

    a   b   c
    0   0   0
    0   0   1
    0   1   0
    0   1   1
    1   0   0
    1   0   1
    1   1   0 
    1   1   1

In general, for n variables, there will be 2^n possible assignments, so the approach of "trying everything" is not efficient for large n. In fact, this is the SAT ("satisfiability") problem, which is NP-complete, meaning that it is "one of the hardest problems to which solutions can be verified quickly. But this difficult problem is exactly what tools like the Z3 SMT solver! Here’s how we can solve the problem using the Z3:
"""
def boolean_expressions():
    a = Bool('a')
    b = Bool('b')
    c = Bool('c')

    s = Solver()

    clause_1 = Or(a,Not(b))
    clause_2 = Or(Not(a),c)

    s.add(clause_1)
    s.add(clause_2)

    match s.check():
        case z3.sat:
            f_1_model = s.model()
            print(f_1_model)

    """
    The output says that the formula (a || !b) && (!a || c) will be true when a, b, and c are all false.

    But what if we want a different solution?

    In this case, we can add an additional constraint that says that we don’t want the solution where a, b, and c are all false.
    """


    clause_3 = Not(And(Not(a),Not(b),Not(c)))
    s.add(clause_3)

    match s.check():
        case z3.sat:
            f_2_model = s.model()
            print(f_2_model)

    """
    This output says that the formula (a || !b) && (!a || c) will be true when b is false and c is true (it doesn’t matter what a is).

    Let’s try adding one more constraint
    """

    clause_4 = (And(Not(a),b))
    s.add(clause_4)
    match s.check():
        case z3.unsat:
            print("Unsatisfiable")
    """
    The output unsat means unsatisfiable. The solver is telling us that there is no possible choice of a, b, c that makes the current constraints true.
    """

"""
Z3 can find solutions to more than just SAT problems – it is an SMT solver.

SMT stands for SAT modulo theories; it generalizes SAT to formulas involving integers, strings, arrays, and so on (the details of how it can do this are interesting but complicated, and we probably wont be able to get to them in class). For example, we can use Z3 to find a solution for the system of equations 3x - 2y = 1, y - x = 1.
"""
def integer_expressions():
    x,y = Ints('x y')
    s=Solver()
    s.add(3*x-2*y==1)
    s.add(y-x==1)

    match s.check():
        case z3.sat:
            model = s.model()
            print(model)

"""
In addition to integers Z3 can solve systems of equations that use real numbers. These can get quite complex and also very useful potentially for some of your final projects.
"""

def real_artithmetic():
    x, y = Reals('x y')
    s=Solver()
    s.add(x != 0)
    s.add(y != 0)
    s.add(x + y == 4 * x * y)
    match s.check():
        case z3.sat:
            print (f"Model: {s.model()}")

        case z3.unsat:
            print ("UNSAT")

"""
One of the most prominent uses of SMT in industry (especially now when so much software is being produced with little else to ensure correctness) is in software verification. You can see how we can prove interesting properties about programs including relating logical properties with underlying representation properties.
"""
def integer_overflow():
    # Note this takes a long time to process!
    x = BitVec('x', 16)
    y = BitVec('y', 16)

    s=Solver()
    s.add((BV2Int(x) + BV2Int(y)) != BV2Int(x+y))
    match s.check():
        case z3.sat:
            print (f"Model: {s.model()}")

        case z3.unsat:
            print ("UNSAT")




"""
Often, SMT solvers are not used to find a solution, but to prove that no solution exists. For instance, say that we want to prove the mathematical fact y > 0 ==> x + y > x. How might we do this using z3?
"""
def proof_by_unsat():
    # y>0 => x+y > x
    x,y = Ints('x y')
    s = Solver()

    # !(y>0) OR (x+y > x) -- logical expansion of implies
    s.add(Not(y>0))
    s.add(x+y>x)

    match s.check():
        case z3.unsat:
           print("The formula is UNSAT, meaning no contradiction can be found. Therefore the original formula must always be true.  QED.")


"""
Similarly, how might we try to generally prove any valid logical formula such as De Morgan's Laws?
"""
def demorgans_proof():
    p, q = Bools('p q')
    demorgan = And(p, q) == Not(Or(Not(p), Not(q)))

    def prove(f):
        """
        Print "No counterexample can be found, therefore the statement is true" if the given formula f is true, otherwise print "The formula f is false, with counterexample given by: " and the model that shows the formula to be false.
        """
        s = Solver()
        s.add(f)

        match s.check():
            case z3.sat:
                print("No counterexample can be found, therefore the statement is true")
            case z3.unsat:
                print(f"The formula f is false, with counterexample given by: {s.model()}")

    prove(demorgan)


"""
Let us try to use z3 to solve a classic kind of puzzle. You will need to come up with an encoding of the relevant part of the puzzle into variables and constraints as well translate the output of the solver into a solution.
"""
def wedding_planning():
    """
    You need to assign seating for a table of three potentially contentious wedding guests.

    There are three seats: left, middle, right.
    There are three guests: Alice, Bob, Charlie.



    The requirements are that:

    - Alice does not sit next to Charlie

    - Alice does not sit on the leftmost chair

    - Bob does not sit to the right of Charlie


    Can you find a seating arrangement that satisfies all of the guests?

    Print out either:
        The satisfying arrangement in the form "Alice sits on the left, Charlie in the middle, and Bob on the right."
    or
        "There is no acceptable seating arraignment"
    """

    a, b, c = Bools('Alice Charlie Bob')
    l, m, r = Bools('left middle right')

    clause_1 = And(a, Not(l)) # alice does not sit in the leftmost chair
    clause_2 = And(a, Not(m)) # alice cant sit in the middle because she cant sit next to charlie
    clause_3 = Or(And(And(b,l), And(c,m)), And(And(b,m), And(c,r))) # bob has to sit to the left of charlie
 
    s = Solver()
    s.add(clause_1)
    s.add(clause_2)
    s.add(clause_3)

    match s.check():
        case z3.sat:
            print(f"The satisfying argument is:{s.model()}") 

        case z3.unsat:
            print("There is no acceptable arraignment")

"""
Lets try to solve a more complex puzzle like sudoku, given an arbitrary input.

In case you do not know, sudoku is a puzzle where the goal is to insert numbers in boxes to satisfy the following condition: each row, column, and 3x3 box must contain the digits 1 through 9 exactly once.

You will need to transform an arbitrary sudoku puzzle template (where zero represents the unfilled boxes) into a solved puzzle (or show that the puzzle is impossible).
"""

def print_sudoku(grid):
    for i,row in enumerate(grid):
        if i%3==0:
            print('-'*25)
        print(f'| {row[0]} {row[1]} {row[2]} | {row[3]} {row[4]} {row[5]} | {row[6]} {row[7]} {row[8]} |')
    print('-'*25)


def sudoku(puzzle: tuple[tuple[int, ...], ...]):

    """
    Use print_sudoku to print your solution to puzzle or otherwise print "The puzzle is impossible.".
    """

    s = Solver()

    logical_sudoku = []
    cols_grid = []

    # make the logical variables
    for i, row in enumerate(puzzle):
        logical_row = []

        # go through each col in a row
        for j in range(len(row)):
            if (i == 0):
                cols_grid.append([])

            # make a new int
            logical_int = Int(f'r{i}c{j}')

            # save the constraint into the solver 
            if (row[j] > 0):
                s.add(logical_int == puzzle[i][j])
            else:
                # numbers can only range from 1-9
                s.add(logical_int < 10) 
                s.add(logical_int > 0)

            # save the variable (no matter what it is into the array)
            logical_row.append(logical_int)
            cols_grid[j].append(logical_int)

        # save the filled out row into the board array
        logical_sudoku.append(logical_row)
    
    # encode row rules
    for row in logical_sudoku:
        s.add(Distinct(col for col in row))

    # encode col rules
    for col in cols_grid:
        s.add(Distinct(val for val in col))


    # encode 3x3 rules
    num_cells = 0
    num_three_by_threes = 0

    if puzzle[0]:
        num_cells = len(puzzle[0])**2 # all the  

    num_three_by_threes = num_cells // 9 
    num_tbt_per_row = num_three_by_threes // 3 

    tbt = []

    # extract coordinates of each 3x3 chunk
    for i in range(num_tbt_per_row):
        for j in range(num_tbt_per_row):
            # clean slate
            tbt = []

            # populate the 3x3 with it's values
            start_row = j * 3
            start_col = i * 3

            # coordinates inside the 3x3 in question
            for k in range(3):
                for l in range(3):
                    tbt.append(logical_sudoku[start_row + k][start_col + l])

            # commit the 3x3 to the solver
            s.add(Distinct(tbt))
    
    # turns the solver model back into a grid
    def modelToGrid(model, logical_grid):
        grid: list[list[int]] = [] 

        for row in logical_grid:
            reconstructed_row = []

            for val in row:
                res = model[val].py_value()
                reconstructed_row.append(res)
            
            grid.append(reconstructed_row)
        return grid
            
    # check the solution
    match s.check():
        case z3.sat:
            print_sudoku(modelToGrid(s.model(), logical_sudoku))
        case z3.unsat:
            print("The puzzle is impossible")


instance = ((0,0,0,0,9,4,0,3,0),
            (0,0,0,5,1,0,0,0,7),
            (0,8,9,0,0,0,0,4,0),
            (0,0,0,0,0,0,2,0,8),
            (0,6,0,2,0,1,0,5,0),
            (1,0,2,0,0,0,0,0,0),
            (0,7,0,0,0,0,5,2,0),
            (9,0,0,0,6,5,0,0,0),
            (0,4,0,9,7,0,0,0,0))



"""
The final puzzle you will solve using Z3 is the Coin Sum problem. Here in the US we have (or used to have) pennies worth 1 cent, nickels worth 5 cents, dimes worth 10 cents, quarters worth 25 cents, half dollar coins worth 50 cents, and dollar coins worth 100 cents.

It is possible to make $2 using these coins in the following way:

    1 * 1$ + 1*50c + 1*25c + 1*10c + 2*5c + 5*1c

The question is: How many ways can $2 be made using any number of coins?
"""

def coin_sum(total):
    # Variables for the numbers of each coin denomination
    # penny, nickle, dime, quarter, fifty cent coin, dollar coin
    p,n,d,q,f,c = Ints('p n d q f c')

    coin_amnts = [p, n, d, q, f, c]

    successes = 0
    s = Solver()

    s.add(p >= 0)
    s.add(n >= 0)
    s.add(d >= 0)
    s.add(q >= 0)
    s.add(f >= 0)
    s.add(c >= 0)

    # add all the values to the coins 
    pv = 1
    nv = 5
    dv = 10
    qv = 25
    fv = 50
    cv = 100

    s.add((p*pv + n*nv + d*dv + q*qv + f*fv + c*cv) == total)

    # go through all the different combinations until the options are exhausted
    while True:
        match s.check():
            case z3.sat:
                successes += 1

                # remove this possibility from the solver
                model = s.model()

                # get rid of this satisfiable case so another soln can be found
                removal_clause = Not(And([coin == model[coin] for coin in coin_amnts]))
                s.add(removal_clause)

            case z3.unsat:
                break;

    print(successes)

