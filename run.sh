#! /bin/bash
#$1 ticks
#S2 sed
sed=$RANDOM
echo "ticks:" $1 "sed" $sed
siec=("awaria" "randomgeographic" "hypercube" "SimpleNetwork")
algo=("LinkStateRouter" "DistanceVectorRouter" "BFS" "RandomRouter")
for i in "${siec[@]}"
do
  echo $i
  for j in "${algo[@]}"
  do
    echo "    " $j $(./simulate.py --ticks $1 -s $sed $i $j)
  done;
done
