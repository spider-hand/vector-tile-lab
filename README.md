# vector-tile-lab

![demo](https://github.com/user-attachments/assets/d401ee31-79af-42f3-8142-93486a80a2c9)

[![Docker Build](https://github.com/spider-hand/vector-tile-lab/actions/workflows/docker-build.yml/badge.svg)](https://github.com/spider-hand/vector-tile-lab/actions/workflows/docker-build.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Vector Tile Lab is a local development tool for experimenting with your vector tiles. It lets you convert GeoJSON into vector tiles, tweak Tippecanoe parameters and visualize data through interactive UI.

## Features
- Zero config - Launch with a single command, no manual setup required
- Instant iteration - Adjust tile generation parameters and test outputs immediately
- Visual insights - Compare tilesets through interactive charts and performance metrics

## Quick Start

### Prerequisite

- [Docker](https://www.docker.com/)

1. Clone this repository:

```sh
git clone https://github.com/spider-hand/vector-tile-lab.git
cd vector-tile-lab
```

2. Set up environment variables:

```sh
cp .env.example .env
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Change the values if needed.

3. Build and start the services:

```sh
docker-compose up --build -d
```

## Contributing
- Bug fix PRs are always welcome.
- UI changes or new features should not be submitted without prior discussion. Please open an issue first to propose and discuss them.

Thanks for your understanding and contributions.

## License
[MIT](./LICENSE)
