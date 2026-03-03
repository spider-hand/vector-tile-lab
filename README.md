# Vector Tile Lab

![demo](https://github.com/user-attachments/assets/3542c06d-2744-4069-927f-895cd8fb6d76)

[![Docker Build](https://github.com/spider-hand/vector-tile-lab/actions/workflows/docker-build.yml/badge.svg)](https://github.com/spider-hand/vector-tile-lab/actions/workflows/docker-build.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A local development tool for experimenting with vector tiles.

It allows you to convert GeoJSON or Shapefile into vector tiles and quickly preview the visualization through an interactive map.

## Features

- 🐳 **Zero configuration** - Set up and launch with a single command
- ⚡️ **Fast iteration** - Preview your vector tiles quickly
- 🗺️ **Visualization** - Generate a beautiful map

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

This project works without any configuration, but if you want to use some additional features with Mapbox map, you can set their token on `client/.env`:

`.env`

```
VITE_MAPBOX_TOKEN=your_mapbox_token
```

## Contributing

- Bug fix PRs are always welcome.
- UI changes or new features should not be submitted without prior discussion. Please open an issue first to propose and discuss them.

Thanks for your understanding and contributions.

## License

[MIT](./LICENSE)
