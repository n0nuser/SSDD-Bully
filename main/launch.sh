NUM_PROCESOS=2
IP_SERVER="127.0.0.1"

for ID in `seq 0 $(($NUM_PROCESOS-1))`;
do

    PORT=$((8080+$ID))
    poetry run python3.5 proceso.py $IP_SERVER "$PORT" "$ID" &
done
