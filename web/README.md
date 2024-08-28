# RCD front-end

RCD stands for **R***esource* **C***onfiguration* **D***ata*.

This repository contains the web-based front-end for the RCD tool.

This project outputs the Front-end files (HTML , JS and CSS) which can be displayed by a modern web-browser.



It is based on [Vue.js v3](https://v3.vuejs.org) web-framework.

The style is provided by Ericsson Design System (EDS).

The bundler used by the project is [Vite](https://vitejs.dev).

## Development

### Requirements
- Node.js (14.17.1 LTS and after)
- npm (7.17.0 or higher)
  - playwright/test (1.15.2 or higher)

### Getting started

1. Navigate to the cloned repository's `web` folder.

2. Install all the dependencies from internet:
    ```bash
    npm install
    ```

3. Start development server on http://localhost:5001/
    ```bash
    ./dev.sh
    ```
    It will symlink `<reporoot>/data` to `<reporoot>/web/res/data`, so Vite will host the data as well during development.

## Build production output

### Output to local `dist` folder

Prerequisites: Getting Started steps 1-2.

1. Build optimized and minimized production output
    ```bash
    npm run build
    ```

2. Copy the content of `./dist` folder to your web-server

### Build docker image

Prerequisites: Getting Started steps 1-2.

1. Build docker image
    ```bash
    docker build -t <registry>/rcd-web .
    ```
2. Push image to registry
    ```bash
    docker push <registry>/rcd-web
    ```

## Project architecture and details

Please check [`./docs/README.md`](./docs/README.md) for more information.
