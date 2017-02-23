from . import archive
# import makesig
from . import exceptions
import os
from os.path import dirname, join, realpath

# this comes with the repo
PACKAGE_ROOT = dirname(realpath(__file__))
APPLE_CERT_PATH = join(PACKAGE_ROOT, 'apple_credentials', 'applecerts.pem')

# We will default to using credentials if they are located in a particular
# directory. Sauce Labs in 2015 uses a scheme under '~/isign-credentials'
# but probably everyone else should use '~/.isign', or specify credential
# files in command line arguments.
try:
    DEFAULT_CREDENTIALS_PATH = join(os.environ['HOME'], 'isign-credentials')
    CERTIFICATE_PATH = join(DEFAULT_CREDENTIALS_PATH, 'mobdev.cert.pem')
    KEY_PATH = join(DEFAULT_CREDENTIALS_PATH, 'mobdev.key.pem')
    PROVISIONING_PROFILE_PATH = join(DEFAULT_CREDENTIALS_PATH,
                                     'mobdev1.mobileprovision')
except Exception as e:
    DEFAULT_CREDENTIALS_PATH = join(os.environ['HOME'], '.isign')
    CERTIFICATE_PATH = join(DEFAULT_CREDENTIALS_PATH, 'certificate.pem')
    KEY_PATH = join(DEFAULT_CREDENTIALS_PATH, 'key.pem')
    PROVISIONING_PROFILE_PATH = join(DEFAULT_CREDENTIALS_PATH,
                                     'isign.mobileprovision')


class NotSignable(Exception):
    """ This is just so we don't expose other sorts of exceptions """
    pass


def get_credential_paths(directory, file_names=DEFAULT_CREDENTIAL_FILE_NAMES):
    """ Given a directory, return dict of paths to standard
        credential files """
    paths = {}
    for (k, file_name) in file_names.iteritems():
        paths[k] = join(directory, file_name)
    return paths


# We will default to using credentials in a particular
# directory with well-known names. This is complicated because
# the old way at Sauce Labs (pre-2017) was:
#   ~/isign-credentials/mobdev.cert.pem, etc.
# But the new way that everyone should now use:
#   ~/.isign/certificate.pem, etc.
if exists(join(os.environ['HOME'], 'isign-credentials')):
    DEFAULT_CREDENTIAL_PATHS = get_credential_paths(
        join(os.environ['HOME'], 'isign-credentials'),
        {
            'certificate': 'mobdev.cert.pem',
            'key': 'mobdev.key.pem',
            'provisioning_profile': 'mobdev1.mobileprovision'
        }
    )
else:
    DEFAULT_CREDENTIAL_PATHS = get_credential_paths(
        join(os.environ['HOME'], '.isign')
    )


def resign_with_creds_dir(input_path,
                          credentials_directory,
                          **kwargs):
    """ Do isign.resign(), but with credential files from this directory """
    kwargs.update(get_credential_paths(credentials_directory))
    return resign(input_path, **kwargs)


def resign(input_path,
           apple_cert=DEFAULT_APPLE_CERT_PATH,
           certificate=DEFAULT_CREDENTIAL_PATHS['certificate'],
           key=DEFAULT_CREDENTIAL_PATHS['key'],
           provisioning_profile=DEFAULT_CREDENTIAL_PATHS['provisioning_profile'],
           output_path=join(os.getcwd(), "out"),
           info_props=None):
    """ Mirrors archive.resign(), put here for convenience, to unify exceptions,
        and to omit default args """
    try:
        return archive.resign(input_path,
                              certificate,
                              key,
                              apple_cert,
                              provisioning_profile,
                              output_path,
                              info_props)
    except exceptions.NotSignable as e:
        # re-raise the exception without exposing internal
        # details of how it happened
        raise NotSignable(e)


def view(input_path):
    """ Obtain information about the app """
    try:
        return archive.view(input_path)
    except exceptions.NotSignable as e:
        raise NotSignable(e)
