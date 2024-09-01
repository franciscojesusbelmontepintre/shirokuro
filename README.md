# shirokuro
Japanese logical hobby developed in <b>Python</b> and <b>Kivy</b><br>
<b>Author:</b> Francisco Jesús Belmonte Pintre<br>
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/board.png">
</p><br>

# Board generation features
 - Stochastic/Random boards generation
 - Unitary/Non-Unitary solution boards generation
 - Level-based difficulty system
 - Possibility to choose the board's size
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/metrics.png">
</p><br>

# Game options
 - BackTracking-heuristic-technique to generate all solutions
 - Aid system based on Breadth-first search, redirecting from wrong paths and giving a next step
 - Save and Load the current game so you can continue later
 - Pause and Resume the chronometer
 - Reset the current game
 - Return to past states
 - Guided solution
 - Etc.
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/game options.png">
</p><br>

# Others
 - Ranking based on time spent and used aids
 - Different ranking classifications based on difficulty and board size
 - Instructions
 - Etc.
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/others.png">
</p><br>

# Desktop
 - A Dockerfile has been cooked so that the entire game can be run inside a container
 - A VNC Client and SSH Client (for example VNC Viewer and Putty) are both needed
 <br>

The Shirokuro docker container up and running
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/desktop/docker_run.png">
</p><br>

The Putty Configuration (VNC Connection cyphered under SSH)
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/desktop/putty_conf.png">
</p><br>

Setting up the VNC Connection after the SSH one is established
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/desktop/vnc_over_ssh.png">
</p><br>

A few captures from the game running inside the container
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/desktop/kivy_over_docker.png">
</p><br>
<p align="center">
  <img src="https://raw.githubusercontent.com/franciscojesusbelmontepintre/shirokuro/master/images/desktop/kivy_over_docker2.png">
</p><br>

# Roadmap
 - Currently the Ranking feature works within the installed app but there is no way to have an online ranking
 - Its a kind of offline ranking, each installed app has its own, so that someone can borrow your phone/tablet, play a game and the ranking is updated within the app installed in your device by using the .json as savedata's file.
 - The idea could be setting up a backend and a BBDD, a basic login system so that whenever a player finish a game, the results are sent to the backend
 - A Multiplayer option. Boards of 15x15 are big ones, so what if two players play the same board in terms of each player has to force the second one to do the final move. The one who forces the second one to do the final move wins the match. Is that possible? Is it fair?
 - It is important to make a point on big size boards because the smaller ones are easy from both players to know which movements lead to a solution, so in that case it wouldnt be fair and the one who starts the game will have advantage
