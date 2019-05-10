import copy
import heapq

initial_board = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
]

invalid_set = [
    [0, 0],
    [0, 1],
    [0, 5],
    [0, 6],
        
    [1, 0],
    [1, 1],
    [1, 5],
    [1, 6],
    
    [5, 0],
    [5, 1],
    [5, 5],
    [5, 6],
    
    [6, 0],
    [6, 1],
    [6, 5],
    [6, 6],
]

class Node:
    def __init__(self, state, parent = None, movement = None):
        self.parent = parent
        self.state  = state
        self.movement = movement
        
        self.cost   = 0
        self.rating = 0
        self.total  = 0

    def __eq__(self, that):
        return self.state == that.state

    def __lt__(self, that):
        #return (self.total, self.cost) < (-that.total, that.cost)
        return self.total < that.total

def heuristic(state):
    counter = 0
    
    for i in range(0,7):
        for j in range(0,7):
            if filled_valid_position(state, i, j):
                counter += 1
    return counter

def valid_position(i, j):
    """Check if the indexes are valid on the board"""
    return i in range(0, 7) and j in range(0, 7) and [i, j] not in invalid_set

def filled_valid_position(state, i, j):
    """Check if the [i, j] is a valid position and if it has a pin"""
    return valid_position(i, j) and state[i][j] == 1

def empty_valid_position(state, i, j):
    """Check if the [i, j] is a valid position and if it don't have a pin"""
    return valid_position(i, j) and state[i][j] == 0

def is_goal(state):
    """
    Check if the state is the goal
    
    Sum all rows and check if the result is 1 (has only one pin in the board)
    """
    return sum(sum(state, [])) == 1

def generate_sons(state):
    """
    Given the current state, for each pin left on the board, try to jump in
    
    For each successfully jump, create new state for it.
    """
    child = []

    for i in range(0, 7):
        for j in range(0, 7):

            # Check possible move up
            if (filled_valid_position(state, i, j)
                and filled_valid_position(state, i - 1, j)
                and empty_valid_position(state, i - 2, j)):

                new_state = copy.deepcopy(state) # Copy the current state
                new_state[i][j]     = 0          # Remove pin from current position
                new_state[i - 1][j] = 0          # Remove jumped pin
                new_state[i - 2][j] = 1          # Set new pin position
                child.append((new_state, [(i, j), (i - 2, j)]))

            # Check possible move down
            if (filled_valid_position(state, i, j)
                and filled_valid_position(state, i + 1, j)
                and empty_valid_position(state, i + 2, j)):

                new_state = copy.deepcopy(state) # Copy the current state
                new_state[i][j]     = 0          # Remove pin from current position
                new_state[i + 1][j] = 0          # Remove jumped pin
                new_state[i + 2][j] = 1          # Set new pin position
                child.append((new_state, [(i, j), (i + 2, j)]))

            # Check possible move left
            if (filled_valid_position(state, i, j)
                and filled_valid_position(state, i, j - 1)
                and empty_valid_position(state, i, j - 2)):

                new_state = copy.deepcopy(state) # Copy the current state
                new_state[i][j]     = 0          # Remove pin from current position
                new_state[i][j - 1] = 0          # Remove jumped pin
                new_state[i][j - 2] = 1          # Set new pin position
                child.append((new_state, [(i, j), (i, j - 2)]))

            # Check possible move right
            if (filled_valid_position(state, i, j)
                and filled_valid_position(state, i, j + 1)
                and empty_valid_position(state, i, j + 2)):

                new_state = copy.deepcopy(state) # Copy the current state
                new_state[i][j]     = 0          # Remove pin from current position
                new_state[i][j + 1] = 0          # Remove jumped pin
                new_state[i][j + 2] = 1          # Set new pin position
                child.append((new_state, [(i, j), (i, j + 2)]))

    return child

def astar(board):

    # Create the start node
    start_node = Node(board)
    
    visited_states = []                # Initialize visited nodes list
    candidates     = [ start_node ]    # Initialize candidates nodes list

    while len(candidates) > 0:
        current_node = heapq.heappop(candidates) # Find the minimum total cost (cost + rating)


        if is_goal(current_node.state):
            path = []
            while current_node.parent:
                path.append("{} - {}".format(str(current_node.movement[0]), str(current_node.movement[1])))
                current_node = current_node.parent

            with open('./saida-resta-um.txt', 'w') as f:
                f.write('==SOLUCAO\n')
                for i in range(len(path) - 1) :
                    f.write('{}\n'.format(path[i]))
                
                f.write('FINAL {}\n'.format(path[i + 1]))

            break

        visited_states.append(current_node.state)             # Add to the visited list
        # print("Current node cost: ", current_node.cost, " total: ", current_node.total)

        for child, movement in generate_sons(current_node.state):       # Generate new possible states from here
            if child in visited_states:                       # Skip generated child if his state were already visited
                continue

            new_node        = Node(child, current_node, movement)       # Create new node if current node as parent
            new_node.cost   = current_node.cost + 1           # Update the cost
            new_node.rating = heuristic(new_node.state)       # Update the rating score (heuristic)
            new_node.total  = new_node.cost + new_node.rating # Update it's total score
            heapq.heappush(candidates, new_node)              # Add to candidates list

if __name__ == "__main__":
    astar(initial_board)