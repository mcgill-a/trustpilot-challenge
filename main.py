import requests
import json
import random
import math
import os
import argparse

class Node():
    """A* Pathfinding Node"""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.f = 0 # estimated total cost path through node to goal
        self.g = 0 # cost so far to reach node
        self.h = 0 # estimated cost from node to goal


PARAMS = {
    "maze-width": None,
    "maze-height": None,
    "maze-player-name": None,
    "difficulty": None
}

PLAYERS = [
    "Twilight Sparkle",
    "Fluttershy",
    "Applejack",
    "Rainbow Dash",
    "Rarity",
    "Pinkie Pie",
]

SETTINGS = {
    "min-width": 15,
    "max-width": 25,
    "min-height": 15,
    "max-height": 25,
    "min-difficulty": 0,
    "max-difficulty": 10,
    "display": True
}

HTTP_HEADERS = {'Content-type': 'application/json',
                'Accept': 'application/json'}
API_BASE_URL = "https://ponychallenge.trustpilot.com/pony-challenge/maze"


def clear_console():
    """Clear the Python console"""
    os.system('cls' if os.name == 'nt' else 'clear')


def create_maze():
    """Create a maze using the Pony API and return the maze id"""
    try:
        response = requests.post(
            API_BASE_URL, data=json.dumps(PARAMS), headers=HTTP_HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    data = json.loads(response.content.decode("utf-8"))
    return data['maze_id']


def get_maze(maze_id):
    """Get the current state of the maze using the Pony API"""
    try:
        url = API_BASE_URL + "/" + maze_id
        response = requests.get(url, headers=HTTP_HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    data = json.loads(response.content.decode("utf-8"))
    return data


def print_maze(maze_id):
    """Print the current visual representation of the maze using the Pony API"""
    try:
        url = API_BASE_URL + "/" + maze_id + "/print"
        response = requests.get(url, headers=HTTP_HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    data = response.content.decode("utf-8")
    clear_console()
    print(data)


def move(maze_id, direction):
    """Move the player character in the maze using the Pony API"""
    try:
        url = API_BASE_URL + "/" + maze_id
        response = requests.post(url, data=json.dumps(
            {'direction': direction}), headers=HTTP_HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    data = json.loads(response.content.decode("utf-8"))
    return data


def backtrack(node):
    """Iterate back through each path node to return a list of move positions"""
    steps = []
    while node is not None:
        steps.append(node.position)
        node = node.parent
    return steps[::-1]


def search(maze, start, end):
    """Search for the shortest path betwen two points using the A* search algorithm"""
    start_node = Node(None, start)
    end_node = Node(None, end)

    open_list, closed_list = set(), set()
    open_list.add(start_node)
    explored = [start_node.position]

    while len(open_list):
        current_node = min(open_list, key=lambda o: o.g + o.h)
        if current_node.position == end_node.position:
            return backtrack(current_node)

        open_list.remove(current_node)
        closed_list.add(current_node)

        children = []
        moves = get_available_moves(maze, position=current_node.position)
        for move in moves:
            node_position = get_new_position(maze, current_node.position, move)
            if node_position and node_position not in explored:
                explored.append(node_position)
                new_node = Node(current_node, node_position)
                children.append(new_node)

        for node in children:
            if node in closed_list:
                continue
            if node in open_list:
                new_g = current_node.g + 1
                if node.g > new_g:
                    node.g = new_g
                    node.parent = current_node
            else:
                node.g = current_node.g + 1
                node.h = get_distance_to_exit(
                    maze, current_node.position, end_node.position)
                node.parent = current_node
                open_list.add(node)


def get_new_position(maze, position, direction):
    """Get the updated position of the player based moving in the a given direction"""
    y_dim = PARAMS['maze-height']

    output = None

    if direction == "north":
        output = position - y_dim
    elif direction == "east":
        output = position + 1
    elif direction == "south":
        output = position + y_dim
    elif direction == "west":
        output = position - 1

    # Fallback for out of bounds edge cases
    if output < 0 or output > (PARAMS['maze-width'] * PARAMS['maze-height']) - 1:
        output = None
    return output


def get_distance_to_exit(maze, current_position, exit_position):
    """Get the euclidean distance between the player and the maze exit"""
    x_dim, y_dim = PARAMS['maze-width'], PARAMS['maze-height']

    current_x = current_position % x_dim
    current_y = math.floor(current_position / y_dim)

    exit_x = exit_position % x_dim
    exit_y = math.floor(exit_position / y_dim)

    # Euclidean distance
    return math.sqrt((exit_x - current_x)**2 + (exit_y - current_y)**2)


def get_position(maze, element):
    """Get the position of an element in the maze (pony, domokun, or end-point)"""
    if element == 'pony':
        return int(maze['pony'][0])
    elif element == 'domokun':
        return int(maze['domokun'][0])
    elif element == 'end-point':
        return int(maze['end-point'][0])
    return None


def get_available_moves(maze, position=None):
    """Get the directions that a player can move given a specific position"""
    if not position:
        position = get_position(maze, 'pony')

    available_moves = []

    on_south_edge = False
    x_dim, y_dim = PARAMS['maze-width'], PARAMS['maze-height']
    size = x_dim * y_dim
    if "north" not in maze['data'][position]:
        available_moves.append('north')
    if "west" not in maze['data'][position]:
        available_moves.append('west')

    # Check if the player is at the south edge of the maze
    if (position > size - y_dim - 1):
        on_south_edge = True
    # Check if there is a north wall to the south of the player
    if not on_south_edge and "north" not in maze['data'][position+x_dim]:
        available_moves.append('south')

    # Check if there is a west wall to the east of the player
    # (if the player is on the east of the maze, there will still be a west wall at position + 1)
    if position + 1 < size and "west" not in maze['data'][position+1]:
        available_moves.append('east')
    return available_moves


def get_direction(maze, pos1, pos2):
    """Get the direction travelled moving from one position to another"""
    x_dim = PARAMS['maze-width']

    if pos2 - pos1 == x_dim:
        return "south"
    elif pos2 - pos1 == -x_dim:
        return "north"
    elif pos2 - pos1 == 1:
        return "east"
    elif pos2 - pos1 == -1:
        return "west"
    return None


def get_directions(maze, a, b):
    """Get the directions between point a and point b"""
    path = search(maze, get_position(maze, a),
                  get_position(maze, b))

    directions = []
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            directions.append(get_direction(maze, path[i], path[i+1]))
    return directions


def get_random_safe_move(maze, pos_player, domokun_path,):
    moves = get_available_moves(maze, pos_player)
    if len(moves) > 1:
        if domokun_path[0] in moves:
            moves.remove(domokun_path[0])
    return random.choice(moves)


def solve(maze):
    """Run the A* search to find the shortest path and then send each move to the Pony API"""
    response = dict({'state': 'active'})  # default state
    while(response['state'] == 'active'):
        reset_path = False
        directions = get_directions(maze, 'pony', 'end-point')
        for direction in directions:
            if response['state'] != 'active':
                break

            # if there is a domokun blocking the exit path direction
            domokun_path = get_directions(maze, 'pony', 'domokun')
            if len(domokun_path) <= 2 and domokun_path[0] == direction:
                pos_player = get_position(maze, 'pony')
                new_direction = get_random_safe_move(
                    maze, pos_player, domokun_path)
                if new_direction:
                    direction = new_direction
                    reset_path = True
                else:
                    # no additional moves to avoid the domokun - accept your fate
                    reset_path = False
            response = move(maze['maze_id'], direction)
            maze = get_maze(maze['maze_id'])
            if SETTINGS['display']:
                print_maze(maze['maze_id'])
            if reset_path:
                print("=============================================================")
                print(PARAMS['maze-player-name'] + " is running away from the domokun")
                print("=============================================================")
                break

    display_info(maze, response)


def valid_player_name(arg):
    """Type function to determine whether a player name is valid"""
    if arg:
        if not arg.lower() in (player.lower() for player in PLAYERS):
            raise argparse.ArgumentTypeError(
                "Player name must be a valid pony name")
    return arg


def display_info(maze, response):
    if SETTINGS['display']:
        print_maze(maze['maze_id'])
    print("=============================================================")
    print(response['state-result'])
    if response['hidden-url']:
        print('https://ponychallenge.trustpilot.com' + response['hidden-url'])
    print("Maze ID: " + maze['maze_id'])
    print("=============================================================")


def get_arguments():
    """Get the command line arguments to setup the maze parameters"""
    parser = argparse.ArgumentParser(
        description='Trustpilot Challenge - Save the Pony!')
    parser.add_argument('-width', default=15, type=int, choices=range(
        SETTINGS['min-width'], SETTINGS['max-width']+1))
    parser.add_argument('-height', default=15, type=int, choices=range(
        SETTINGS['min-height'], SETTINGS['max-height']+1))
    parser.add_argument('-difficulty', default=1, type=int, choices=range(
        SETTINGS['min-difficulty'], SETTINGS['max-difficulty']+1))
    parser.add_argument('-display', default=True,
                        type=bool, choices=[True, False])
    parser.add_argument('-player', default=random.choice(PLAYERS),
                        type=str.title, choices=PLAYERS)

    args = parser.parse_args()
    PARAMS['maze-width'] = args.width
    PARAMS['maze-height'] = args.height
    PARAMS['difficulty'] = args.difficulty
    PARAMS['maze-player-name'] = args.player
    SETTINGS['display'] = args.display


def main():
    get_arguments()
    maze_id = create_maze()
    maze = get_maze(maze_id)
    print_maze(maze_id)
    solve(maze)


if __name__ == "__main__":
    main()
