#/bin/bash

current_pos=${CURRENT_POS}
declare -A positions=( [0]="C" [1]="1B" [2]="2B" [3]="3B" [4]="OF" [5]="SP" [6]="RP")

echo ~~~~~~~~~~ BEGIN ~~~~~~~~~~~~~~
echo Creating free agency plot for "${positions[$current_pos]}"

python3 processing/for_fantasy_baseball/get_free_agent_summary.py -p "${positions[$current_pos]}";
python3 plotting/fantasy/mlb_free_agents.py -p "${positions[$current_pos]}";
python3 tweet-posting/skeet_picture.py -i fantasy_plot.png -t 'this is a test'

echo Scripts completed

new_pos=$(( ($current_pos + 1) % 7 ))
export CURRENT_POS=$new_pos

echo CURRENT_POS is not set to "${CURRENT_POS}"
echo ~~~~~~~~~~~ END ~~~~~~~~~~~~~~