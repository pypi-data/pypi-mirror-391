import fused
from fused.core._fs_utils import is_non_empty_dir


@fused.udf(cache_max_age=0)
def udf_extract(
    src_path: str,
    chunk_id: int,
    x_chunks: int,
    y_chunks: int,
    tmp_path: str,
    res: int,
    k_ring: int,
    parent_offset: int,
    file_res: int,
    chunk_name: str | None = None,
):
    # define UDF that imports the helper function inside the UDF
    from job2.partition.raster_to_h3 import udf_extract as run_udf_extract

    run_udf_extract(
        src_path,
        chunk_id,
        x_chunks,
        y_chunks,
        tmp_path,
        res=res,
        k_ring=k_ring,
        parent_offset=parent_offset,
        file_res=file_res,
        chunk_name=chunk_name,
    )


def run_extract(
    src_path: str | list[str],
    tmp_path: str,
    x_chunks: int,
    y_chunks: int,
    chunk_ids: list[int] = None,
    res: int = 12,
    k_ring: int = 1,
    parent_offset: int = 1,
    file_res: int = 2,
    debug_mode: bool = False,
    **kwargs,
):
    """
    Chunk up the input raster file, extract pixel values and assign to H3 cells.

    Parameters
    ----------
    src_path : str
        Path to the input raster file.
    tmp_path : str
        Path to store intermediate files.
    x_chunks : int
        Number of chunks in the x direction.
    y_chunks : int
        Number of chunks in the y direction.
    chunk_ids : list of int, default None
        List of chunk IDs to process, default to all.
    res : int
        The resolution at which to assign the pixel values to H3 cells.
    k_ring : int
        The k-ring distance at resolution `res` to which the pixel value
        is assigned (in addition to the center cell).
    parent_offset : int
        Offset to parent resolution to which to assign the pixel values
        and counts
    file_res : int
        The H3 resolution to chunk the resulting files of the Parquet dataset

    """

    params = {
        "tmp_path": tmp_path,
        "x_chunks": x_chunks,
        "y_chunks": y_chunks,
        #
        "res": res,
        "k_ring": k_ring,
        "parent_offset": parent_offset,
        "file_res": file_res,
    }

    if isinstance(src_path, str):
        params["src_path"] = src_path

        if chunk_ids is None:
            chunk_ids = range(x_chunks * y_chunks)
            if debug_mode:
                # avoid creating huge submit_params list in case of tiny target_chunk_size
                chunk_ids = range(2)

        submit_params = [{"chunk_id": i} for i in chunk_ids]
    else:
        params["chunk_id"] = 0
        submit_params = [
            {"src_path": p, "chunk_name": p.split("/")[-1].rsplit(".", maxsplit=1)[0]}
            for p in src_path
        ]

    if debug_mode:
        submit_params = submit_params[:2]

    print(f"-- processing {len(submit_params)} chunks")

    pool = fused.submit(
        udf_extract,
        submit_params,
        **params,
        collect=False,
        **kwargs,
    )
    return pool


@fused.udf(cache_max_age=0)
def udf_partition(
    file_id: int,
    tmp_path: str,
    output_path: str,
    metrics: list[str],
    groupby_cols: list[str] = ["hex", "data"],
    window_cols: list[str] = ["hex"],
    additional_cols: list[str] = [],
    chunk_res: int = 3,
    overview_res: list = [3, 4, 5, 6],
):
    # define UDF that imports the helper function inside the UDF
    from job2.partition.raster_to_h3 import udf_partition as run_udf_partition

    run_udf_partition(
        file_id,
        tmp_path,
        output_path,
        metrics=metrics,
        groupby_cols=groupby_cols,
        window_cols=window_cols,
        additional_cols=additional_cols,
        chunk_res=chunk_res,
        overview_res=overview_res,
    )


