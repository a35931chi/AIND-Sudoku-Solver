#this is written with Python 3.5 IDLE
#shell code was taken from github: https://github.com/udacity/aind-sudoku
#majority of structure/functions are taken from udacity sudoku exercises

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B): #loop through rows and columsn to create box labels
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

boxes = cross(rows, cols) #produce all the boxes
row_unit = [cross(r, cols) for r in rows] #produce a list containing all the row units
col_unit = [cross(rows, c) for c in cols] #produce a list containing all thr column units
square_unit = [cross(rs, cs) for rs in ['ABC','DEF','GHI'] for cs in ['123','456','789']] #produce a list containing all the square units
diag_unit = [[rows[i] + cols[i] for i in range(len(rows))] , [rows[-i-1] + cols[i] for i in range(len(rows))]] #produce a list containing all the diagonal units
if True: #taking in acocunt diagonal units
    unitlist = row_unit + col_unit + square_unit + diag_unit
else:
    unitlist = row_unit + col_unit + square_unit
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid): #initalize the values dictionary
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    
    assert len(grid) == 81
    return dict(zip(boxes, chars))

def display(values): #show the sudoku (only works if puzzle is solved)
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values): #if we have solved boxes, all the peers of those boxes should ride those solved values
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(values[box], ''))
    return values

def only_choice(values): #if a value is unique in a unit, assign that value to that box
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def naked_twins(values): #if in the unit there exists two cells with the same values of length two, other cells shouldn't have those values
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    #identify cells with length 2
    len2_boxes = [box for box in values.keys() if len(values[box]) == 2]
    len2_values = [values[box] for box in len2_boxes]
    #for each twin value found
    for box in len2_boxes:
        if len(values[box]) == 2:
            #identify the units that it belongs to
            for unit in units[box]:
                #iterate through the unit to see if we find a value that is the same
                for another_box in unit:
                    if box != another_box and values[box] == values[another_box]:
                        digits = values[box]
                        #if we do, we iterate through the cells in other units and remove those values
                        for yet_another_box in unit:
                            if yet_another_box != another_box and yet_another_box != box and (digits[0] in values[yet_another_box] or digits[1] in values[yet_another_box]):
                                assign_value(values, yet_another_box, values[yet_another_box].replace(digits[0], ''))
                                assign_value(values, yet_another_box, values[yet_another_box].replace(digits[1], ''))
    return values
    
def reduce_puzzle(values): #chaining the value processor together
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    print('{} solved values: {}'.format(len(solved_values), solved_values))
    stalled = False
    while not stalled:
        solved_values_before = [box for box in values.keys() if len(values[box]) == 1]
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = [box for box in values.keys() if len(values[box]) == 1]
        stalled = (solved_values_before == solved_values_after)
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values): #if stalled, then build a tree and try all the combination until solution is found
    values = reduce_puzzle(values)
    if values is not False:
        print('value reduced')
    if values is False:
        print('stuck')
        return False
    if all([len(values[s]) == 1 for s in boxes]):
        print('solved!')
        return values
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    for value in values[s]:
        print('for square {}, trying {} out of {}'.format(s, value, values[s]))
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid): # the main function that calls other functions
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    
    #initialize
    values = grid_values(grid)
    #solve
    values = search(values)
    return values
    

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    try_this = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(try_this))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

