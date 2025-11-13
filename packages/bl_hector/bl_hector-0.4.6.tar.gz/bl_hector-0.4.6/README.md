# Hector — a collection manager

## Install

Hector is available on PyPI under the name `bl_hector`.
To install, just run `python -m pip install bl_hector`.


## Configure

Hector is configured using environment variables.
See [the `settings` module](bl_hector/infrastructure/settings.py) for
a comprehensive list of configuration variables.

All the variable names must be prefixed with `HECTOR_`. For instance :

```console
# The secret can be generated using the `secrets.token_hex()` function.
$ export HECTOR_SECRET_KEY="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

# Additional Python database drivers might be required depending on the DSN.
$ export HECTOR_DSN="sqlite:///data.sqlite"
```


## Authentication

To enable WebAuthn authentication, you must install extra dependencies (`bl-hector[webauthn]`)
and enable it explicitly:

```console
$ export HECTOR_WEBAUTHN_ENABLED=1
```

TOTP authentication is provided to be able to login on servers that do not (yet) support
the `cryptography` module. You must install extra dependencies (`bl-hector[totp]`)
and enable it explicitly by setting a base32 random secret:

```console
# The secret can be generated using the `pyotp.random_base32()` function.
$ export HECTOR_TOTP_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Note that it is a highly insecure way of authenticating, as anyone gaining access to your
OTP generator would be able to login.


## Initialise

Once configured, you must initialise Hector's database with the dedicated command:

```console
$ hector init-db
```


## Run

Hector being a Flask application, it can be run using any WSGI server,
for instance, with [Gunicorn](https://gunicorn.org):

```console
$ gunicorn --access-logfile="-" -w 4 -b 127.0.0.1:3000 "bl_hector.configuration.wsgi:app()"
```


## Contributing

See [CONTRIBUTING.md]() to set up a development environment.
