# Mosaik Simulations development environment

This project includes a full development environment for working with Mosaik Co-simulator framework using Development Containers for Visual Studio Code.

## How to get started

To run this environment you only need `Visual Studio Code` with `devcontainers extension` and `Docker`. Everything else is included in the development environment. If you are familiar with devcontainers and have all of the required software installed, simply open VSCode and start the devcontainer via VSCode, otherwise follow the steps below: 

1. Install [Visual Studio Code](https://code.visualstudio.com/) and [Docker](https://www.docker.com/) (Docker Desktop is recommended for easy setup if you are not familiar with docker)
2. Start Docker (or if you installed it, Docker Desktop)
3. Start Visual Studio Code and open the folder of this project (upon opening, you should get a notification for recommended extension which includes `devcontainers` which you should install)
    - If you didn't get recommended `devcontainers` extension: click on the "extensions" menu icon on the left sidebar in Visual Studio Code and type `ms-vscode-remote.remote-containers` to the find the correct extension and install it
5. You should get prompted to "Reopen the folder in Container", click on it and wait for the container to start
    - If you didn't get prompted to open the folder in a Dev Container, you can manually start and open the development environment by clicking on the icon on bottom left with a tooltip that says "Open a Remote window" and clicking on "Reopen in Container" option in the menu that is opened
6. Doing this for the first time might take awhile depending on your internet speed, but your Visual Studio Code window should now be connected to the Development Environment! Read on to get an idea about the workflow inside the development environment

Once you are done you can try running a Mosaik Simulation Example by running the following command in the integrated terminal (if an integrated terminal is not open use the following shortcut: `CTRL+J`):

```bash
python src/ex_scenario_csvload.py
```

This will create a simulation results file at the root of the project `simresults_ex_scenario_csvload.hdf5` which you can open in your DevContainer-connected VSCode by just clicking it.

## Exploring the development environment

Now that you have a development environment open, let's explain a few things:

### the dev container

The dev environment is inside a docker container. If you are unfamiliar with containers: a container is basically a portable, self-contained environment that holds everything an app needs to run (code, tools, settings). We can use containers to ensure a project works the same everywhere, regardless of your own computer setup. [A more detailed explanation can be found on docker's official website](https://www.docker.com/resources/what-container/). For this development environment we use a Debian Linux based Python image.

### this project inside the dev container

This project folder is "mounted" to the development environment, so changes to the files inside this folder are persistent. Other changes to the container are not persistent and the development environment itself is reset every time you exit the environment. An example: you install a python package with `pip`, `apt` or install a Visual Studio Code extension while connected to the dev container and then exit the dev container. Next time you open the project in the dev container these installations are not available and need to be reinstalled. If you want to persist python package installations you need to update requirements.txt.

### running commands and scripts inside the dev container

You can open a terminal in your Visual Studio Code that is connected to the dev environment with `CTRL+J` (or top menu bar > Terminal > New Terminal). In this terminal you have full access to the development environment's file system and can find your working folder under `/workspaces` folder. You should be automatically inside the correct folder and be able to run e.g. `python src/ex_scenario_csvload.py` command.

### python packages

Python packages in requirements.txt are automatically installed when you start this dev container in the global scope of the container, so you don't need to (but can if you want to) set up a python virtual environment.

### making persistent changes to the dev container itself

If you want to make a change to the environment of the dev container itself that should be persistent (e.g. adding an VSCode extension or an APT package) you can do so by editing the files in `.devcontainer/` folder. `.devcontainer/devcontainer.json` file has the full configuration of the container itself and `post-create-script.sh` is called after container creation.

## Mosaik and running simulations

Mosaik simulation scenarios should be in the `src/` folder and can be run within the terminal simply with `python src/my_sim_scenario.py`. If you are generating simulation data results into a HDF5 file you can view the data in this development environment by simply clicking on the file (HDF5 viewer VSCode extension is included in the dev container).

## Extra notes, known issues, etc.

### What about VSCodium and Podman?

Unfortunately Dev Containers extension is not available for VSCodium. If you want to run this project inside a dev container on VSCodium you could take a look at [devpodcontainers project](https://github.com/3timeslazy/vscodium-devpodcontainers) which also is aware of Podman Container Engine (this project has not yet been tested with devpodcontainers extension).

### Why isn't uv included in the Dev Container?

While [uv](https://docs.astral.sh/uv/) is a very powerful piece of Python tooling, we thought that we'd leave it out for the sake of simplicity. If uv is desired, it can easily be added to the Dev Container by e.g. adding the installation to the `.devcontainer/post-create-script.sh` script. 

## Data, License, and information about Mosaik

Simbench datasets included in this project are [licensed under the Open Database License](https://simbench.de/en/download/). Mosaik is created and developed by OFFIS e.V. and is [licensed under LGPL](https://gitlab.com/mosaik/mosaik/-/blob/develop/LICENSE.txt).