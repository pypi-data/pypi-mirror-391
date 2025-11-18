import re

from biolib._shared.types.resource import ResourceUriDict, SemanticVersionDict
from biolib.biolib_errors import BioLibError
from biolib.typing_utils import Optional

URI_REGEX = re.compile(
    r'^(@(?P<resource_prefix>[\w._-]+)/)?'
    r'(?P<account_handle>[\w-]+)'
    r'(/(?P<resource_name>[\w-]+))?'
    r'(?::(?P<suffix>[^:]+))?$'
)
SEMVER_REGEX = re.compile(r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$')
TAG_REGEX = re.compile(r'^[a-z0-9-]{1,255}$')


def normalize_resource_name(string: str) -> str:
    return string.replace('-', '_').lower()


def parse_resource_uri(uri: str, use_account_as_name_default: bool = True) -> ResourceUriDict:
    matches = URI_REGEX.match(uri)
    if matches is None:
        raise BioLibError(f"Could not parse resource uri '{uri}', uri did not match regex")

    version: Optional[SemanticVersionDict] = None
    tag: Optional[str] = None

    suffix = matches.group('suffix')
    if suffix:
        if suffix == '*':
            pass
        elif semver_match := SEMVER_REGEX.fullmatch(suffix):
            version = SemanticVersionDict(
                major=int(semver_match.group('major')),
                minor=int(semver_match.group('minor')),
                patch=int(semver_match.group('patch')),
            )
        elif TAG_REGEX.fullmatch(suffix):
            tag = suffix
        else:
            raise BioLibError(
                f'Invalid tag name "{suffix}". Tag names must contain only lowercase alphanumeric '
                'characters and dashes, and must not exceed 255 characters.'
            )

    resource_prefix_raw: Optional[str] = matches.group('resource_prefix')
    resource_prefix = resource_prefix_raw.lower() if resource_prefix_raw is not None else None
    account_handle: str = matches.group('account_handle')
    account_handle_normalized: str = normalize_resource_name(account_handle)
    resource_name: Optional[str] = matches.group('resource_name')

    if resource_name:
        resource_name_normalized = normalize_resource_name(resource_name)
    elif use_account_as_name_default:
        resource_name_normalized = account_handle_normalized
    else:
        resource_name_normalized = None

    return ResourceUriDict(
        resource_prefix=resource_prefix,
        account_handle=account_handle,
        account_handle_normalized=account_handle_normalized,
        resource_name_normalized=resource_name_normalized,
        resource_name=resource_name if resource_name is not None or not use_account_as_name_default else account_handle,
        version=version,
        tag=tag,
    )
