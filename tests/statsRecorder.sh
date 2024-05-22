CONTAINER_NAME='gatewaysubscriber'
OUTPUT_FILE='record_22052024.txt'

while true; do
  docker stats --no-stream | grep $CONTAINER_NAME | awk -v date="$(date +%T)" '{
    cpu = $3; 
    mem = $4; 
    gsub("MiB", "", mem); 
    print date ", " cpu ", " mem
  }' >> $OUTPUT_FILE
  sleep 5
done