def run_partition(
    tmp_path: str,
    file_ids: list[str],
    output_path: str,
    metrics: list[str] = ["cnt"],
    groupby_cols: list[str] = ["hex", "data"],
    window_cols: list[str] = ["hex"],
    additional_cols: list[str] = [],
    chunk_res: int = 3,
    overview_res: list = [3, 4, 5, 6],
    debug_mode: bool = False,
    **kwargs,
):
    """
    Combine chunks per file_id H3 cell and recalculate data.

    Parameters
    ----------
    tmp_path : str
        Path where the intermediate files to combine are stored.
    output_path : str
        Path for the resulting Parquet dataset.
    chunk_res : int
        The H3 resolution to chunk the row groups within each file of the Parquet dataset
    overview_res : list of int
        The H3 resolutions for which to create overview files.

    """
    params = {
        "tmp_path": tmp_path,
        "output_path": output_path,
        #
        "metrics": metrics,
        "groupby_cols": groupby_cols,
        "window_cols": window_cols,
        "additional_cols": additional_cols,
        "chunk_res": chunk_res,
        "overview_res": overview_res,
    }
    submit_params = [{"file_id": i} for i in file_ids]

    if debug_mode:
        submit_params = submit_params[:2]

    pool = fused.submit(
        udf_partition,
        submit_params,
        **params,
        collect=False,
        **kwargs,
    )
    return pool


def _create_tmp_path(src_path: str, output_path: str, cache_id: int) -> str:
    src_path_part = src_path.replace("/", "_").replace(":", "_").replace(".", "_")
    if output_path.startswith("file:///"):
        # create local tmp path
        import tempfile

        local_tmp_dir = tempfile.gettempdir()
        tmp_path = f"file://{local_tmp_dir}/fused-tmp/tmp/{src_path_part}-{cache_id}/"
    else:
        api = fused.api.FusedAPI()
        tmp_path = api._resolve(f"fd://fused-tmp/tmp/{src_path_part}-{cache_id}/")

    if is_non_empty_dir(tmp_path):
        raise ValueError(
            f"Temporary path {tmp_path} is not empty. Remove the directory first "
            "manually, or specify a different `cache_id=..` to change the generated "
            "tmp_path."
        )

    return tmp_path


def _cleanup_tmp_files(tmp_path: str, remove_tmp_files: bool):
    if remove_tmp_files:
        _delete_path(tmp_path)


def _delete_path(path: str):
    if path.startswith("file://"):
        import shutil

        shutil.rmtree(path.replace("file://", ""), ignore_errors=True)
    else:
        orig = fused.options.request_timeout
        fused.options.request_timeout = 30
        fused.api.delete(path)
        fused.options.request_timeout = orig


def _list_files(path: str):
    if path.startswith("file://"):
        from pathlib import Path

        path = Path(path.replace("file://", ""))
        return [str(p) for p in path.iterdir() if p.is_file()]
    else:
        orig = fused.options.request_timeout
        fused.options.request_timeout = 10
        files = [
            path.url
            for path in fused.api.list(path, details=True)
            if not path.is_directory
        ]
        fused.options.request_timeout = orig
        return files


def _list_tmp_file_ids(tmp_path: str):
    if tmp_path.startswith("file://"):
        from pathlib import Path

        path = Path(tmp_path.replace("file://", ""))
        file_ids = [p.name for p in path.iterdir() if p.is_dir()]
    else:
        orig = fused.options.request_timeout
        fused.options.request_timeout = 10
        file_ids = [path.strip("/").split("/")[-1] for path in fused.api.list(tmp_path)]
        fused.options.request_timeout = orig
    return file_ids


