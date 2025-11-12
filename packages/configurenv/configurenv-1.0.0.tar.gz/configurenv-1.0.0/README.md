# configurenv

Utilities for simplifying application configuration

## Description

This package provides two functions: [`envsubst`](#envsubst) and 
[`load_config_from_file`](#load_config_from_file).

`envsubst` was created to allow runtime substitution of environment
variables into otherwise static configuration files.

`load_config_from_file` was created to extend [Flask] app configuration by 
reading configuration values from files specified by keys of the shape 
`{NAME}_FILE`. After passing those configuration values though `envsubst` 
(using the existing configuration as the context environment), it updates 
the `{NAME}` key of the original configuration.

## Dependencies

* Python 3.10+
* [PyYAML]

## Installation

```zsh
pip install configurenv
```

## Usage

### envsubst

With this environment:

```dotenv
SERVER_NAME=test.example.com
```

Running this Python code:

```python
from configurenv import envsubst

url = envsubst('http://${SERVER_NAME}/endpoint')
```

Results in `url` having the value `'http://test.example.com/endpoint'`.

### load_config_from_file

Typical usage is in the setup phase of a [Flask] app, after loading the 
initial config from somewhere else (often from environment variables).

With this environment:

```dotenv
MYAPP_USERNAME=jdoe
MYAPP_COLORMAP_FILE=colors.yml
```

And this *colors.yml* file:

```yaml
danger: red
warning: yellow
alert: orange
info: blue
```

Running this Python code:

```python
from flask import Flask
from configurenv import load_config_from_files

app = Flask(__name__)
app.config.from_prefixed_env('MYAPP')

load_config_from_files(app.config)
```

Will result in `app.config` containing these keys and values:

```python
{
    'USERNAME': 'jdoe',
    'COLORMAP_FILE': 'colors.yml',
    'COLORMAP': {
        'danger': 'red',
        'warning': 'yellow',
        'alert': 'orange',
        'info': 'blue',
    },
}
```

The *colors.yml* could also refer to other configuration values.

With this environment:

```dotenv
MYAPP_USERNAME=jdoe
MYAPP_DANGER_COLOR=hotpink
MYAPP_COLORMAP_FILE=colors.yml
```

And this *colors.yml* file:

```yaml
danger: ${DANGER_COLOR}
warning: yellow
alert: orange
info: blue
```

Running the same Python code as above will result in `app.config` 
containing these keys and values:

```python
{
    'USERNAME': 'jdoe',
    'DANGER_COLOR': 'hotpink',
    'COLORMAP_FILE': 'colors.yml',
    'COLORMAP': {
        'danger': 'hotpink',
        'warning': 'yellow',
        'alert': 'orange',
        'info': 'blue',
    },
}
```

## Development Setup

```zsh
git clone git@github.com:umd-lib/configurenv.git
cd configurenv
pyenv install $(cat .python-version) --skip-existing
python -m venv .venv --prompt "$(basename $PWD)-py$(cat .python-version)"
source .venv/bin/activate
pip install -e .[test]
```

### Testing

Using [pytest]:

```zsh
pytest
```

With test coverage information:

```zsh
pytest --cov-report=term-missing --cov src
```

### Code Style

Using [ruff]:

```zsh
ruff check
```

## History

`envsubst` originated in the [Plastron] project of the [UMD Libraries]; 
see also [plastron.utils.envsubst]

`load_config_from_files` originated in [Solrizer] project of the
[UMD Libraries]; see also [solrizer.web.load_config_from_files]

[PyYAML]: https://pypi.org/project/PyYAML/
[Flask]: https://flask.palletsprojects.com/
[pytest]: https://pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[UMD Libraries]: https://github.com/umd-lib
[Plastron]: https://github.com/umd-lib/plastron
[plastron.utils.envsubst]: https://github.com/umd-lib/plastron/blob/4.6.0/plastron-utils/src/plastron/utils/__init__.py#L81
[Solrizer]: https://github.com/umd-lib/solrizer
[solrizer.web.load_config_from_files]: https://github.com/umd-lib/solrizer/blob/1.3.0/src/solrizer/web.py#L156
