# linka-ota-server

Remote OTA Server for [Linka sensors](https://github.com/melizeche/AireLibre/) using [linka-firmware](https://github.com/garyservin/linka-firmware)

## Development instructions
### Using uv
Install [uv](https://docs.astral.sh/uv/), then:
```
$ uv sync
$ uv run pytest
$ FIRMWARE_PATH=./bin uv run gunicorn --bind 0.0.0.0:5000 'linka_ota_server:create_app()'
```

### Using docker compose
Build the image locally and start the service:
```
docker compose up -d --build
```

## Deployment
`.github/workflows/ci.yml` runs on every push to `master`:
1. Runs the tests (GitHub-hosted runner).
2. Builds the Docker image and publishes it to `ghcr.io/garyservin/linka-ota-server`
   with the tags `latest` and `sha-<commit>` (`vX.Y.Z` git tags also publish `X.Y.Z` / `X.Y`).
3. Deploys it on the server with the self-hosted runner: pulls `sha-<commit>`, restarts
   the service in `/home/gary/linka/linka-ota-server` and checks `/up`.

Pull requests only run steps 1 and 2 (without publishing).

To update the server manually, next to `compose.yaml` and the `bin/` firmware directory:
```
docker compose pull && docker compose up -d
```

The firmware is not part of the image: it is read from `bin/`, which is mounted at `/app/bin`.

## Firmware directory storage
### Directory hierarchy
Your directory should look like this
```
bin
├── versions
├── linka-firmware-v0.0.1.bin
├── linka-firmware-v0.0.2.bin
├── linka-firmware-v0.0.3.bin
└── ...
```
### versions file format
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