def infer_defaults(
    src_path: str,
    res: int | None = None,
    file_res: int | None = None,
    chunk_res: int | None = None,
    k_ring: int = 1,
    parent_offset: int = 1,
):
    import math

    import h3.api.basic_int as h3
    import pyproj
    import rasterio

    if res is None:
        with rasterio.open(src_path) as src:
            src_crs = pyproj.CRS(src.crs)
            # estimate target resolution based on pixel size
            # -> use resolution where 7 cells would roughly cover one pixel
            if src_crs.is_projected:
                pixel_area = (
                    (src.bounds.right - src.bounds.left)
                    / src.width
                    * (src.bounds.top - src.bounds.bottom)
                    / src.height
                )
            else:
                # approximate pixel area in m^2 at center of raster
                transformer = pyproj.Transformer.from_crs(
                    src_crs, "EPSG:3857", always_xy=True
                )
                x_center = (src.bounds.right + src.bounds.left) / 2
                y_center = (src.bounds.top + src.bounds.bottom) / 2
                x1, y1 = transformer.transform(x_center, y_center)
                x2, y2 = transformer.transform(
                    x_center + (src.bounds.right - src.bounds.left) / src.width,
                    y_center + (src.bounds.top - src.bounds.bottom) / src.height,
                )
                pixel_area = abs((x2 - x1) * (y2 - y1))

            n_cells = max(7 * k_ring, 1)
            # get lat/lng of center
            transformer = pyproj.Transformer.from_crs(
                src_crs, "EPSG:4326", always_xy=True
            )
            lng, lat = transformer.transform(
                (src.bounds.right + src.bounds.left) / 2,
                (src.bounds.top + src.bounds.bottom) / 2,
            )

            for res in range(15, 0, -1):
                if h3.cell_area(h3.latlng_to_cell(lat, lng, res), "m^2") > (
                    pixel_area / n_cells
                ):
                    break

    target_res = res - parent_offset

    if file_res is None:
        # target is to have files around 100MB up to 1 GB in size:
        # with the current compression and typical dataset with the
        # `hex, data, cnt, cnt_total` columns, a rought estimate is that
        # we have 1 byte per row.
        # (and assuming a minimum of one value for each cell in the target
        # resolution)
        file_res = target_res - math.ceil(math.log(100_000_000, 7))
        file_res = max(file_res, 0)

    if chunk_res is None:
        # choose a chunk_res such that each row group has
        # at least 1,000,000 rows, assuming we have one value for each cell
        # in the target resolution
        # (typical recommendation of 100,000 rows gives to small row groups
        # with our files with few columns)
        chunk_res = target_res - math.floor(math.log(1_000_000, 7))
        # with a minimum of +2 compared to the file resolution,
        # to ensure we have multiple (10+) row groups per file
        chunk_res = max(chunk_res, file_res + 2)

    return res, file_res, chunk_res


