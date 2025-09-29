from repository import Repository

from db.data.adb_hub import AdbHub
from meta.exceptions import AdbHubNotFound, AdbHubAlreadyExists


class AdbHubManager:
    """
        All functions to get/add/update adb hub info in database.
        Must-have layer between core/main program and repository.
    """

    def __init__(self) -> None:
        self.repository = Repository()

    def exists(self, hubUUID: str) -> bool:
        return bool(
            self.repository.read(AdbHub, hubUUID)
        )

    def _require(self, hubUUID: str) -> None:
        if not self.exists(hubUUID):
            raise AdbHubNotFound(f"Adb hub {hubUUID} not found.")

    def get(self, hubUUID: str) -> AdbHub:
        self._require(hubUUID)
        return self.repository.read(AdbHub, hubUUID)

    def getAll(self) -> list[AdbHub]:
        return self.repository.readAll(AdbHub)

    def add(self, hubUUID: str, hubApiLink: str) -> None:
        # check if record is already in DB
        if self.exists(hubUUID):
            raise AdbHubAlreadyExists(f"Adb hub {hubUUID} already exists")

        self.repository.create(
            AdbHub(id=hubUUID, apiLink=hubApiLink)
        )


    def delete(self, hubUUID: str) -> None:
        self.v(hubUUID)
        self.repository.delete(AdbHub, hubUUID)


    def update(self, hubUUID: str, hubApiLink: str) -> None:
        self._require(hubUUID)
        self.repository.update( AdbHub, hubUUID, apiLink=hubApiLink )
