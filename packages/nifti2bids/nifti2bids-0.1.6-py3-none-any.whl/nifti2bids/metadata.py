"""Utility functions to extract or create metadata."""

import datetime, re
from pathlib import Path
from typing import Any, Literal, Optional

import nibabel as nib, numpy as np

from ._exceptions import SliceAxisError, DataDimensionError
from ._decorators import check_all_none
from .io import load_nifti, get_nifti_header
from .logging import setup_logger

LGR = setup_logger(__name__)


@check_all_none(parameter_names=["nifti_file_or_img", "nifti_header"])
def determine_slice_axis(
    nifti_file_or_img: Optional[str | Path | nib.nifti1.Nifti1Image] = None,
    nifti_header: Optional[nib.nifti1.Nifti1Header] = None,
) -> int:
    """
    Determine the slice axis.

    Uses "slice_end" plus one to determine the likely slice axis.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image` default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_header`` is None.

    nifti_header: :obj:`Nifti1Header`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_file_or_img`` is None.

    Returns
    -------
    int
        A number representing the slice axis.
    """
    kwargs = {"nifti_file_or_img": nifti_file_or_img, "nifti_header": nifti_header}
    slice_end, hdr = get_hdr_metadata(
        **kwargs, metadata_name="slice_end", return_header=True
    )
    if not slice_end or np.isnan(slice_end):
        raise ValueError("'slice_end' metadata field not set.")

    n_slices = int(slice_end) + 1
    dims = np.array(hdr.get_data_shape()[:3])

    return np.where(dims == n_slices)[0][0]


def _is_numeric(value: Any) -> bool:
    """
    Check if value is a number.
    """
    return isinstance(value, (float, int))


def _to_native_numeric(value: np.floating | np.int_) -> float | int:
    """
    Ensures numpy floats and integers are converted
    to regular Python floats and integers.
    """
    return float(value) if isinstance(value, np.floating) else int(value)


@check_all_none(parameter_names=["nifti_file_or_img", "nifti_header"])
def get_hdr_metadata(
    metadata_name: str,
    nifti_file_or_img: Optional[str | Path | nib.nifti1.Nifti1Image] = None,
    nifti_header: Optional[nib.nifti1.Nifti1Header] = None,
    return_header: bool = False,
) -> Any | tuple[Any, nib.nifti1.Nifti1Header]:
    """
    Get metadata from a NIfTI header.

    Parameters
    ----------
    metadata_name: :obj:`str`
        Name of the metadata field to return.

    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_header`` is None.

    nifti_header: :obj:`Nifti1Header`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_file_or_img`` is None.

    return_header: :obj:`bool`
        Returns the NIfTI header

    Returns
    -------
    Any or tuple[Any, Nifti1Header]
        If ``return_header`` is False, only returns the associated
        value of the metadata. If ``return_header`` is True returns
        a tuple containing the assoicated value of the metadata
        and the NIfTI header.
    """
    hdr = nifti_header if nifti_header else get_nifti_header(nifti_file_or_img)
    metadata_value = hdr.get(metadata_name)
    metadata_value = (
        _to_native_numeric(metadata_value)
        if _is_numeric(metadata_value)
        else metadata_value
    )

    return metadata_value if not return_header else (metadata_value, hdr)


def get_n_volumes(nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image) -> int:
    """
    Get the number of volumes from a 4D NIftI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    int
        The number of volumes in img.
    """
    img = load_nifti(nifti_file_or_img)

    if is_3d_img(img):
        raise DataDimensionError("Image is 3D not 4D.")

    return img.get_fdata().shape[-1]


