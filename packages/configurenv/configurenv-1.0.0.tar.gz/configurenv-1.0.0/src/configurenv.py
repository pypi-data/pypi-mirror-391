import json
import logging
import os
from pathlib import Path
from typing import MutableMapping, Mapping

import yaml

logger = logging.getLogger(__name__)

LOADERS = {
    '.json': json.load,
    '.yml': yaml.safe_load,
    '.yaml': yaml.safe_load,
}


def load_config_from_files(config: MutableMapping):
    """Iterates over the keys in `config`. For any with the format "{NAME}_FILE",
    treat its value as a filename. Reads that file using the appropriate loader
    (".json" files use `json.load`, and ".yml" and ".yaml" files use `yaml.safe_load`)
    and set the config key "{NAME}" to the return value of the loader.

    After loading, uses `envsubst` to apply substitutions to the loaded object. You
    may use any of the keys currently defined in the config;

    Ignores a "{NAME}_FILE" key if "{NAME}" is already defined in config (i.e.,
    "{NAME}" takes precedence over "{NAME}_FILE").

    Raises a `RuntimeError` if the file suffix is unrecognized, or if the file
    cannot be opened."""
    file_keys = [k for k in config.keys() if k.endswith('_FILE')]
    for file_key in file_keys:
        # strip the "_FILE" suffix
        key = file_key[:-5]
        if key not in config:
            # only load from file if there isn't already a config value with this key
            file = Path(config[file_key])
            try:
                loader = LOADERS[file.suffix]
            except KeyError as e:
                raise RuntimeError(f'Cannot open a config file with suffix "{file.suffix}"') from e
            try:
                with file.open() as fh:
                    config[key] = envsubst(loader(fh), config)
            except FileNotFoundError as e:
                raise RuntimeError(f'Config file "{file}" not found') from e


def envsubst(value: str | list | dict, env: Mapping[str, str] = None) -> str | list | dict:
    """
    Recursively replace `${VAR_NAME}` placeholders in value with the values of the
    corresponding keys of `env`. If `env` is not given, it defaults to the environment
    variables in `os.environ`.

    Any placeholders that do not have a corresponding key in the `env` dictionary
    are left as is.

    :param value: String, list, or dictionary to search for `${VAR_NAME}` placeholders.
    :param env: Dictionary of values to use as replacements. If not given, defaults
        to `os.environ`.
    :return: If `value` is a string, returns the result of replacing `${VAR_NAME}` with the
        corresponding `value` from env. If `value` is a list, returns a new list where each
        item in `value` replaced with the result of calling `envsubst()` on that item. If
        `value` is a dictionary, returns a new dictionary where each item in `value` is replaced
        with the result of calling `envsubst()` on that item.
    """
    if env is None:
        env = os.environ
    if isinstance(value, str):
        if '${' in value:
            try:
                return value.replace('${', '{').format(**env)
            except KeyError as e:
                missing_key = str(e.args[0])
                logger.warning(f'Environment variable ${{{missing_key}}} not found')
                # for a missing key, just return the string without substitution
                return envsubst(value, {missing_key: f'${{{missing_key}}}', **env})
        else:
            return value
    elif isinstance(value, list):
        return [envsubst(v, env) for v in value]
    elif isinstance(value, dict):
        return {k: envsubst(v, env) for k, v in value.items()}
    else:
        return value
