# Team39
The application is intended for use within the context of simulation games.
A simulation game is designed to build first-person experience of a simulated scenario.
In this case, it's student teachers within a simulated school environment

## Development

### Installing dependencies

First of all, make sure you have [uv](https://docs.astral.sh/uv/) installed.

Then, use uv to install the required dependencies.

```sh
uv sync
```

### Running the project

To run the project use the following command.

```sh
uv run rat
```

### Packaging to an executable

The application can be packed into a single executable by running the following command **on the target platform**, with the matching spec file specified.

```sh
uv run pyinstaller <spec file>
```