def get_n_slices(
    nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image,
    slice_axis: Optional[Literal["x", "y", "z"]] = None,
) -> int:
    """
    Gets the number of slices from the header of a NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    slice_axis: :obj:`Literal["x", "y", "z"]` or :obj:`None`, default=None
        Axis the image slices were collected in. If None,
        determines the slice axis using metadata ("slice_end")
        from the NIfTI header.

    Returns
    -------
    int
        The number of slices.
    """
    slice_dim_map = {"x": 0, "y": 1, "z": 2}

    hdr = get_nifti_header(nifti_file_or_img)
    if slice_axis:
        n_slices = hdr.get_data_shape()[slice_dim_map[slice_axis]]
        if slice_end := get_hdr_metadata(nifti_header=hdr, metadata_name="slice_end"):
            if not np.isnan(slice_end) and n_slices != slice_end + 1:
                raise SliceAxisError(slice_axis, n_slices, slice_end)

        slice_dim_indx = slice_dim_map[slice_axis]
    else:
        slice_dim_indx = determine_slice_axis(nifti_header=hdr)

    reversed_slice_dim_map = {v: k for v, k in slice_dim_map.items()}

    n_slices = hdr.get_data_shape()[slice_dim_indx]
    LGR.info(
        f"Number of slices based on "
        f"{reversed_slice_dim_map.get(slice_dim_indx)}: {n_slices}"
    )

    return _to_native_numeric(n_slices)


def get_tr(nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image) -> float:
    """
    Get the repetition time from the header of a NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    float
        The repetition time.
    """
    hdr = get_nifti_header(nifti_file_or_img)

    if not (tr := hdr.get_zooms()[3]):
        raise ValueError(f"Suspicious repetition time: {tr}.")

    LGR.info(f"Repetition Time: {tr}.")

    return round(_to_native_numeric(tr), 2)


def _flip_slice_order(slice_order: list[int], ascending: bool) -> list[int]:
    """
    Flip slice index order.

    Parameters
    ----------
    slice_order: :obj:`list[int]`
        List containing integer values representing the slices.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    Returns
    -------
    list[int]
        The order of the slices.
    """
    return np.flip(slice_order) if not ascending else slice_order


def _create_sequential_order(n_slices: int, ascending: bool = True) -> list[int]:
    """
    Create index ordering for sequential acquisition method.

    Parameters
    ----------
    n_slices: :obj:`int`
        The number of slices.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    Returns
    -------
    list[int]
        The order of the slices.
    """
    slice_order = list(range(0, n_slices))

    return _flip_slice_order(slice_order, ascending)


def _create_interleaved_order(
    n_slices: int,
    ascending: bool = True,
    interleaved_pattern: Literal["even", "odd", "philips"] = "odd",
) -> list[int]:
    """
    Create index ordering for interleaved acquisition method.

    .. note:: Equivalent to Philips default order.

    Parameters
    ----------
    n_slices: :obj:`int`
        The number of slices.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    interleaved_pattern: :obj:`Literal["even", "odd", "philips"]`, default="odd"
        If slices for interleaved acquisition were collected by acquiring the
        "even" or "odd" slices first. For "philips" (the interleaved implementation
        by Philips'), slices are acquired by a step factor equivalent to the rounded
        square root of the total slices.
        mode).

        .. important::
           Philips' "default" mode is equivalent to "interleave" with the pattern
           set to "odd", and ascending set to True.

    Returns
    -------
    list[int]
        The order of the slices.
    """
    if interleaved_pattern not in ["even", "odd", "philips"]:
        raise ValueError(
            "``interleaved_start`` must be either 'even', 'odd', or 'philips'."
        )

    if interleaved_pattern == "odd":
        slice_order = list(range(0, n_slices, 2)) + list(range(1, n_slices, 2))
    elif interleaved_pattern == "even":
        slice_order = list(range(1, n_slices, 2)) + list(range(0, n_slices, 2))
    else:
        step = round(np.sqrt(n_slices))
        slice_order = [
            slice_indx
            for base in range(step)
            for slice_indx in range(base, n_slices, step)
        ]

    return _flip_slice_order(slice_order, ascending)


