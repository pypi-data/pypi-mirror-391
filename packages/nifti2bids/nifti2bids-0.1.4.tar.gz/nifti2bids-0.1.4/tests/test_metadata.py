import nibabel as nib, numpy as np, pytest
import nifti2bids.metadata as bids_meta


@pytest.mark.parametrize("return_header", (False, True))
def test_get_hdr_metadata(nifti_img_and_path, return_header):
    """Test for ``get_hdr_metadata``."""
    img, _ = nifti_img_and_path
    img.header["slice_end"] = 100

    if return_header:
        slice_end, hdr = bids_meta.get_hdr_metadata(
            metadata_name="slice_end",
            nifti_file_or_img=img,
            return_header=return_header,
        )
        assert isinstance(hdr, nib.nifti1.Nifti1Header)
    else:
        slice_end = bids_meta.get_hdr_metadata(
            metadata_name="slice_end",
            nifti_file_or_img=img,
            return_header=return_header,
        )

    assert slice_end == 100


def test_determine_slice_axis(nifti_img_and_path):
    """Test for ``determine_slice_axis``."""
    img, _ = nifti_img_and_path

    with pytest.raises(ValueError):
        bids_meta.determine_slice_axis(img)

    # Subtract one to convert to index
    img.header["slice_end"] = img.get_fdata().shape[2] - 1
    assert bids_meta.determine_slice_axis(img) == 2


def test_get_n_volumes(nifti_img_and_path):
    """Test for ``get_n_volumes``."""
    img, _ = nifti_img_and_path
    assert bids_meta.get_n_volumes(img) == 5

    from nifti2bids.simulate import simulate_nifti_image
    from nifti2bids._exceptions import DataDimensionError

    with pytest.raises(DataDimensionError):
        bids_meta.get_n_volumes(simulate_nifti_image((10, 10, 10)))


def test_get_n_slices(nifti_img_and_path):
    """Test for ``get_n_slices``."""
    from nifti2bids._exceptions import SliceAxisError

    img, _ = nifti_img_and_path
    # Subtract one to convert to index
    img.header["slice_end"] = img.get_fdata().shape[2] - 1

    with pytest.raises(SliceAxisError):
        bids_meta.get_n_slices(img, slice_axis="x")

    assert bids_meta.get_n_slices(img, slice_axis="z") == img.header["slice_end"] + 1
    assert bids_meta.get_n_slices(img) == img.header["slice_end"] + 1


def test_get_tr(nifti_img_and_path):
    """Test for ``get_tr``."""
    img, _ = nifti_img_and_path
    img.header["pixdim"][4] = 2.3
    assert bids_meta.get_tr(img) == 2.3
    assert not isinstance(bids_meta.get_tr(img), np.floating)
    assert not isinstance(bids_meta.get_tr(img), np.integer)

    img.header["pixdim"][4] = 0
    with pytest.raises(ValueError):
        bids_meta.get_tr(img)


@pytest.mark.parametrize("acquisition", ("sequential", "interleaved"))
def test_create_slice_timing_singleband(acquisition):
    """Test for ``create_slice_timing`` for singleband acquisition."""
    from nifti2bids.simulate import simulate_nifti_image

    img = simulate_nifti_image((10, 10, 4, 10))
    img.header["pixdim"][4] = 2
    img.header["slice_end"] = 3

    if acquisition == "sequential":
        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
        )
        assert slice_timing_list == [0, 0.5, 1, 1.5]

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
        )
        assert slice_timing_list == [1.5, 1, 0.5, 0]
    else:
        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="odd",
        )
        assert slice_timing_list == [0, 1, 0.5, 1.5]

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
            interleaved_pattern="odd",
        )
        assert slice_timing_list == [1.5, 0.5, 1, 0]

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="even",
        )
        assert slice_timing_list == [1, 0, 1.5, 0.5]

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
            interleaved_pattern="even",
        )
        assert slice_timing_list == [0.5, 1.5, 0, 1]

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="philips",
        )
        assert slice_timing_list == [0, 1, 0.5, 1.5]

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
            interleaved_pattern="philips",
        )
        assert slice_timing_list == [1.5, 0.5, 1, 0]

        with pytest.raises(ValueError):
            slice_timing_list = bids_meta.create_slice_timing(
                nifti_file_or_img=img,
                acquisition=acquisition,
                ascending=False,
                interleaved_pattern="incorrect_value",
            )


@pytest.mark.parametrize("acquisition", ("sequential", "interleaved"))
def test_create_slice_timing_multiband(acquisition):
    """Test for ``create_slice_timing`` for multiband acquisition."""
    from nifti2bids.simulate import simulate_nifti_image

    img = simulate_nifti_image((12, 12, 10, 12))
    img.header["pixdim"][4] = 2
    img.header["slice_end"] = 9

    if acquisition == "sequential":
        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [0.0, 0.4, 0.8, 1.2, 1.6, 0.0, 0.4, 0.8, 1.2, 1.6]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [1.6, 1.2, 0.8, 0.4, 0.0, 1.6, 1.2, 0.8, 0.4, 0.0]
        )
    else:
        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="odd",
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [0.0, 1.2, 0.4, 1.6, 0.8, 0.0, 1.2, 0.4, 1.6, 0.8]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            interleaved_pattern="odd",
            ascending=False,
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [0.8, 1.6, 0.4, 1.2, 0.0, 0.8, 1.6, 0.4, 1.2, 0.0]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="even",
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [0.8, 0.0, 1.2, 0.4, 1.6, 0.8, 0.0, 1.2, 0.4, 1.6]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            interleaved_pattern="even",
            ascending=False,
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [1.6, 0.4, 1.2, 0.0, 0.8, 1.6, 0.4, 1.2, 0.0, 0.8]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="philips",
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [0.0, 0.8, 1.6, 0.4, 1.2, 0.0, 0.8, 1.6, 0.4, 1.2]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
            interleaved_pattern="philips",
            multiband_factor=2,
        )
        assert np.allclose(
            slice_timing_list, [0.4, 1.6, 0.8, 0.0, 1.2, 0.4, 1.6, 0.8, 0.0, 1.2]
        )

        with pytest.raises(ValueError):
            slice_timing_list = bids_meta.create_slice_timing(
                nifti_file_or_img=img,
                acquisition=acquisition,
                interleaved_pattern="philips",
                multiband_factor=3,
            )


