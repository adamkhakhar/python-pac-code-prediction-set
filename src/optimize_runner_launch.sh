TIMEOUT=300
MAX_INDEX=90

for m in {1..5}
do
    for ((i=0; i < $MAX_INDEX; i=i+1))
    do
        echo running i=$i ...
        timeout $TIMEOUT python3 optimize_runner.py --dataind $i --m $m >> or.log
        sleep 1
    done
done