def _create_singleband_timing(tr: float | int, slice_order: list[int]) -> list[float]:
    """
    Create singleband timing based on slice order.

    Parameters
    ----------
    tr: :obj:`float` or :obj:`int`
        Repetition time in seconds.

    slice_order: :obj:`list[int]`
        Order of the slices.

    Returns
    -------
    list[float]
        Ordered slice timing information.
    """
    n_slices = len(slice_order)
    slice_duration = tr / n_slices
    slice_timing = np.linspace(0, tr - slice_duration, n_slices)
    # Pair slice with timing then sort dict
    sorted_slice_timing = dict(
        sorted({k: v for k, v in zip(slice_order, slice_timing.tolist())}.items())
    )

    return list(sorted_slice_timing.values())


def _generate_sequence(
    start: int, n_count: int, step: int, ascending: bool
) -> list[int]:
    """
    Generate a sequence of numbers.

    Parameters
    ----------
    start: :obj:`int`
        Starting number.

    n_count: :obj:`int`
        The amount of numbers to generate.

    step: :obj:`int`
        Step size between numbers.

    ascending: :obj:`int`
        If numbers are ascending or descending relative to ``start``.

    Returns:
        list[int]
            The sequence list.
    """
    if ascending:
        stop = start + n_count * step
        return np.arange(start, stop, step).tolist()
    else:
        stop = start - n_count * step
        return np.arange(start, stop, -step).tolist()


def _create_multiband_slice_groupings(
    slice_order: list[int],
    multiband_factor: int,
    step_size: int,
    n_fake_slices: int,
    ascending: bool,
) -> list[tuple[int, int]]:
    """
    Create slice groupings for multiband based on ``multiband_factor``.

    Parameters
    ----------
    slice_order: :obj:`list[int]`
        Order of the slices from single slice acquisition.

    multiband_factor: :obj:`int`
        The multiband acceleration factor, which is the number of slices
        acquired simultaneously during multislice acquistion.

    step_size : :obj:`int`
        The step size between grouped slice indices computed by dividing
        the number of slices by the multiband factor.

    n_fake_slices: :obj:`int`
        The number of fake slices added to make total slices divisible
        by the multiband factor.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    Returns
    -------
    list[tuple[int, int]]
        A list of tuples containing the binned slice indices

    Example
    -------
    >>> from nifti2bids.metadata import _create_multiband_slice_groupings
    >>> slice_order = [0, 2, 4, 6, 8, 1, 3, 5, 7, 9] # interleaved order
    >>> _create_multiband_slice_groupings(slice_order, multiband_factor=2, step_size=5, ascending=True)
    >>> [(0, 5), (2, 7), (4, 9), (1, 6), (3, 8)]
    """
    n_real_slices = len(slice_order) - n_fake_slices
    slice_groupings = []
    for slice_idx in slice_order:
        if any(slice_idx in group for group in slice_groupings):
            continue

        sequence = _generate_sequence(slice_idx, multiband_factor, step_size, ascending)

        if max(sequence) >= n_real_slices or min(sequence) < 0:
            if n_fake_slices:
                sequence = [val for val in sequence if val < n_real_slices]
            else:
                continue

        # If list is empty due to sequence filtering from n_fake_slices case
        # then continue
        if not sequence:
            continue

        if sequence:
            slice_groupings.append(tuple(sequence))

    return slice_groupings