@pytest.mark.parametrize("acquisition", ("sequential", "interleaved"))
def test_create_slice_timing_multiband_indivisible(acquisition):
    """
    Test for ``create_slice_timing`` for multiband acquisition with
    indivisible multiband factor.
    """
    from nifti2bids.simulate import simulate_nifti_image

    img = simulate_nifti_image((12, 12, 10, 12))
    img.header["pixdim"][4] = 2
    img.header["slice_end"] = 9

    if acquisition == "sequential":
        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            multiband_factor=3,
        )
        # 4 time steps: [0.0, 0.5, 1.0, 1.5]
        # Groups : (0, 4, 8), (1, 5, 9), (2, 6), (3, 7)
        assert np.allclose(
            slice_timing_list, [0.0, 0.5, 1.0, 1.5, 0.0, 0.5, 1.0, 1.5, 0.0, 0.5]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=False,
            multiband_factor=3,
        )
        # Order: 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0
        # Groups: (7, 3), (6, 2), (9, 5, 1), (8, 4, 0)
        assert np.allclose(
            slice_timing_list, [1.5, 1.0, 0.5, 0.0, 1.5, 1.0, 0.5, 0.0, 1.5, 1.0]
        )
    else:
        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="odd",
            multiband_factor=3,
        )
        # Order: 0, 2, 4, 6, 8, 10, 1, 3, 5, 7, 9, 11
        # Groups: (0, 4, 8), (2, 6), (1, 5, 9), (3, 7)
        assert np.allclose(
            slice_timing_list, [0.0, 1.0, 0.5, 1.5, 0.0, 1.0, 0.5, 1.5, 0.0, 1.0]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            interleaved_pattern="odd",
            ascending=False,
            multiband_factor=3,
        )
        # Order: 11, 9, 7, 5, 3, 1, 10, 8, 6, 4, 2, 0
        # Groups: (7, 3), (9, 5, 1), (6, 2), (8, 4, 0)
        assert np.allclose(
            slice_timing_list, [1.5, 0.5, 1.0, 0.0, 1.5, 0.5, 1.0, 0.0, 1.5, 0.5]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            ascending=True,
            interleaved_pattern="even",
            multiband_factor=3,
        )
        # Order: 1, 3, 5, 7, 9, 11, 0, 2, 4, 6, 8, 10
        # Groups: (1, 5, 9), (3, 7), (0, 4, 8), (2, 6)
        assert np.allclose(
            slice_timing_list, [1.0, 0.0, 1.5, 0.5, 1.0, 0.0, 1.5, 0.5, 1.0, 0.0]
        )

        slice_timing_list = bids_meta.create_slice_timing(
            nifti_file_or_img=img,
            acquisition=acquisition,
            interleaved_pattern="even",
            ascending=False,
            multiband_factor=3,
        )
        # Order: 10, 8, 6, 4, 2, 0, 11, 9, 7, 5, 3, 1
        # Groups: (6, 2), (8, 4, 0), (7, 3), (9, 5, 1)
        assert np.allclose(
            slice_timing_list, [0.5, 1.5, 0.0, 1.0, 0.5, 1.5, 0.0, 1.0, 0.5, 1.5]
        )


def test_is_3d_img(nifti_img_and_path):
    """Test for ``is_3d_img``."""
    from nifti2bids.simulate import simulate_nifti_image

    img = simulate_nifti_image((10, 10, 10))
    assert bids_meta.is_3d_img(img)

    img, _ = nifti_img_and_path
    assert not bids_meta.is_3d_img(img)


def test_get_scanner_info(nifti_img_and_path):
    """Test for ``get_scanner_info``."""
    img, _ = nifti_img_and_path
    with pytest.raises(ValueError):
        bids_meta.get_scanner_info(img)

    img.header["descrip"] = "Philips Ingenia Elition X 5.7.1"
    manufacturer_name, model_name = bids_meta.get_scanner_info(img)
    assert manufacturer_name == "Philips"
    assert model_name == "Ingenia Elition X 5.7.1"


def test_get_date_from_filename():
    """Test for ``get_date_from_filename``."""
    date = bids_meta.get_date_from_filename("101_240820_mprage_32chan.nii", "%y%m%d")
    assert date == "240820"

    date = bids_meta.get_date_from_filename("101_mprage_32chan.nii", "%y%m%d")
    assert not date


def test_get_entity_value():
    """Test for ``get_entity_value``."""
    filename = "sub-01_task-test_bold.nii.gz"
    assert bids_meta.get_entity_value(filename, "task") == "test"
    assert not bids_meta.get_entity_value(filename, "ses")


def test_infer_task_from_image(nifti_img_and_path):
    """Test for ``infer_task_from_image``."""
    img, _ = nifti_img_and_path

    volume_to_task_map = {5: "flanker", 10: "nback"}

    assert bids_meta.infer_task_from_image(img, volume_to_task_map) == "flanker"
