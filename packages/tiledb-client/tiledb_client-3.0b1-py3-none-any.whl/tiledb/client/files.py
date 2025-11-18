"""TileDB File Assets

The functions of this module allow a TileDB File to be downloaded to a
local filesystem, or uploaded from a local filesystem to TileDB so that
it becomes a catalog asset.

"""

import logging
import pathlib
from os import PathLike
from typing import BinaryIO, Optional, Union

import tiledb
from tiledb.client import client
from tiledb.client._common.api_v4 import FilesApi
from tiledb.client.folders import Teamspace

from .assets import Asset
from .assets import AssetType
from .assets import _normalize_ids
from .assets import get_asset
from .rest_api import ApiException
from .tiledb_cloud_error import maybe_wrap

logger = logging.getLogger(__name__)


class FilesError(tiledb.TileDBError):
    """Raised when a file transfer operation fails."""


def download_file(
    teamspace: Union[Teamspace, str],
    path: str,
    file: Union[BinaryIO, str],
) -> None:
    """Download a file from a teamspace.

    Parameters
    ----------
    teamspace : Teamspace or str
        The teamspace to which the downloaded file belongs.
    path : str
        The path of the file to be downloaded.
    file : BinaryIO or str
        The file to be written.

    Returns
    -------
    None

    Raises
    ------
    FilesError:
        If the file download failed.

    Examples
    --------
    >>> files.download_file(
    ...     "teamspace",
    ...     "README.md",
    ...     open("README.md", "wb"),
    ... )

    Notes
    -----
    The current implementation makes a copy of the file in memory
    before writing to the output file.

    """
    try:
        api_instance = client.client.build(FilesApi)
        resp = api_instance.file_get(
            client.get_workspace_id(),
            getattr(teamspace, "teamspace_id", teamspace),
            path,
            _preload_content=False,
        )
    except ApiException as exc:
        raise FilesError("The file download failed.") from exc
    else:
        file.write(resp.read())


def upload_file(
    file: Union[BinaryIO, PathLike, bytes, bytearray, memoryview],
    path: Union[object, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
    content_type: str = "application/octet-stream",
) -> None:
    """Upload a file to a teamspace.

    Parameters
    ----------
    file : BinaryIO, PathLike, or Buffer
        The file to be uploaded.
    path : str or object
        The TileDB path at which the file is to be registered. May be
        a path relative to a teamspace, a `Folder` or `Asset` instance,
        or an absolute "tiledb" URI. If the path to a folder is
        provided, the basename of the file will be appended to form
        a full asset path.
    teamspace : Teamspace or str, optional
        The teamspace to which the file will be registered, specified
        by object or id. If not provided, the `path` parameter is
        queried for a teamspace id.
    content_type: str, optional
        The content type of the uploaded file.

    Raises
    ------
    FilesError:
        If the file upload failed.

    Examples
    --------
    >>> folder = folders.create_folder(
    ...     "files",
    ...     teamspace="teamspace",
    ...     exists_ok=True,
    ... )
    >>> upload_file(
    ...     open("README.md", "rb"),
    ...     "files",
    ...     teamspace="teamspace",
    ...     content_type="text/markdown",
    ... )

    This creates a file asset at path "files/README.md" in the teamspace
    named "teamspace". The file's basename has been used to construct
    the full path.

    If you like, you can pass a Folder or Asset object instead of a path
    string and get the same result.

    >>> upload_file(
    ...     open("README.md", "rb"),
    ...     folder,
    ...     teamspace="teamspace",
    ...     content_type="text/markdown",
    ... )

    If you like, you can pass a Folder or Asset object instead of a path
    string and get the same result.

    >>> register_udf(get_tiledb_version, folder)

    A file can also be registered to a specific absolute "tiledb" URI
    that specifies a different name.

    >>> files.upload_file(
    ...     open("README.md", "rb"),
    ...     "tiledb://workspace/teamspace/files/index.md",
    ...     content_type="text/markdown",
    ... )

    Notes
    -----
    The current implementation copies the file in memory
    before submiting it to the server.

    """
    teamspace_id, path_id = _normalize_ids(teamspace, path)
    api_instance = client.client.build(FilesApi)
    api_instance.api_client.set_default_header("Content-Type", content_type)

    if hasattr(file, "read"):
        fileobj = file
        if hasattr(file, "name"):
            file_name = pathlib.Path(file.name).name
        else:
            file_name = None
        data = fileobj.read()
    elif isinstance(file, (str, PathLike)):
        file_path = pathlib.Path(file)
        file_name = file_path.name
        fileobj = file_path.open("rb")
        data = fileobj.read()
    else:
        mv = memoryview(file)
        data = mv[:].tobytes()
        file_name = None

    # TODO: upload in chunks.

    try:
        api_instance.upload_part(
            client.get_workspace_id(),
            teamspace_id,
            path_id,
            data,
        )
    except ApiException:
        # Is there a folder at path? If so, try again.
        ast: Asset = get_asset(path_id, teamspace=teamspace_id)
        if ast and ast.type == AssetType.FOLDER:
            if not file_name:
                raise FilesError(
                    "An unnamed sequence of bytes can not be uploaded to a folder."
                )
            logger.info(
                "Upload targeting a folder: file=%r, teamspace_id=%r, path_id=%r",
                file,
                teamspace_id,
                path_id,
            )
            target_path = pathlib.Path(ast.path).joinpath(file_name).as_posix()

            try:
                api_instance.upload_part(
                    client.get_workspace_id(),
                    teamspace_id,
                    target_path,
                    data,
                )
            except ApiException as exc2:
                raise FilesError(
                    "Upload of a file to a folder failed."
                ) from maybe_wrap(exc2)

    except ApiException as exc:
        raise FilesError("The file upload failed.") from maybe_wrap(exc)
    finally:
        api_instance.api_client.default_headers.pop("Content-Type")