def _create_multiband_timing(
    tr: float | int,
    slice_order: list[int],
    n_fake_slices: int,
    multiband_factor: int,
    ascending: bool,
) -> list[float]:
    """
    Create multiband timing based on slice order.

    Parameters
    ----------
    tr: :obj:`float` or :obj:`int`
        Repetition time in seconds.

    slice_order: :obj:`list[int]`
        Order of the slices from single slice acquisition.

    n_fake_slices: :obj:`int`
        The number of fake slices added to make total slices divisible
        by the multiband factor.

    multiband_factor: :obj:`int`
        The multiband acceleration factor, which is the number of slices
        acquired simultaneously during multislice acquisition.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    Returns
    -------
    list[float]
        Ordered slice timing information for multiband acquisition.

    Example
    -------
    >>> from nifti2bids.metadata import _create_mutiband_timing
    >>> slice_order = [0, 2, 4, 6, 8, 1, 3, 5, 7, 9] # interleaved order
    >>> _create_mutiband_timing(0.8, slice_order, multiband_factor=2, ascending=True)
    >>> [0.0, 0.48, 0.16, 0.64, 0.32, 0.0, 0.48, 0.16, 0.64, 0.32]
    >>> # Note step size in groupings = n_slices / multiband_factor (10 / 2)
    >>> # also corresponds to number of unique slice timings
    >>> # slices grouping: [[0, 5], [2, 7], [4, 9], [1, 6], [3, 8]]
    """
    n_slices = len(slice_order)

    # Number of time steps (also serves as the step size for slice grouping)
    n_time_steps = n_slices // multiband_factor
    slice_duration = tr / n_time_steps
    unique_slice_timings = np.linspace(0, tr - slice_duration, n_time_steps)
    slice_timing = np.zeros((n_slices - n_fake_slices))

    slice_groupings = _create_multiband_slice_groupings(
        slice_order, multiband_factor, n_time_steps, n_fake_slices, ascending
    )

    for time_indx, multiband_group in enumerate(slice_groupings):
        slice_timing[list(multiband_group)] = unique_slice_timings[time_indx]

    return slice_timing.tolist()


