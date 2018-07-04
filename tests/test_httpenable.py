import os

from dtoolcore import DataSet

from . import tmp_uuid_and_uri  # NOQA
from . import TEST_SAMPLE_DATA


def test_http_manifest():

    uri = "s3://test-dtool-s3-bucket/04c4e3a4-f072-4fc1-881a-602d589b089a"

    dataset = DataSet.from_uri(uri)

    http_manifest = dataset._storage_broker.generate_http_manifest()

    assert "admin_metadata" in http_manifest
    assert http_manifest["admin_metadata"] == dataset._admin_metadata

    assert "overlays" in http_manifest
    assert "readme_url" in http_manifest
    assert "manifest_url" in http_manifest

    # Check item urls
    assert "item_urls" in http_manifest
    assert set(http_manifest["item_urls"].keys()) == set(dataset.identifiers)

    dataset._storage_broker.write_http_manifest(http_manifest)


def test_http_enable(tmp_uuid_and_uri):  # NOQA

    uuid, dest_uri = tmp_uuid_and_uri

    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore import DataSet

    name = "my_dataset"
    admin_metadata = generate_admin_metadata(name)
    admin_metadata["uuid"] = uuid

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)
    local_file_path = os.path.join(sample_data_path, 'tiny.png')

    # Create a minimal dataset
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config_path=None)
    proto_dataset.create()
    proto_dataset.put_item(local_file_path, 'tiny.png')
    proto_dataset.put_readme("---\nproject: testing\n")
    proto_dataset.freeze()

    dataset = DataSet.from_uri(dest_uri)

    access_url = dataset._storage_broker.http_enable()

    assert access_url.startswith("https://")
