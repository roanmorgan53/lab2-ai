from model import (
    Location,
    Wizard,
    IceStone,
    FireStone,
    WizardMoves,
    GameAction,
    GameState,
    WizardSpells, NeutralStone,
)
from agents import WizardAgent

import z3
from z3 import (Solver, Bool, Bools, Int, Ints, Or, Not, And, Implies, Distinct, If)


# masyu constraints 
# ice stone = must move straight through before, during, and after
# ice stone must have 90deg turn before the ice stone or next cell after ice stone


class PuzzleWizard(WizardAgent):

    def react(self, state: GameState) -> WizardMoves:
        fire_stones = state.get_all_tile_locations(FireStone)
        ice_stones = state.get_all_tile_locations(IceStone)
        grid_size = state.grid_size
        wizard_location = state.active_entity_location
        logical_grid = []
        s = Solver()
        
        # possible moves
        VERTICAL = 0
        HORIZONTAL = 1

        # takes in the location and the gridsize and checks if it's inside bounds
        def isInBounds(loc: Location):
            return True if ((loc.row, loc.col) in grid_size) else False

        # initialize the logical grid
        for i in range(grid_size[0]):
            row = []
            for j in range(grid_size[1]):
                row.append(Int(f'{i}_{j}'))
            logical_grid.append(row)

        # add the parameters
        for i in range(len(logical_grid)):
            for j in range(len(logical_grid[i])):
                above_loc = Location(i - 1, j)
                below_loc = Location(i + 1, j)
                right_loc = Location(i, j + 1)
                left_loc = Location(i, j - 1)
                cur_loc = Location(i, j)
                
                # current spot is an ice stone
                if cur_loc in ice_stones:
                    # can go through vertically
                    if isInBounds(above_loc) and isInBounds(below_loc):
                        s.add(logical_grid[above_loc.row][above_loc.col] == VERTICAL)
                        s.add(logical_grid[below_loc.row][below_loc.col] == VERTICAL)

                        # move before or after the stone needs to be a 90deg turn
                        #!!! possible issue is accessing out of bounds on these
                        s.add(
                            Or (
                                logical_grid[above_loc.row][above_loc.col + 1] == HORIZONTAL,
                                logical_grid[above_loc.row][above_loc.col - 1] == HORIZONTAL,
                                logical_grid[below_loc.row][below_loc.col + 1] == HORIZONTAL,
                                logical_grid[below_loc.row][below_loc.col - 1] == HORIZONTAL,
                            )
                        )
                    
                    # can go through horizontally
                    if isInBounds(left_loc) and isInBounds(right_loc):
                        s.add(logical_grid[left_loc.row][left_loc.col] == HORIZONTAL)
                        s.add(logical_grid[right_loc.row][right_loc.col] == HORIZONTAL)

                        # move before or after the stone needs to be a 90deg turn
                        #!!! possible issue is accessing out of bounds on these
                        s.add(
                            Or (
                                logical_grid[left_loc.row - 1][left_loc.col] == VERTICAL,
                                logical_grid[left_loc.row + 1][left_loc.col] == VERTICAL,
                                logical_grid[right_loc.row - 1][right_loc.col] == VERTICAL,
                                logical_grid[right_loc.row + 1][right_loc.col] == VERTICAL,
                            )
                        )
                
                # fire stone restrictions
                # fire stone = no straight lines through, must turn 90deg
                # path must be straight from before fir stone and a cell after it

                # current spot is a fire stone
                elif cur_loc in fire_stones:

                    # a couple things to keep in mind
                    # there can either be a 
                    #     |  |    O-- --O
                    #     |  |    |     |
                    #   --O, O--, |   , |

                    left_horizontal = logical_grid[left_loc.row][left_loc.col] == HORIZONTAL
                    left_left_horizontal = logical_grid[left_loc.row][left_loc.col - 1] == HORIZONTAL

                    right_horizontal = logical_grid[right_loc.row][right_loc.col] == HORIZONTAL
                    right_right_horizontal = logical_grid[right_loc.row][right_loc.col + 1] == HORIZONTAL

                    top_vertical = logical_grid[above_loc.row][above_loc.col] == VERTICAL
                    top_top_vertical = logical_grid[above_loc.row - 1][above_loc.col] == VERTICAL

                    bot_vertical = logical_grid[below_loc.row][below_loc.col] == VERTICAL
                    bot_bot_vertical = logical_grid[below_loc.row + 1][below_loc.col] == VERTICAL

                    left_then_up = And (
                        left_left_horizontal,
                        left_horizontal,
                        top_top_vertical,
                        top_vertical
                    )

                    right_then_up = And (
                        right_right_horizontal,
                        right_horizontal,
                        top_vertical,
                        top_top_vertical
                    )

                    below_then_right = And (
                        bot_bot_vertical,
                        bot_vertical,
                        right_horizontal,
                        right_right_horizontal
                    )

                    below_then_left = And (
                        bot_bot_vertical,
                        bot_vertical,
                        left_horizontal,
                        left_left_horizontal
                    )

                    s.add(
                        Or (
                            left_then_up,
                            right_then_up,
                            below_then_left,
                            below_then_left
                        )
                    )

                else:
                    s.add(
                        Or(cur_loc == VERTICAL, cur_loc == HORIZONTAL)
                    )
        
        match s.check():
            case z3.sat:
                print(f"found a solution for ")
            case z3.unsat:
                print("couldn't find a solution") 

        return MASYU_1_SOLUTION.pop(0)




class SpellCastingPuzzleWizard(WizardAgent):

    def react(self, state: GameState) -> GameAction:
        fire_stones = state.get_all_tile_locations(FireStone)
        ice_stones = state.get_all_tile_locations(IceStone)
        neutral_stones = state.get_all_tile_locations(NeutralStone)

        grid_size = state.grid_size
        wizard_location = state.active_entity_location

        # TODO: YOUR CODE HERE
        return MASYU_2_SOLUTION.pop(0)






"""
Here are some reference solutions for some of the included puzzle maps you can use to help you test things
"""

MASYU_1_SOLUTION =[WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP]


MASYU_2_SOLUTION =[WizardMoves.RIGHT,WizardSpells.FIREBALL,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardSpells.FREEZE,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardSpells.FIREBALL,WizardMoves.RIGHT]