def create_slice_timing(
    nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image,
    tr: Optional[float | int] = None,
    slice_axis: Optional[Literal["x", "y", "z"]] = None,
    acquisition: Literal["sequential", "interleaved"] = "interleaved",
    ascending: bool = True,
    interleaved_pattern: Literal["even", "odd", "philips"] = "odd",
    multiband_factor: Optional[int] = None,
) -> list[float]:
    """
    Create slice timing dictionary mapping the slice index to its
    acquisition time.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    tr: :obj:`float` or :obj:`int`
        Repetition time in seconds. If None, the repetition time is
        extracted from the NIfTI header.

    slice_axis: :obj:`Literal["x", "y", "z"]` or :obj:`None`, default=None
        Axis the image slices were collected in. If None,
        determines the slice axis using metadata ("slice_end")
        from the NIfTI header.

    acquisition :obj:`Literal["sequential", "interleaved"]`, default="interleaved"
        Method used for acquiring slices.

        .. note::
           "interleaved" is the common interleaving pattern (e.g [0, 2, 4, 6, 1, 3, 5, 7]),
           which is also equivalent to Philips' "default". The "interleaved_sqrt_step"
           is an method where slices are acquired by a step factor equivalent
           to the rounded square root of the total slices (this method is Philips' "interleaved"
           mode).

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    interleaved_pattern: :obj:`Literal["even", "odd", "philips"]`, default="odd"
        If slices for interleaved acquisition were collected by acquiring the
        "even" or "odd" slices first. For "philips" (the interleaved implementation
        by Philips'), slices are acquired by a step factor equivalent to the rounded
        square root of the total slices.
        mode).

        .. important::
           Philips' "default" mode is equivalent to "interleave" with the pattern
           set to "odd", and ascending set to True.

    multiband_factor: :obj:`int` or :obj:`None`, default == None
        The multiband acceleration factor, which is the number of slices
        acquired simultaneously during multislice acquisition. Slice
        ordering is created using a step factor equivalent to
        ``n_slices / multiband_factor``. For instance, if ``n_slices`` is
        12 and ``slice_acquisition_method`` is "interleaved" with
        ``multiband_factor`` of 3, then the traditional interleaved
        order using the "odd" first ascending pattern is [0, 2, 4, 6, 8, 10,
        1, 3, 5, 7, 9, 11]. This order is then grouped into sets of 3
        with a step of 4 (12 slices divided by multiband factor of 3),
        resulting in slice groups: (0, 4, 8), (2, 6, 10), (1, 5, 9), (3, 7, 11).
        The final slice timing order is [0, 4, 8, 2, 6, 10, 1, 5, 9, 3, 7, 11].

        .. important::
            - Multiband grouping is primarily based on based on
              Philip's ordering for multiband acquisition for different
              slice acquisition methods. For more information refer to the
              `University of Washington Diagnostic Imaging Sciences Center Technical Notes
              <https://depts.washington.edu/mrlab/technotes/fmri.shtml>`_.

            ** Indivisible Multiband Factor**:
            - When pattern is not set to "philips", then for cases where the number
              of slices is indivisible by the ``multiband_factor``, the total slice
              count is padded to the next highest integer evenly divisible
              by the factor. The slice ordering and groupings are generated based on
              this new count, and any non-existent "fake" slices are automatically filtered
              out from these groupings. For instance, if ``n_slices=10`` and ``multiband_factor=3``,
              then the slice order is based on ceil(10 / 3) = 4 -> ``n_slices = 4 * 3`` (12 slices).
              Then 4 timesteps are used to create the following slice order groupings:
              (0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11). Finally, the "fake" slices
              (10 and 11) are filtered out and the final slice order groupings are
              (0, 4, 8), (1, 5, 9), (2, 6), and (3, 7). This method is based on
              `GE's Slice Timing Info Guide
              <https://raw.githubusercontent.com/mr-jaemin/ge-mri/main/doc/GEHC_fMRI_Slice_Timing_Info.pdf>`_.

    Returns
    -------
    list[float]
        List containing the slice timing acquisition.

    Referenes
    ---------
    Parker, David, et al. "Optimal Slice Timing Correction and Its Interaction with
    FMRI Parameters and Artifacts." Medical Image Analysis, vol. 35, Jan. 2017, pp. 434–445,
    https://doi.org/10.1016/j.media.2016.08.006. Accessed 28 Jan. 2022.
    """
    slice_ordering_func = {
        "sequential": _create_sequential_order,
        "interleaved": _create_interleaved_order,
    }

    n_slices = get_n_slices(nifti_file_or_img, slice_axis)

    # Calculate fake slices needed for multiband only for even/odd pattern
    # GE implementation of indivisible multiband:
    # https://raw.githubusercontent.com/mr-jaemin/ge-mri/main/doc/GEHC_fMRI_Slice_Timing_Info.pdf
    n_fake_slices = 0
    if multiband_factor and n_slices % multiband_factor != 0:
        if acquisition == "interleaved" and interleaved_pattern == "philips":
            raise ValueError(
                f"For 'philips' interleave pattern with multiband, the number "
                f"of slices ({n_slices}) must be evenly divisible by the "
                f"multiband factor ({multiband_factor})."
            )

        LGR.warning(
            f"Number of slices ({n_slices}) is not divisible by the"
            f"multiband factor ({multiband_factor})"
        )

        n_timepoints = int(np.ceil(n_slices / multiband_factor))
        n_fake_slices = (n_timepoints * multiband_factor) - n_slices

    total_slices = n_slices + n_fake_slices
    acquisition_kwargs = {"n_slices": total_slices, "ascending": ascending}
    if acquisition == "interleaved":
        acquisition_kwargs.update({"interleaved_pattern": interleaved_pattern})

    slice_order = slice_ordering_func[acquisition](**acquisition_kwargs)
    tr = tr if tr else get_tr(nifti_file_or_img)
    band_kwargs = {"tr": tr, "slice_order": slice_order}

    return (
        _create_singleband_timing(**band_kwargs)
        if not multiband_factor
        else _create_multiband_timing(
            multiband_factor=multiband_factor,
            ascending=ascending,
            n_fake_slices=n_fake_slices,
            **band_kwargs,
        )
    )


def is_3d_img(nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image) -> bool:
    """
    Determines if ``nifti_file_or_img`` is a 3D image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    bool
        True if ``nifti_file_or_img`` is a 3D image.
    """
    return len(get_nifti_header(nifti_file_or_img).get_zooms()) == 3


