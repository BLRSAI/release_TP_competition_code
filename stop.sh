#!/bin/bash
# Ends the whole pipeline i.e. the pros terminal as well as the Brain program
pros v5 stop
tmux kill-window -t 0
tmux kill-window -t 1