def run_ingest_raster_to_h3(
    src_path: str | list[str],
    output_path: str,
    metrics: str | list[str] = "cnt",
    res: int | None = None,
    k_ring: int = 1,
    parent_offset: int = 1,
    chunk_res: int | None = None,
    file_res: int | None = None,
    overview_res: list[int] | None = None,
    overview_chunk_res: int | list[int] | None = None,
    target_chunk_size: int = 10_000_000,
    debug_mode: bool = False,
    remove_tmp_files: bool = True,
    cache_id: int = 0,
    overwrite: bool = False,
    extract_kwargs={},
    partition_kwargs={},
    **kwargs,
):
    """
    Run the raster to H3 ingestion process.

    This process involves multiple steps:
    - extract pixels values and assign to H3 cells in chunks (extract step)
    - combine the chunks per partition (file) and prepare metadata (partition step)
    - create the metadata `_sample` file and overviews files

    Parameters
    ----------
    src_path : str, list
        Path(s) to the input raster data. When this is a single path, the file
        is chunked up for processing based on `target_chunk_size`.
        When this is a list of paths, each file is processed as one chunk.
    output_path : str
        Path for the resulting Parquet dataset.
    metrics : str or list of str
        The metrics to compute per H3 cell. Supported metrics are either "cnt"
        or a list containing any of "avg", "min", "max", "stddev", and "sum".
    res : int
        The resolution at which to assign the pixel values to H3 cells.
    k_ring : int
        The k-ring distance at resolution `res` to which the pixel value
        is assigned (in addition to the center cell).
    parent_offset : int
        Offset to parent resolution (relative to `res`) to which to assign
        the pixel values and counts.
    file_res : int
        The H3 resolution to chunk the resulting files of the Parquet dataset
    chunk_res : int
        The H3 resolution to chunk the row groups within each file of the
        Parquet dataset
    overview_res : list of int
        The H3 resolutions for which to create overview files. By default,
        overviews are created for resolutions 3 to 7 (or capped at a lower
        value if the `res` of the output dataset is lower).
    overview_chunk_res : int or list of int
        The H3 resolution to chunk the row groups within each overview file of the
        Parquet dataset. By default, each overview file is chunked at the overview
        resolution minus 5 (clamped between 0 and the `res` of the output dataset).
    target_chunk_size : int
        The approximate number of pixel values to process per chunk in
        the first "extract" step.
    debug_mode : bool, default False
        If True, run only the first two chunks for debugging purposes.
    remove_tmp_files : bool, default True
        If True, remove the temporary files after ingestion is complete.
    cache_id : int, default 0
        An identifier to use for the temporary path to avoid collisions
         when running multiple ingestions simultaneously.
    overwrite : bool, default False
        If True, overwrite the output path if it already exists, by first
        removing the existing content before writing the new files.
    extract_kwargs : dict
        Additional keyword arguments to pass to `fused.submit` for the extract step.
    partition_kwargs : dict
        Additional keyword arguments to pass to `fused.submit` for the partition step.
    **kwargs
        Additional keyword arguments to pass to `fused.submit` for
        both the extract and partition steps. Keys specified here are further
        overridden by those in `extract_kwargs` and `partition_kwargs` respectively.

    The extract and partition steps are run in parallel using fused.submit. By
    default, the function will first attempt to run this using "realtime"
    instances, and retry any failed runs using "large" instances.

    You can override this behavior by specifying the `engine`, `instance_type`,
    `max_workers`, `n_processes_per_worker`, etc parameters as additional
    keyword arguments to this function (`**kwargs`). If you want to specify
    those per step, use `extract_kwargs` and `partition_kwargs`.
    For example, to run everything locally on the same machine where this
    function runs, use:

        run_ingest_raster_to_h3(..., engine="local")

    To run the extract step on realtime and the partition step on medium
    instance, you could do:

        run_ingest_raster_to_h3(...,
            extract_kwargs={"instance_type": "realtime", "max_workers": 256, "max_retry": 1},
            partition_kwargs={"instance_type": "medium", "max_workers": 5, "n_processes_per_worker": 2},
        )
    """
    import datetime

    import numpy as np
    import rasterio

    try:
        from job2.partition.raster_to_h3 import (
            udf_overview,
            udf_sample,
        )
    except ImportError:
        raise RuntimeError(
            "The ingestion functionality can only be run using the remote engine"
        )

    result_extract = None
    result_partition = None

    is_single_file = isinstance(src_path, str)
    # use single file for inferring defaults and creating paths
    src_path_file = src_path if is_single_file else src_path[0]

    print(
        f"Starting ingestion process for {src_path_file}{' ({} files)'.format(len(src_path)) if not is_single_file else ''}\n"
    )
    start_time = datetime.datetime.now()

    # Validate output path and verify that it is empty
    output_path = str(output_path)
    if not output_path.endswith("/"):
        output_path += "/"
    if is_non_empty_dir(output_path):
        if overwrite:
            print(f"-- Overwriting existing output path {output_path}")
            _delete_path(output_path)
        else:
            raise ValueError(
                f"Output path {output_path} is not empty. If you want to remove "
                "existing files, specify `overwrite=True`."
            )

    # Construct path for intermediate results
    tmp_path = _create_tmp_path(src_path_file, output_path, cache_id)
    print(f"-- Using {tmp_path=}")

    res, file_res, chunk_res = infer_defaults(
        src_path_file,
        res,
        file_res,
        chunk_res,
        k_ring=k_ring,
        parent_offset=parent_offset,
    )
    print(
        f"\n-- Using {res=} (target res={res - parent_offset}), {file_res=}, {chunk_res=}"
    )

    if isinstance(metrics, str):
        metrics = [metrics]
    else:
        metrics = list(metrics)
        if len(metrics) > 1 and "cnt" in metrics:
            raise ValueError("The 'cnt' metric cannot be combined with other metrics")

    if overview_res is None:
        max_overview_res = min(res - parent_offset - 1, 7)
        overview_res = list(range(3, max_overview_res + 1))

    ###########################################################################
    # Step one: extracting pixel values and converting to hex divided in chunks

    print("\nRunning extract step")
    start_extract_time = datetime.datetime.now()

    if isinstance(src_path, str):
        # determine number of chunks based on target chunk size
        with rasterio.open(src_path) as src:
            meta = src.meta

        x_chunks = max(round(meta["width"] / np.sqrt(target_chunk_size)), 1)
        y_chunks = max(round(meta["height"] / np.sqrt(target_chunk_size)), 1)
    else:
        # for now assume that each input file is a single chunk
        x_chunks = 1
        y_chunks = 1

    extract_run_kwargs = dict(
        src_path=src_path,
        tmp_path=tmp_path,
        x_chunks=x_chunks,
        y_chunks=y_chunks,
        res=res,
        k_ring=k_ring,
        parent_offset=parent_offset,
        file_res=file_res,
        debug_mode=debug_mode,
    )
    extract_submit_kwargs = {"max_retry": 0} | kwargs | extract_kwargs

    # Run the actual extract step
    if not (
        extract_submit_kwargs.get("engine", None) == "local"
        or "instance_type" in extract_submit_kwargs
    ):
        # default logic: try realtime and fallback to large instance
        extract_submit_kwargs["instance_type"] = "realtime"
        result_extract = run_extract(
            **extract_run_kwargs,
            **extract_submit_kwargs,
        )
        result_extract.wait()
        if not result_extract.all_succeeded():
            errors = result_extract.errors()
            print(
                f"-- Extract step failed on realtime instances ({len(errors)} out of "
                f"{result_extract.n_jobs} runs, first error: {next(iter(errors.values()))}), "
                "retrying failed runs on large instances"
            )
            if is_single_file:
                extract_run_kwargs["chunk_ids"] = list(errors.keys())
            else:
                extract_run_kwargs["src_path"] = [
                    src_path[i] for i in list(errors.keys())
                ]
            extract_submit_kwargs["instance_type"] = "large"
            result_extract = run_extract(
                **extract_run_kwargs,
                **extract_submit_kwargs,
            )
            result_extract.wait()
    else:
        # otherwise run once with user provided configuration
        result_extract = run_extract(
            **extract_run_kwargs,
            **extract_submit_kwargs,
        )
        result_extract.wait()

    end_extract_time = datetime.datetime.now()
    if not result_extract.all_succeeded():
        print("\nExtract step failed!")
        try:
            _cleanup_tmp_files(tmp_path, remove_tmp_files)
        except Exception:
            pass
        return result_extract, result_partition
    print(f"-- Done extract! (took {end_extract_time - start_extract_time})")

    ###########################################################################
    # Step two: combining the chunks per file (resolution 2) and preparing
    # metadata and overviews

    print("\nRunning partition step")

    # list available file_ids from the previous step
    file_ids = _list_tmp_file_ids(tmp_path)
    print(f"-- processing {len(file_ids)} file_ids")

    partition_run_kwargs = dict(
        tmp_path=tmp_path,
        file_ids=file_ids,
        output_path=output_path,
        metrics=metrics,
        chunk_res=chunk_res,
        overview_res=overview_res,
    )
    partition_submit_kwargs = {"max_retry": 0} | kwargs | partition_kwargs

    # Run the actual partition step
    if not (
        partition_submit_kwargs.get("engine", None) == "local"
        or "instance_type" in partition_submit_kwargs
    ):
        # default logic: try realtime and fallback to large instance
        partition_submit_kwargs["instance_type"] = "realtime"
        result_partition = run_partition(
            **partition_run_kwargs,
            **partition_submit_kwargs,
        )
        result_partition.wait()
        if not result_partition.all_succeeded():
            errors = result_partition.errors()
            print(
                f"-- Partition step failed on realtime instances ({len(errors)} out of "
                f"{result_partition.n_jobs} runs, first error: {next(iter(errors.values()))}), "
                "retrying failed runs on large instances"
            )
            partition_run_kwargs["file_ids"] = [file_ids[i] for i in errors.keys()]
            partition_submit_kwargs["instance_type"] = "large"
            result_partition = run_partition(
                **partition_run_kwargs,
                **partition_submit_kwargs,
            )
            result_partition.wait()
    else:
        # otherwise run once with user provided configuration
        result_partition = run_partition(
            **partition_run_kwargs,
            **partition_submit_kwargs,
        )
        result_partition.wait()

    end_partition_time = datetime.datetime.now()
    if not result_partition.all_succeeded():
        print("\nPartition step failed!")
        _cleanup_tmp_files(tmp_path, remove_tmp_files)
        return result_extract, result_partition
    print(f"-- Done partition! (took {end_partition_time - end_extract_time})")

    ###########################################################################
    # Step 3: combining the metadata and overview tmp files

    print("\nRunning sample step")

    @fused.udf(cache_max_age=0)
    def udf_sample(tmp_path: str, output_path: str):
        from job2.partition.raster_to_h3 import udf_sample as run_udf_sample

        return run_udf_sample(tmp_path, output_path)

    sample_file = fused.run(
        udf_sample,
        tmp_path=tmp_path,
        output_path=output_path,
        verbose=False,
        engine=kwargs.get("engine", None),
    )
    end_sample_time = datetime.datetime.now()
    print(f"-- Written: {sample_file}")
    print(f"-- Done sample! (took {end_sample_time - end_partition_time})")

    print("\nRunning overview step")

    @fused.udf(cache_max_age=0)
    def udf_overview(tmp_path: str, output_path: str, res: int, chunk_res: int):
        from job2.partition.raster_to_h3 import udf_overview as run_udf_overview

        return run_udf_overview(tmp_path, output_path, res=res, chunk_res=chunk_res)

    for overview_res_index, current_overview_res in enumerate(overview_res):
        current_overview_chunk_res = (
            max(min(current_overview_res - 5, res), 0)
            if overview_chunk_res is None
            else overview_chunk_res
            if isinstance(overview_chunk_res, int)
            else overview_chunk_res[overview_res_index]
        )
        overview_file = fused.run(
            udf_overview,
            tmp_path=tmp_path,
            output_path=output_path,
            res=current_overview_res,
            chunk_res=current_overview_chunk_res,
            verbose=False,
            engine=kwargs.get("engine", None),
        )
        print(
            f"-- Written: {overview_file} res={current_overview_res} chunk_res={current_overview_chunk_res}"
        )

    end_overview_time = datetime.datetime.now()
    print(f"-- Done overview! (took {end_overview_time - end_sample_time})")

    # remove tmp files
    _cleanup_tmp_files(tmp_path, remove_tmp_files)

    print(f"\nIngestion process done! (took {datetime.datetime.now() - start_time})")

    return result_extract, result_partition


