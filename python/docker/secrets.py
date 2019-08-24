import os

secrets_directory = "/run/secrets"


def get(secret_name, default_value=None):
    """
    Get a docker secret
    :param secret_name:
    :param default_value:
    :return:
    """
    secret_file = os.path.join(secrets_directory, secret_name)
    try:
        with open(secret_file, 'r') as fpt:
            value = fpt.read()
    except IOError:
        if default_value is not None:
            value = default_value
        else:
            raise ValueError(f"Unable to read secret {secret_name}")
    return value
