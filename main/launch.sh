NUM_PROCESOS=$(python -c "import json; f = open('config.json','r'); print(json.loads(f.read())['process_number'])")
echo $NUM_PROCESOS
for ID in `seq 0 $(($NUM_PROCESOS-1))`;
do
    PORT=$((8080+$ID))
    poetry run python3.5 proceso.py $PORT &
done
