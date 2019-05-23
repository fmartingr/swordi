Swordi
-

Just an experiment to try out asyncio.

- [Requirements](#requirements)
- [Running the server](#running-the-server)
- [Running the client](#running-the-client)
  - [Commands](#commands)
    - [`join`](#join)
    - [`leave`](#leave)
    - [`say`](#say)
    - [`quit`](#quit)

## Requirements

- Python 3.6+
- [Poetry](https://github.com/sdispater/poetry)
- (optional) [direnv](https://github.com/direnv/direnv)

## Running the server

```
poetry run server
```

## Running the client

```
poetry run client
```

### Commands

#### `join`

Joins a room

```
join general
```

#### `leave`

Leaves a room

```
leave general
```

#### `say`

Say something in the current room

```
say Hello there!
```

#### `quit`

Closes de client and discconects from the server.
