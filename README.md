
### EA Average Polygon Gas Price

Clone the repo
```
git clone https://github.com/Block-Farms/ea-poly-avg-gas-price-public.git
```

Build the image
```
cd ea-poly-avg-gas-price && docker build -t ea-avg-gas-price .
```

Make persistence directory & Create persistence volume for the container
```
sudo mkdir .pd-volumes && docker volume create --name ea-storage --opt type=none --opt device=/home/commander/ea-poly-avg-gas-price/.pd-volumes/ --opt o=bind
```

Run the container
```
docker run --restart always -d \
    --log-driver json-file \
    --log-opt max-size=100m \
    --log-opt max-file=1 \
    --log-opt tag="{{.ImageName}}|{{.Name}}|{{.ImageFullID}}|{{.FullID}}" \
    -v ea-storage:/app/ \
    -p 8080:8080 \
    --name ea-avg-gas-price \
    ea-avg-gas-price:latest
```

Remove the container
```
docker rm -f ea-avg-gas-price
```

Check the container logs
```
docker logs --tail 100 ea-avg-gas-price
```

Test the container
```
curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:8080
```
```
{
  "data": {
    "avg_gas_price": 45971385216599998464
  },
  "statusCode": 200
}
```

Test the API URL of the EA from a Chainlink Node GUI via webhook job
```
type            = "webhook"
schemaVersion   = 1
name = "[WH] cbor0-v0"
observationSource   = """
    fetch [type="bridge" name="test" requestData="{}"]
    parse [type=jsonparse path="data,avg_gas_price" data="$(fetch)"]

    fetch -> parse
"""
```
