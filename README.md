# Trustpilot Maze Pony Challenge


## Description

Help the pony escape the Domokun!
1. Create your maze API call (dimensions 15 to 25) + valid pony name
2. Get the maze with the ID from 1: you will get pony (player) location, Domokun (monster) location and maze walls
3. Move your pony (until you are dead or you reach the end-point)
(you can also print the maze with the API)


## Solution

- Find the path between the maze and the exit using the A* search algorithm
- Detect when the Domokun is nearby using the A* search algorithm
- Move towards the exit unless the Domokun is nearby
- If the Domokun is nearby, avoid taking the path towards it unless no other path is available


## Demo

<img alt="Level 10 difficulty maze win" src="https://i.imgur.com/SfpQdBG.gif" width="36%" height="46%" />


## Requirements

```bash
pip install requests
```


## Usage
```bash
python maze.py
python maze.py -player "Rainbow Dash" -difficulty 10 -width 25 -height 25
python maze.py -difficulty 5 -player "Applejack"
```


## Parameters

|Parameter   | Description                                         | Default       | Range   | Optional         |
|------------|-----------------------------------------------------|---------------|---------|------------------|
|`difficulty`| The difficulty of the enemy Domokun                 | 1             | 0 - 10  | :heavy_check_mark:
|`width`     | The width of the maze                               | 15            | 15 - 25 | :heavy_check_mark:
|`height`    | The height of the maze                              | 15            | 15 - 25 | :heavy_check_mark:
|`player`    | The player (pony) name - must be part of the "[m6]" | Random        | N/A     | :heavy_check_mark:


## Meta
Distributed under the [MIT license](https://choosealicense.com/licenses/mit/). See ``LICENSE`` for more information.
Author [@mcgill-a](https://github.com/mcgill-a)


[Mane 6][m6]

[m6]: https://mylittlepony.hasbro.com/en-us/characters/ponies
