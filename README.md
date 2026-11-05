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
