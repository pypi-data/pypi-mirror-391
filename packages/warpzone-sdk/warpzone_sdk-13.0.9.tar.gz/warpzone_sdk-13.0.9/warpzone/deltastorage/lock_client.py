import datetime as dt
import os
from contextlib import contextmanager

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobClient, BlobLeaseClient

import warpzone as wz

logger = wz.get_logger(__name__)
LEASE_DURATION = 60  # seconds
CONTAINER_NAME = "locks"


class LockClient:
    def __init__(self, wz_blob_client: wz.WarpzoneBlobClient):
        self.wz_blob_client = wz_blob_client
        self.blob_lock_clients: list[BlobLockClient] = []

    @classmethod
    def from_func_env_variables(cls):
        data_store_name = os.environ["OPERATIONAL_DATA_STORAGE_ACCOUNT"]
        wz_blob_client = wz.WarpzoneBlobClient.from_resource_name(data_store_name)
        return cls(wz_blob_client)

    def create_blob_lock_clients(self, lock_names: list[str]) -> None:
        """Create BlobLockClients for each lock name, based on the WarpzoneBlobClient.
        This sets the blob_lock_clients attribute of the LockClient instance,
        as a list of BlobLockClients.

        Args:
            lock_names (list[str]): Names of the locks to create BlobLeaseClients for.
        """
        blob_lock_clients: list[BlobLockClient] = []
        for name in lock_names:
            blob_client = self.wz_blob_client._blob_service_client.get_blob_client(
                CONTAINER_NAME, name
            )
            blob_lock_client = BlobLockClient(blob_client)
            blob_lock_client.create_blob_if_not_exist()

            blob_lock_clients.append(blob_lock_client)

        self.blob_lock_clients = blob_lock_clients

    def break_expired_locks(self):
        """Break leases that have expired for all BlobLockClients
        in the blob_lock_clients attribute.
        """
        for blob_lock_client in self.blob_lock_clients:
            if blob_lock_client.is_expired():
                blob_lock_client.break_lock()

    @contextmanager
    def lock(self, lock_names: list[str]):
        """Context manager to acquire and release leases for given lock names.
        Args:
            lock_names (list[str]): Names of the locks to acquire locks for.

        Yields:
            LockClient: The LockClient instance with acquired locks.
        """
        self.create_blob_lock_clients(lock_names)
        self.break_expired_locks()

        try:
            self.acquire_locks()
            yield self
        finally:
            self.release_locks()

    def acquire_locks(self) -> bool:
        """Try to acquire leases for all BlobLeaseClients
        in the lease_clients attribute.
        """
        for blob_lock_client in self.blob_lock_clients:
            blob_lock_client.acquire_lock()

    def release_locks(self):
        """Try to release all leases held by the BlobLeaseClients
        in the lease_clients attribute.
        """
        for blob_lock_client in self.blob_lock_clients:
            blob_lock_client.release_lock()


class BlobLockClient:
    """Combine BlobClient and BlobLeaseClient to implement locking functionality."""

    LOCK_DURATION_SECONDS = (
        10 * 60
    )  # Seconds. Needs to match function timeout settings.
    LOCKED_TIME_UTC_COLUMN_NAME = "locked_time_utc"

    # _LEASE_DURATION is used to specify infinite lease duration for BlobLeaseClient
    _INFINITE_LEASE_DURATION = -1

    def __init__(self, blob_client: BlobClient):
        self.blob_client = blob_client
        self.lease_client = BlobLeaseClient(self.blob_client)

    def get_lock_id(self) -> str:
        """Get the lease ID held by the BlobLeaseClient."""
        return getattr(self.lease_client, "id", None)

    def is_expired(self) -> bool:
        """Check if the lease held by the BlobLeaseClient has expired.

        Returns:
            bool: True if the lease has expired,
            False if not expired, or if metadata does not yet exist.
        """
        properties = self.blob_client.get_blob_properties()
        locked_time_str = properties.metadata.get(
            self.LOCKED_TIME_UTC_COLUMN_NAME, None
        )
        locked_time_utc = dt.datetime.fromisoformat(locked_time_str)
        lease_duration = self.LOCK_DURATION_SECONDS
        expiration_time_utc = locked_time_utc + dt.timedelta(seconds=lease_duration)
        return dt.datetime.now(dt.timezone.utc) > expiration_time_utc

    def create_blob_if_not_exist(self) -> None:
        """Create blobs if they do not exist and add metadata:
        Set `locked_time_utc` to 1999-01-01, such that the lock will be expired.
        The blob does not contain any data, but the name is used for handling locks.
        """
        if not self.blob_client.exists():
            self.blob_client.upload_blob(
                b"",
                overwrite=True,
                metadata={
                    self.LOCKED_TIME_UTC_COLUMN_NAME: dt.datetime(
                        1999, 1, 1, tzinfo=dt.timezone.utc
                    ).isoformat()
                },
            )

    def acquire_lock(self) -> bool:
        """Try to acquire lease for the BlobLeaseClient.

        Returns:
            bool: True if lease was acquired successfully, False otherwise.

        Raises:
            Exception: If lease acquisition fails.
        """
        self.lease_client.acquire(lease_duration=self._INFINITE_LEASE_DURATION)
        logger.info(f"Lease acquired: {self.get_lock_id()}")
        self.blob_client.set_blob_metadata(
            {
                self.LOCKED_TIME_UTC_COLUMN_NAME: dt.datetime.now(
                    dt.timezone.utc
                ).isoformat()
            },
            lease=self.lease_client,
        )

    def release_lock(self):
        """Try to release lease held by the BlobLeaseClient.
        Log errors if release fails.
        """
        try:
            self.lease_client.release()
            logger.info(f"Lease released: {self.get_lock_id()}")
        except ResourceExistsError:
            pass  # Someone else has already acquired the lease

    def break_lock(self):
        """Break the lease held by the BlobLeaseClient.
        Log errors if breaking fails.
        """
        try:
            self.lease_client.break_lease()
            logger.info(f"Lease broken: {self.get_lock_id()}")
        except ResourceExistsError:
            pass  # Lease is already available
