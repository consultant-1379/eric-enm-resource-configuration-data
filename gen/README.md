# RCD JSON Generator

## Requirements
- Linux machine (This tool attach to helm in a Linux specific way, supporting other OSs was not investigated yet)
- Python (3.8 or higher)
- helm executable on PATH (a version used during cENM installation)
- Python libraries listed in `requirements.txt`

## Usage
Run `python3 gen/main_app.py`
This starts the flask app in the foreground.
Then to generate a JSON file for a new product set a rest request should be made.

### Example

```bash
cd ..
gen/main_app.py -n
```

For ENM Internal Product sets:
```bash
curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Basic eC1hdXRoLXRva2Vu==" \
    -d '{"product": "cENM", "productset": "22.02.48"}' \
    -k https://localhost:5000/addproductset
```

For ENM release candidate:
```bash
curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Basic eC1hdXRoLXRva2Vu==" \
    -d '{"product": "cENM", "productset": "22.03.95"}' \
    -k https://localhost:5000/addreleaseproductset
```

For EIC Internal Product sets:
```bash
curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Basic eC1hdXRoLXRva2Vu==" \
    -d '{"product": "EIC", "productset": "2.19.0-8"}' \
    -k https://localhost:5000/addproductset
```

For EIC release candidate:
```bash
curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Basic eC1hdXRoLXRva2Vu==" \
    -d '{, "product": "EIC", "productset": "2.19.0-8"}' \
    -k https://localhost:5000/addreleaseproductset
