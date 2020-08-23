import requests
import json
import random
import math
import os
from tqdm import tqdm


class Node():

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.f = 0
        self.g = 0
        self.h = 0


players = [
    "Twilight Sparkle",
    "Pinkie Pie",
    "Fluttershy",
    "Rainbow Dash",
    "Princess Celestia",
    "Rarity",
    "Applejack",
    "Spike"
]

parameters = {
  "maze-width": 15,
  "maze-height": 15,
  "maze-player-name": random.choice(players),
  "difficulty": 5
}

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
api_base_url = "https://ponychallenge.trustpilot.com/pony-challenge/maze"

# TODO:
# - add try catch exceptions
# - implement enemy avoidance logic
# - switch x_dim and y_dim to grab from parameters rather than maze


def cls():
    os.system('cls' if os.name=='nt' else 'clear')


def create_maze():
    parameters_json = json.dumps(parameters)
    response = requests.post(api_base_url, data=parameters_json, headers=headers)
    print(response.status_code, response.reason)
    data = json.loads(response.content.decode("utf-8"))
    return data['maze_id']


def get_maze(maze_id):
    url = api_base_url + "/" + maze_id
    response = requests.get(url, headers=headers)
    print(response.status_code, response.reason)
    data = json.loads(response.content.decode("utf-8"))
    return data


def print_maze(maze_id):
    url = api_base_url + "/" + maze_id + "/print"
    response = requests.get(url, headers=headers)
    #print(response.status_code, response.reason)
    data = response.content.decode("utf-8")
    print(data)


def move(maze_id, direction):
    data = {'direction': direction}
    data_json = json.dumps(data)
    url = api_base_url + "/" + maze_id
    response = requests.post(url, data=data_json, headers=headers)
    #print(response.status_code, response.reason)
    data = json.loads(response.content.decode("utf-8"))
    
    return data


def backtrack(node):
    steps = []
    while node is not None:
        steps.append(node.position)
        node = node.parent
    return steps[::-1]


def search(maze, start, end):
    start_node = Node(None, start)
    end_node = Node(None, end)
    
    open_list, closed_list = set(), set()
    open_list.add(start_node)
    explored = [start_node.position]

    while len(open_list):
        current_node = min(open_list, key=lambda o:o.g + o.h)
        if current_node.position == end_node.position:
            return backtrack(current_node)
        
        open_list.remove(current_node)
        closed_list.add(current_node)
        
        children = []
        moves = get_available_moves(maze, position=current_node.position)
        for move in moves:
            node_position = get_new_position(maze, current_node.position, move)
            if node_position not in explored:
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
                node.h = get_distance_to_exit(maze, current_node.position, end_node.position)
                node.parent = current_node
                open_list.add(node)


def get_new_position(maze, position, direction):
    y_dim = int(maze['size'][1])
    
    if direction == "north":
        return position - y_dim
    elif direction == "east":
        return position + 1
    elif direction == "south":
        return position + y_dim
    elif direction == "west":
        return position - 1
    return None


def get_distance_to_exit(maze, current_position, exit_position):
    x_dim, y_dim = int(maze['size'][0]), int(maze['size'][1])

    current_x = current_position % x_dim
    current_y = math.floor(current_position / y_dim)

    exit_x = exit_position % x_dim
    exit_y = math.floor(exit_position / y_dim)

    # Euclidean distance
    return math.sqrt((exit_x - current_x)**2 + (exit_y - current_y)**2)


def get_position(maze, element):
    if element == 'pony':
        return int(maze['pony'][0])
    elif element == 'demokun':
        return int(maze['demokun'][0])
    elif element == 'end-point':
        return int(maze['end-point'][0])
    return None


def get_available_moves(maze, position=None):
    if not position:
        position = get_position(maze, 'pony')
    
    available_moves = {}
    
    on_south_edge, on_east_edge = False, False
    x_dim, y_dim = int(maze['size'][0]), int(maze['size'][1])
    size = x_dim * y_dim
    if "north" not in maze['data'][position]:
        available_moves['north'] = True
    if "west" not in maze['data'][position]:
        available_moves['west'] = True

    # Check if the player is at the south edge of the maze
    if (position > size - y_dim - 1):
        on_south_edge = True
    # Check if there is a north wall to the south of the player
    if not on_south_edge and "north" not in maze['data'][position+x_dim]:
        available_moves['south'] = True
    
    # Check if there is a west wall to the east of the player
    # (if the player is on the east of the maze, there will still be a west wall at position + 1)
    if position + 1 < size and "west" not in maze['data'][position+1]:
        available_moves['east'] = True
    
    return available_moves

def get_direction(maze, pos1, pos2):
    x_dim = int(maze['size'][0])

    if pos2 - pos1 == x_dim:
        return "south"
    elif pos2 - pos1 == -x_dim:
        return "north"
    elif pos2 - pos1 == 1:
        return "east"
    elif pos2 - pos1 == -1:
        return "west"
    return None


def solve(maze):
    get_available_moves(maze)
    path = search(maze, get_position(maze, 'pony'), get_position(maze, 'end-point'))
    
    directions = []
    for i in range(len(path) - 1):
        directions.append(get_direction(maze, path[i], path[i+1]))
    
    response = dict({'state': 'active'})
    for direction in tqdm(directions):
        if response['state'] != "active":
            break
        response = move(maze['maze_id'], direction)
    print(response['state-result'])

def main():
    maze_id = create_maze()
    print(maze_id)
    maze = get_maze(maze_id)
    print_maze(maze_id)
    solve(maze)


if __name__ == "__main__":
    main()