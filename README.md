# BLRS VAIC Pipeline

Check out our [technical report here!](https://arxiv.org/abs/2211.14385)

## Dependencies
- [tmux](https://github.com/tmux/tmux)
- [pros-cli](https://github.com/purduesigbots/pros-cli)
- [ARMS](https://github.com/purduesigbots/ARMS)

## Installation
- `git clone https://github.com/BLRSAI/competition_code`
- `cd competition_code`
- Create a PROS project or use an existing one
    - New project: `pros c new-project project_name`
    - `mv main.cpp project_name/src`
    - Install ARMS in this project
    - `pros mu` [Brain has to be plugged in via USB]

## Setup
These requirements need to be met for the pipeline to run properly:
1. V5 Brain with the `main.cpp` uploaded needs to be plugged into the Jetson
2. The Intel RealSense camera needs to be plugged into the Jetson

## Usage
### Running the Pipeline
`./run.sh`

### Stopping the Pipeline
`./stop.sh`