def get_scanner_info(
    nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image,
) -> tuple[str, str]:
    """
    Determines the manufacturer and model name of scanner.

    .. important::
        Assumes this information is in the "descrip" of the NIfTI
        header, which can contain any information.


    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    tuple[str, str]
        The manufacturer and model name for the scanner.
    """
    if not (
        scanner_info := get_hdr_metadata(
            nifti_file_or_img=nifti_file_or_img,
            metadata_name="descrip",
            return_header=False,
        )
    ):
        raise ValueError("No scanner information in NIfTI header.")

    scanner_info = str(scanner_info.astype(str)).rstrip(" ")
    manufacturer_name, _, model_name = scanner_info.partition(" ")

    return manufacturer_name, model_name


def is_valid_date(date_str: str, date_fmt: str) -> bool:
    """
    Determine if a string is a valid date based on format.

    Parameters
    ----------
    date_str: :obj:`str`
        The string to be validated.

    date_fmt: :obj:`str`
        The expected format of the date.

    Return
    ------
    bool
        True if ``date_str`` has the format specified by ``date_fmt``.

    Example
    -------
    >>> from nifti2bids.metadata import is_valid_date
    >>> is_valid_date("241010", "%y%m%d")
        True
    """
    try:
        datetime.datetime.strptime(date_str, date_fmt)
        return True
    except ValueError:
        return False


def get_date_from_filename(filename: str | Path, date_fmt: str) -> str | None:
    """
    Get date from filename.

    Extracts the date from the name a file.

    Parameters
    ----------
    filename: :obj:`str` or :obj:`Path`
        The absolute path or name of file.

    date_fmt: :obj:`str`
        The expected format of the date.

    Returns
    -------
    str or None:
        A string if a valid date based on specified ``date_fmt`` is detected
        or None if no valid date is detected.

    Example
    -------
    >>> from nifti2bids.metadata import get_date_from_filename
    >>> get_date_from_filename("101_240820_mprage_32chan.nii", "%y%m%d")
        "240820"
    """
    split_pattern = "|".join(map(re.escape, ["_", "-", " "]))

    basename = Path(filename).name
    split_basename = re.split(split_pattern, basename)

    date_str = None
    for part in split_basename:
        if is_valid_date(part, date_fmt):
            date_str = part
            break

    return date_str


def get_entity_value(filename: str | Path, entity: str) -> str | None:
    """
    Gets entity value of a BIDS compliant filename.

    Parameters
    ----------
    filename: :obj:`str` or :obj:`Path`
        Filename to extract entity from.

    entity: :obj:`str`
        The entity key (e.g. "sub", "task")

    Returns
    -------
    str or None
        The entity value.

    Example
    -------
    >>> from nifti2bids.metadata import get_entity_value
    >>> get_entity_value("sub-01_task-flanker_bold.nii.gz", "task")
        "flanker"
    """
    basename = Path(filename).name
    match = re.search(rf"{entity}-([^_\.]+)", basename)

    return match.group(1) if match else None


def infer_task_from_image(
    nifti_file_or_img: str | Path | nib.nifti1.Nifti1Image,
    volume_to_task_map: dict[int, str],
) -> str:
    """
    Infer the task based on the number of volumes in a 4D NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str`, :obj:`Path`, or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    volume_to_task_map: :obj:`dict[int, str]`
        A mapping of the number of volumes for each taskname.

    Returns
    -------
    str
        The task name.

    Example
    -------
    >>> from nifti2bids.io import simulate_nifti_image
    >>> from nifti2bids.metadata import infer_task_from_image
    >>> img = simulate_nifti_image((100, 100, 100, 260))
    >>> volume_to_task_map = {300: "flanker", 260: "nback"}
    >>> infer_task_from_image(img, volume_to_task_map)
        "nback"
    """
    n_volumes = get_n_volumes(nifti_file_or_img)

    return volume_to_task_map.get(n_volumes)