@fused.udf(cache_max_age=0)
def udf_divide(
    src_path: str,
    tmp_path: str,
    chunk_name: str,
    file_res: int = 2,
):
    # define UDF that imports the helper function inside the UDF
    from job2.partition.raster_to_h3 import write_by_file_res

    write_by_file_res(
        src_path,
        tmp_path,
        chunk_name,
        file_res=file_res,
    )


def run_partition_to_h3(
    input_data,
    output_path: str,
    metrics: str | list[str] = "cnt",
    groupby_cols: list[str] = ["hex", "data"],
    window_cols: list[str] = ["hex"],
    additional_cols: list[str] = [],
    res: int | None = None,
    # k_ring: int = 1,
    # parent_offset: int = 1,
    chunk_res: int | None = None,
    file_res: int | None = None,
    overview_res: list = [3, 4, 5, 6],
    # target_chunk_size: int = 10_000_000,
    # debug_mode: bool = False,
    remove_tmp_files: bool = True,
    cache_id: int = 0,
    overwrite: bool = False,
    extract_kwargs={},
    partition_kwargs={},
    **kwargs,
):
    """
    Run the raster to H3 ingestion process.

    This process involves multiple steps:
    - extract pixels values and assign to H3 cells in chunks (extract step)
    - combine the chunks per partition (file) and prepare metadata (partition step)
    - create the metadata `_sample` file and overviews files

    Parameters
    ----------
    src_path : str, list
        Path(s) to the input raster data. When this is a single path, the file
        is chunked up for processing based on `target_chunk_size`.
        When this is a list of paths, each file is processed as one chunk.
    output_path : str
        Path for the resulting Parquet dataset.
    metrics : str or list of str
        The metrics to compute per H3 cell. Supported metrics are either "cnt"
        or a list containing any of "avg", "min", "max", "stddev", and "sum".
    res : int
        The resolution at which to assign the pixel values to H3 cells.
    k_ring : int
        The k-ring distance at resolution `res` to which the pixel value
        is assigned (in addition to the center cell).
    parent_offset : int
        Offset to parent resolution (relative to `res`) to which to assign
        the pixel values and counts.
    file_res : int
        The H3 resolution to chunk the resulting files of the Parquet dataset
    chunk_res : int
        The H3 resolution to chunk the row groups within each file of the
        Parquet dataset
    overview_res : list of int
        The H3 resolutions for which to create overview files. By default,
        overviews are created for resolutions 3 to 7 (or capped at a lower
        value if the `res` of the output dataset is lower).
    target_chunk_size : int
        The approximate number of pixel values to process per chunk in
        the first "extract" step.
    debug_mode : bool, default False
        If True, run only the first two chunks for debugging purposes.
    remove_tmp_files : bool, default True
        If True, remove the temporary files after ingestion is complete.
    cache_id : int, default 0
        An identifier to use for the temporary path to avoid collisions
         when running multiple ingestions simultaneously.
    overwrite : bool, default False
        If True, overwrite the output path if it already exists, by first
        removing the existing content before writing the new files.
    extract_kwargs : dict
        Additional keyword arguments to pass to `fused.submit` for the extract step.
    partition_kwargs : dict
        Additional keyword arguments to pass to `fused.submit` for the partition step.
    **kwargs
        Additional keyword arguments to pass to `fused.submit` for
        both the extract and partition steps. Keys specified here are further
        overridden by those in `extract_kwargs` and `partition_kwargs` respectively.

    The extract and partition steps are run in parallel using fused.submit. By
    default, the function will first attempt to run this using "realtime"
    instances, and retry any failed runs using "large" instances.

    You can override this behavior by specifying the `engine`, `instance_type`,
    `max_workers`, `n_processes_per_worker`, etc parameters as additional
    keyword arguments to this function (`**kwargs`). If you want to specify
    those per step, use `extract_kwargs` and `partition_kwargs`.
    For example, to run everything locally on the same machine where this
    function runs, use:

        run_ingest_raster_to_h3(..., engine="local")

    To run the extract step on realtime and the partition step on medium
    instance, you could do:

        run_ingest_raster_to_h3(...,
            extract_kwargs={"instance_type": "realtime", "max_workers": 256, "max_retry": 1},
            partition_kwargs={"instance_type": "medium", "max_workers": 5, "n_processes_per_worker": 2},
        )
    """
    import datetime

    try:
        from job2.partition.raster_to_h3 import (
            udf_overview,
            udf_sample,
        )
    except ImportError:
        raise RuntimeError(
            "The ingestion functionality can only be run using the remote engine"
        )

    result_extract = None
    result_partition = None

    if not isinstance(input_data, str):
        raise NotImplementedError
    src_path = input_data

    is_single_file = isinstance(src_path, str)
    # use single file for inferring defaults and creating paths
    src_path_file = src_path if is_single_file else src_path[0]

    print(
        f"Starting ingestion process for {src_path_file}{' ({} files)'.format(len(src_path)) if not is_single_file else ''}\n"
    )
    start_time = datetime.datetime.now()

    # Validate output path and verify that it is empty
    output_path = str(output_path)
    if not output_path.endswith("/"):
        output_path += "/"
    if is_non_empty_dir(output_path):
        if overwrite:
            print(f"-- Overwriting existing output path {output_path}")
            _delete_path(output_path)
        else:
            raise ValueError(
                f"Output path {output_path} is not empty. If you want to remove "
                "existing files, specify `overwrite=True`."
            )

    # Construct path for intermediate results
    tmp_path = _create_tmp_path(src_path_file, output_path, cache_id)
    print(f"-- Using {tmp_path=}")

    if res is None:
        raise ValueError("res must be specified for now")

    res, file_res, chunk_res = infer_defaults(
        None,
        res,
        file_res,
        chunk_res,
    )
    print(f"\n-- Using {res=}, {file_res=}, {chunk_res=}")

    if isinstance(metrics, str):
        metrics = [metrics]
    else:
        metrics = list(metrics)
        if len(metrics) > 1 and "cnt" in metrics:
            raise ValueError("The 'cnt' metric cannot be combined with other metrics")

    if "hex" not in groupby_cols:
        raise ValueError("groupby_cols must contain 'hex'")

    if overview_res is None:
        max_overview_res = min(res - 1, 7)
        overview_res = list(range(3, max_overview_res + 1))

    ###########################################################################
    # Step one: splitting data per file

    print("\nRunning extract step")
    start_extract_time = datetime.datetime.now()

    files = _list_files(input_data)
    print(f"-- processing {len(files)} chunks")

    extract_run_params = dict(
        tmp_path=tmp_path,
        file_res=file_res,
    )
    extract_submit_params = [
        {"src_path": p, "chunk_name": str(i)} for i, p in enumerate(files)
    ]
    extract_submit_kwargs = {"max_retry": 0} | kwargs | extract_kwargs
    result_extract = fused.submit(
        udf_divide,
        extract_submit_params,
        **extract_run_params,
        collect=False,
        **extract_submit_kwargs,
    )
    result_extract.wait()

    end_extract_time = datetime.datetime.now()
    if not result_extract.all_succeeded():
        print("\nExtract step failed!")
        try:
            _cleanup_tmp_files(tmp_path, remove_tmp_files)
        except Exception:
            pass
        return result_extract, result_partition
    print(f"-- Done extract! (took {end_extract_time - start_extract_time})")

    ###########################################################################
    # Step two: combining the chunks per file (resolution 2) and preparing
    # metadata and overviews

    print("\nRunning partition step")

    # list available file_ids from the previous step
    file_ids = _list_tmp_file_ids(tmp_path)
    print(f"-- processing {len(file_ids)} file_ids")

    partition_run_kwargs = dict(
        tmp_path=tmp_path,
        file_ids=file_ids,
        output_path=output_path,
        metrics=metrics,
        groupby_cols=groupby_cols,
        window_cols=window_cols,
        additional_cols=additional_cols,
        chunk_res=chunk_res,
        overview_res=overview_res,
    )
    partition_submit_kwargs = {"max_retry": 0} | kwargs | partition_kwargs

    # Run the actual partition step
    if not (
        partition_submit_kwargs.get("engine", None) == "local"
        or "instance_type" in partition_submit_kwargs
    ):
        # default logic: try realtime and fallback to large instance
        partition_submit_kwargs["instance_type"] = "realtime"
        result_partition = run_partition(
            **partition_run_kwargs,
            **partition_submit_kwargs,
        )
        result_partition.wait()
        if not result_partition.all_succeeded():
            errors = result_partition.errors()
            print(
                f"-- Partition step failed on realtime instances ({len(errors)} out of "
                f"{result_partition.n_jobs} runs, first error: {next(iter(errors.values()))}), "
                "retrying failed runs on large instances"
            )
            partition_run_kwargs["file_ids"] = [file_ids[i] for i in errors.keys()]
            partition_submit_kwargs["instance_type"] = "large"
            result_partition = run_partition(
                **partition_run_kwargs,
                **partition_submit_kwargs,
            )
            result_partition.wait()
    else:
        # otherwise run once with user provided configuration
        result_partition = run_partition(
            **partition_run_kwargs,
            **partition_submit_kwargs,
        )
        result_partition.wait()

    end_partition_time = datetime.datetime.now()
    if not result_partition.all_succeeded():
        print("\nPartition step failed!")
        _cleanup_tmp_files(tmp_path, remove_tmp_files)
        return result_extract, result_partition
    print(f"-- Done partition! (took {end_partition_time - end_extract_time})")

    ###########################################################################
    # Step 3: combining the metadata and overview tmp files

    print("\nRunning sample step")

    @fused.udf(cache_max_age=0)
    def udf_sample(tmp_path: str, output_path: str):
        from job2.partition.raster_to_h3 import udf_sample as run_udf_sample

        return run_udf_sample(tmp_path, output_path)

    sample_file = fused.run(
        udf_sample,
        tmp_path=tmp_path,
        output_path=output_path,
        verbose=False,
        engine=kwargs.get("engine", None),
    )
    end_sample_time = datetime.datetime.now()
    print(f"-- Written: {sample_file}")
    print(f"-- Done sample! (took {end_sample_time - end_partition_time})")

    print("\nRunning overview step")

    @fused.udf(cache_max_age=0)
    def udf_overview(tmp_path: str, output_path: str, res: int):
        from job2.partition.raster_to_h3 import udf_overview as run_udf_overview

        return run_udf_overview(tmp_path, output_path, res=res)

    for res in overview_res:
        overview_file = fused.run(
            udf_overview,
            tmp_path=tmp_path,
            output_path=output_path,
            res=res,
            verbose=False,
            engine=kwargs.get("engine", None),
        )
        print(f"-- Written: {overview_file}")

    end_overview_time = datetime.datetime.now()
    print(f"-- Done overview! (took {end_overview_time - end_sample_time})")

    # remove tmp files
    _cleanup_tmp_files(tmp_path, remove_tmp_files)

    print(f"\nIngestion process done! (took {datetime.datetime.now() - start_time})")

    return result_extract, result_partition
