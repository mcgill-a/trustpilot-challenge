import requests
import json
import random


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
  "maze-player-name": "",
  "difficulty": 1
}

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
api_base_url = "https://ponychallenge.trustpilot.com/pony-challenge/maze"

# TODO:
# - add try catch exceptions
# - switch to random player name each time: random.choice(players)
# - implement a* algorithm


def create_maze():
    parameters['maze-player-name'] = players[0]
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
    print(response.status_code, response.reason)
    data = response.content.decode("utf-8")
    print(data)


def get_available_moves(maze):

    available_moves = {
        'north': False,
        'east': False,
        'south': False,
        'west': False
    }
    
    on_south_edge, on_east_edge = False, False
    x_dim, y_dim = int(maze['size'][0]), int(maze['size'][1])
    size = x_dim * y_dim

    pos_player = int(maze['pony'][0])
    
    if "north" not in maze['data'][pos_player]:
        available_moves['north'] = True
    if "west" not in maze['data'][pos_player]:
        available_moves['west'] = True

    # Check if the player is at the south edge of the maze
    if (pos_player > size - y_dim):
        on_south_edge = True
    # Check if there is a north wall to the south of the player
    if not on_south_edge and "north" not in maze['data'][pos_player+x_dim]:
        available_moves['south'] = True
    
    # Check if the player is at the east edge of the maze
    if (pos_player % x_dim == 0):
        on_east_edge = True
    # Check if there is a west wall to the east of the player
    if not on_east_edge and "west" not in maze['data'][pos_player+1]:
        available_moves['east'] = True
    
    print(available_moves)
    return available_moves


def solve(maze):
    get_available_moves(maze)
    pass


def main():
    #maze_id = create_maze()
    maze_id = "0650ad9d-e2ff-477c-a55b-d86e3401fdf3"
    maze = get_maze(maze_id)
    print_maze(maze_id)

    solve(maze)

if __name__ == "__main__":
    main()