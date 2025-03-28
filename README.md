linka-ota-server

Remote OTA Server for [Linka sensors](https://github.com/melizeche/AireLibre/) using [linka-firmware](https://github.com/garyservin/linka-firmware)

# Development instructions
## Using python vevn directly
Install
```
$ sudo apt install python3-devel
$ python3 -m venv venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

Run
```
$ source ./venv/bin/activate
$ gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## Using docker and docker-compose
1. Start the services
```
docker compose -f docker-compose.yaml up -d --build
```

# Firmware directory storage
## Directory hierarchy
Your directory should look like this
```
bin
├── versions
├── linka-firmware-v0.0.1.bin
├── linka-firmware-v0.0.2.bin
├── linka-firmware-v0.0.3.bin
└── ...
```
## versions file format
The `versions` file is a json file containing each firmware version with the following format
```
{
    "latest": "0.0.3",
    "0.0.1": {
        "file": "linka-firmware-v0.0.1.bin",
        "md5sum": "7f79518ff0f370823700936b4f10acb9"
    },
    "0.0.2": {
        "file": "linka-firmware-v0.0.2.bin",
        "md5sum": "b3f04d699afbb868eb5d4ef908b63fb1"
    },
    "0.0.3": {
        "file": "linka-firmware-v0.0.3.bin",
        "md5sum": "a1ae859790fa8291551978710ac563ad"
    }
}
```
