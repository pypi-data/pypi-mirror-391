import re

from biolib.biolib_errors import BioLibError
from biolib.typing_utils import Optional, TypedDict


class SemanticVersion(TypedDict):
    major: int
    minor: int
    patch: int


class ResourceUriParsed(TypedDict):
    account_handle_normalized: str
    app_name_normalized: Optional[str]
    app_name: Optional[str]
    resource_name_prefix: Optional[str]
    version: Optional[SemanticVersion]
    tag: Optional[str]


def normalize(string: str) -> str:
    return string.replace('-', '_').lower()


def parse_resource_uri(uri: str, use_account_as_name_default: bool = True) -> ResourceUriParsed:
    uri_regex = re.compile(
        r'^(@(?P<resource_name_prefix>[\w._-]+)/)?'
        r'(?P<account_handle>[\w-]+)'
        r'(/(?P<app_name>[\w-]+))?'
        r'(?::(?P<suffix>[^:]+))?$'
    )
    semver_regex = re.compile(r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$')
    tag_regex = re.compile(r'^[a-z0-9-]{1,255}$')

    matches = uri_regex.match(uri)
    if matches is None:
        raise BioLibError(f"Could not parse app uri '{uri}', uri did not match regex")

    version: Optional[SemanticVersion] = None
    tag: Optional[str] = None

    suffix = matches.group('suffix')
    if suffix:
        if suffix == '*':
            pass
        elif semver_match := semver_regex.fullmatch(suffix):
            version = SemanticVersion(
                major=int(semver_match.group('major')),
                minor=int(semver_match.group('minor')),
                patch=int(semver_match.group('patch')),
            )
        elif tag_regex.fullmatch(suffix):
            tag = suffix
        else:
            raise BioLibError(
                f'Invalid tag name "{suffix}". Tag names must contain only lowercase alphanumeric '
                'characters and dashes, and must not exceed 255 characters.'
            )

    resource_name_prefix: Optional[str] = matches.group('resource_name_prefix')
    account_handle_normalized: str = normalize(matches.group('account_handle'))
    app_name: Optional[str] = matches.group('app_name')

    if app_name:
        app_name_normalized = normalize(app_name)
    elif use_account_as_name_default:
        app_name_normalized = account_handle_normalized
    else:
        app_name_normalized = None

    return ResourceUriParsed(
        resource_name_prefix=resource_name_prefix.lower() if resource_name_prefix is not None else 'biolib.com',
        account_handle_normalized=account_handle_normalized,
        app_name_normalized=app_name_normalized,
        app_name=app_name if app_name is not None or not use_account_as_name_default else account_handle_normalized,
        version=version,
        tag=tag,
    )
