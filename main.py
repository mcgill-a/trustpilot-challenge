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


def main():
    maze_id = create_maze()
    maze = get_maze(maze_id)
    print_maze(maze_id)


if __name__ == "__main__":
    main()