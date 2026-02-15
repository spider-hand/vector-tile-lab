# vector-tile-lab

![demo](https://github.com/user-attachments/assets/028904ff-a1d9-41bb-9102-c1df77b696f2)

[![Docker Build](https://github.com/spider-hand/vector-tile-lab/actions/workflows/docker-build.yml/badge.svg)](https://github.com/spider-hand/vector-tile-lab/actions/workflows/docker-build.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A local development tool for visualizing and experimenting with vector tiles

It allows you to convert GeoJSON into vector tiles, tweak Tippecanoe parameters, and immediately see how those changes affect rendering through an interactive map-based UI.

## Features

- 🚀 **Zero configuration** - Launch everything with a single command. No manual setup required
- 🗺️ **Interactive visualization** - Instantly preview generated vector tiles on an interactive map
- ⚡ **Fast iteration** - Adjust Tippecanoe parameters and regenerate tiles without leaving the UI

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
