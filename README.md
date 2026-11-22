# linka-ota-server

Remote OTA Server for [Linka sensors](https://github.com/melizeche/AireLibre/) using [linka-firmware](https://github.com/garyservin/linka-firmware)

## Firmware tracks
Each sensor follows one of two tracks, chosen by the "Server for OTA upgrades" URL in
its setup page:

| Track | Sensor URL | Serves |
|---|---|---|
| production | `https://linka.servin.dev/ota` (the default) | `latest` in the versions file |
| devel | `https://linka.servin.dev/ota/devel` | `devel`, or `latest` when that is newer or `devel` is not set |

So devel sensors get release candidates first, and move on to the release once it is
published. `/ota/production` is the same as `/ota`.

The firmware of a track can be downloaded from `/latest_firmware` (production, used by
the web flasher) and `/latest_firmware/devel`.

Firmware is deployed to a track by the "Deploy firmware" workflow, which linka-firmware
triggers for every release: releases go to production, pre-releases to devel. To run
it by hand, e.g. to roll back:
```
gh workflow run deploy-firmware.yml -f version=X.Y.Z -f track=production|devel|none
```

## Development instructions
### Using uv
Install [uv](https://docs.astral.sh/uv/), then:
```
$ uv sync
$ uv run pytest
$ uv run gunicorn --bind 0.0.0.0:5000 'linka_ota_server:create_app()'
```
Firmware files are read from `bin/` in the repo (see below). Set `FIRMWARE_PATH` to use
another directory.

### Using docker compose
Build the image locally and start the service:
```
docker compose up -d --build
```

## Deployment
`.github/workflows/ci.yml` builds and publishes the Docker image to
`ghcr.io/garyservin/linka-ota-server`:

| Event | Tests | Image tags pushed | Deployed |
|---|---|---|---|
| Pull request | ✅ | none (build only) | no |
| Push to `master` | ✅ | `edge`, `sha-<commit>` | no |
| Tag `vX.Y.Z` | ✅ | `X.Y.Z`, `X.Y`, `latest`, `sha-<commit>` | yes |

### Releasing a new version
The git tag is the version: there is no version to bump in the code
(`version` in `pyproject.toml` is a placeholder).

1. Merge the changes to `master`.
2. Create the release from `master`, choosing the next version:
   ```
   gh release list --limit 1        # latest release
   gh release create vX.Y.Z --target master --generate-notes
   ```
3. CI checks that the tag is a version (`vX.Y.Z`) and is on `master`, publishes the
   image and deploys it with the self-hosted runner in `/home/gary/linka/linka-ota-server`.
   The deploy waits until `/version` reports the new version, and writes `IMAGE_TAG=X.Y.Z`
   to `.env` there.

Check the running version with `curl https://linka.servin.dev/version`.

### Rolling back
On the server, next to `compose.yaml` and the `bin/` firmware directory:
```
IMAGE_TAG=X.Y.Z docker compose up -d
```
(and update `IMAGE_TAG` in `.env`), or re-run the deploy job of that release in GitHub Actions.

The firmware is not part of the image: it is read from `bin/`, which is mounted at `/app/bin`.

## Testing the endpoints
Set `BASE` to the server to test (e.g. `http://127.0.0.1:5000` for a local one):
```sh
BASE=https://linka.servin.dev
```

### Service
```sh
curl -i "$BASE/up"                  # 200, empty body
curl "$BASE/version"                # {"version":"X.Y.Z"}
curl -I "$BASE/"                    # 200, web flasher page
curl "$BASE/manifest.json"          # web flasher manifest
```

### Firmware downloads
Each track's firmware: the file name gives its version. `/latest_firmware` is the one
the web flasher installs.
```sh
curl -sSI "$BASE/latest_firmware" | grep -i disposition        # production file name
curl -sS "$BASE/latest_firmware" | md5sum                      # production md5
curl -sSI "$BASE/latest_firmware/devel" | grep -i disposition  # devel file name
curl -sS "$BASE/latest_firmware/devel" | md5sum                # devel md5

curl -OJ "$BASE/latest_firmware"                   # save the production file
curl -i -X OPTIONS "$BASE/latest_firmware"         # CORS preflight, 200
```

### OTA, as a sensor would ask
`/ota` answers 403 without the headers an ESP8266 sends, so define them once, plus a
helper that prints the status, the md5 of the firmware offered and its file name:
```sh
ESP=(-H "User-Agent: ESP8266-http-Update"
     -H "x-ESP8266-STA-MAC: AA:BB:CC:DD:EE:FF" -H "x-ESP8266-AP-MAC: AA:BB:CC:DD:EE:FE"
     -H "x-ESP8266-free-space: 2000000" -H "x-ESP8266-sketch-size: 400000"
     -H "x-ESP8266-chip-size: 4194304" -H "x-ESP8266-sdk-version: 2.2.2")

# ota <path> <version the sensor runs> <md5 of its firmware>
ota() {
  curl -sS -o /dev/null "${ESP[@]}" -H "x-ESP8266-version: $2" -H "x-ESP8266-sketch-md5: $3" \
    -w "%{http_code} %header{x-md5} %header{content-disposition}\n" "$BASE$1"
}
```
Then, using the versions and md5s of each track from above:
```sh
ota /ota 0.0.0 0                               # sensor on an old version: 200, offered production
ota /ota <production version> <production md5> # sensor up to date: 304
ota /ota/production <production version> <production md5>   # same as /ota: 304
ota /ota/devel 0.0.0 0                         # devel sensor on an old version: 200, offered devel
ota /ota/devel <devel version> <devel md5>     # devel sensor up to date: 304

curl -sS -o /dev/null -w "%{http_code}\n" "$BASE/ota"   # no ESP headers: 403
ota /ota/beta 0.0.0 0                                     # unknown track: 404
```
200 means a sensor in that state would update to the firmware shown, 304 that it already
runs it. Replace `-o /dev/null` with `-o fw.bin` to keep the firmware. `%header{...}`
needs curl 7.84 or newer; with an older curl, use `-D -` to print all response headers.

## Firmware directory storage
### Directory hierarchy
Your directory should look like this
```
bin
├── versions
├── linka-firmware-v0.0.1.bin
├── linka-firmware-v0.0.2.bin
├── linka-firmware-v0.0.3.bin
├── linka-firmware-v0.0.4-rc.1.bin
└── ...
```
### versions file format
The `versions` file is a json file containing each firmware version with the following format
```
{
    "latest": "0.0.3",
    "devel": "0.0.4-rc.1",
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
    },
    "0.0.4-rc.1": {
        "file": "linka-firmware-v0.0.4-rc.1.bin",
        "md5sum": "5d41402abc4b2a76b9719d911017c592"
    }
}
```
`latest` is the production version and `devel` (optional) the devel version.
