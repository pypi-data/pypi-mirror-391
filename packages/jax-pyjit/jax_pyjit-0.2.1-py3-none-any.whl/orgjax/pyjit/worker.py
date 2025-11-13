import os
from multiprocessing import Process


from . import shared_config

from temporalio.client import Client

from jax.cs.storage import StorageObject
from .dao import StorageKey


from pathlib import Path


class WorkerManager:

    def __init__(self, start_workflow_worker, start_activity_worker) -> None:
        """
        Initialize the Worker with two functions: start_workflow_worker and start_activity_worker.
        Both arguments must be callable.
        """
        if not callable(start_workflow_worker):
            raise TypeError("start_workflow_worker must be a function")
        if not callable(start_activity_worker):
            raise TypeError("start_activity_worker must be a function")
        self.start_workflow_worker = start_workflow_worker
        self.start_activity_worker = start_activity_worker

    def run(self):
        """
        Run the worker processes for workflow and activity workers.
        Checks the sample data bucket and starts two separate processes for workflow and activity workers.
        """
        bname: str = shared_config.TEST_BUCKET_NAME
        if bname:
            self.testSampleDataBucket(bname)

        # One wrinkle in this is that we must to run two processes.
        # Since we signal between the workflow and activities we must
        # not use the same python process for both because of the GIL.
        # This is despite the use of asyncio.
        print("Starting worker on '{}'".format(shared_config.TEMPORAL_URI))
        print("Temporal namespace '{}'".format(shared_config.TEMPORAL_NAMESPACE))

        pw = Process(target=self.start_workflow_worker)
        pa = Process(target=self.start_activity_worker)
        pw.start()
        pa.start()
        pw.join()
        pa.join()

    def testSampleDataBucket(self, bucket: str):
        """
        Test access to the sample data bucket by downloading a file and verifying local storage.
        """
        key: StorageKey = StorageKey(bucket, "/")

        if shared_config.USE_NIO_STORAGE:
            # Check local storage system is working
            uri: str = key.to_uri()
            uri = _hack_uri(uri)

            # We still check path, it may be GCS or S3 or local file
            print("Checking sample data: {}".format(uri))
            wrapped = StorageObject(uri)

            dir: Path = get_dir("test")
            file: Path = Path(dir, Path(uri).name)
            os.makedirs(file.parent, exist_ok=True)
            file.touch()

            with open(file, "wb") as test_file:
                data = wrapped.download_as_bytes()
                test_file.write(data)

            print("Download to: {}".format(file))
            os.remove(file)

        else:
            # TODO same for GCS and S3 ideally.
            pass


def _hack_uri(uri: str) -> str:
    """
    Hack the uri to be a local file system.
    This is only for testing purposes.
    """
    # If it's a directory, we need to give a file to StorageObject
    # with jax-cs-storage v<=0.9.3
    try:
        if os.path.isdir(uri):
            for file in os.listdir(uri):
                if file.endswith(".ndpi") and os.path.isfile(os.path.join(uri, file)):
                    uri = os.path.join(uri, file)
                    return uri

    except FileNotFoundError:
        print(f"Directory '{uri}' not found.")

    return None


def get_dir(run_id: str) -> Path:

    cache: Path = Path(shared_config.CACHE_DIR)
    dir: Path = Path(cache, run_id)
    # Make dirs if not existing
    os.makedirs(dir, exist_ok=True)
    return dir


async def connect_client() -> Client:
    """Connect the client."""
    client = await Client.connect(
        shared_config.TEMPORAL_URI, namespace=shared_config.TEMPORAL_NAMESPACE
    )
    return client
