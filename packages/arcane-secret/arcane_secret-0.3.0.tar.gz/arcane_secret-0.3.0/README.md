# Arcane secret
This package allows to encode and decode secrets.

## Get Started

```sh
pip install arcane-secret
```

## Example Usage

```python
from arcane.secret import decode

decoded_secret = decode('secret', 'path_to_secret_key_file')
```

or

```python
from arcane.secret import encode

# Import your configs
from configure import Config

encoded_secret = encode(secret, Config.SECRET_KEY_FILE)
```
