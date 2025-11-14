import json
import os
from os import PathLike
from pathlib import Path

from fsspec import AbstractFileSystem
from tdm import TalismanDocument, TalismanDocumentModel

from tie_datamodel.dataset import SplitTdmData
from tp_interfaces.abstract.dataset import AbstractDatasetManager

README_FILE_NAME = "README.md"
FILES_NAME = "files.json"
DOCUMENTS_NAME = "documents"
VERSIONS_NAME = "versions"
SPLITS_NAME = "splits"


class VersionedTdmDataset(AbstractDatasetManager[TalismanDocument]):
    """
    some-dataset
    ├── documents
    │   ├── f1  # first 2 chars of document uuid
    │   │   ├── f100745d-9412-4765-839a-b67cc7a65d67 # document uuid
    │   │   │  ├──001.json # 1st document version
    │   │   │  └──002.json # 2nd document version
    │   │   ├── ...
    │   │   │
    │   │   └── f100745d-9412-4765-839a-b67cc7a65d66
    │   │      ├──001.json
    │   │      └──002.json
    │   │   ...
    │   └── 00
    │       └── 001d8b03-20cd-497d-9956-b54086288ea7
    │
    └── versions
        └──some_version
            ├── files.json # list of json file names (subset of documents directory)
            ├── README.md  # description of the dataset version
            └── splits
                └── some_split.json
    """

    def __init__(self, path: str | PathLike, version: str | None = None, file_system: AbstractFileSystem | None = None):
        super().__init__(file_system=file_system, path=path)
        self._documents_path = self._path / DOCUMENTS_NAME
        self._version_path = None if version is None else self._path / VERSIONS_NAME / version
        self._description_path = None if self._version_path is None else self._version_path / README_FILE_NAME
        self._version = version

        if self._description_path and self._fs.exists(self._description_path):
            with self._fs.open(self._description_path, "r", encoding="utf-8") as readme_f:
                self._description = readme_f.read()
        else:
            self._description: str = ""

        self._documents = self._get_docs()

    def _get_docs(self) -> dict[str, TalismanDocument]:
        if self._version_path is None or not self._fs.exists(self._version_path):
            return {}

        with self._fs.open(self._version_path / FILES_NAME, "r", encoding="utf-8") as documents_f:
            files_dict = json.load(documents_f)
        # check that documents do not repeat
        assert len(files_dict[DOCUMENTS_NAME]) == len({f_path.split(os.sep)[1] for f_path in files_dict[DOCUMENTS_NAME]})

        documents = {}
        for file_path in files_dict[DOCUMENTS_NAME]:
            full_file_path = self._documents_path / file_path
            if not self._fs.isfile(full_file_path):
                raise ValueError(f"Wrong file path `{full_file_path}`")
            with self._fs.open(full_file_path, "r", encoding="utf-8") as tdm_file:
                document = TalismanDocumentModel.model_validate(json.load(tdm_file)).deserialize()
            documents[document.id] = document
        return documents

    def set_description(self, description: str) -> None:
        self._description = description

    def add(self, element: TalismanDocument) -> None:
        self._documents[element.id] = element

    def remove(self, element: TalismanDocument) -> None:
        self._documents.pop(element.id, None)

    def save(self, version: str | None = None, exist_ok: bool = False) -> None:
        version = self._version if version is None else version
        if version is None:
            raise ValueError("Version is not set")

        new_version_path = self._path / VERSIONS_NAME / version
        if self._fs.exists(new_version_path) and not exist_ok:
            raise ValueError(f"Version {version} already exists")

        self._fs.makedirs(self._documents_path, exist_ok=True)
        self._fs.makedirs(new_version_path, exist_ok=True)

        readme_file_path = new_version_path / README_FILE_NAME
        with self._fs.open(readme_file_path, "w", encoding="utf-8") as readme_file:
            readme_file.write(self._description)

        files_dict = {DOCUMENTS_NAME: []}
        # TODO TALIE-1320 do not duplicate docs
        for doc in self._documents.values():
            doc_dir = Path(doc.id[:2]) / doc.id
            doc_name = self._get_doc_name(doc_dir)
            self._fs.makedirs(self._documents_path / doc_dir, exist_ok=True)
            serialized = TalismanDocumentModel.serialize(document=doc).model_dump(exclude_none=True)
            with self._fs.open(self._documents_path / doc_dir / doc_name, "w", encoding="utf-8") as doc_file:
                json.dump(serialized, doc_file, sort_keys=True, ensure_ascii=False)
            files_dict[DOCUMENTS_NAME].append(str(doc_dir / doc_name))

        documents_file_path = new_version_path / FILES_NAME
        with self._fs.open(documents_file_path, "w", encoding="utf-8") as documents_file:
            json.dump(files_dict, documents_file)

    def get_dataset(self) -> SplitTdmData:
        # TODO: use split files to make train/test/val split
        return SplitTdmData({None: self._documents.values()})

    def _get_doc_name(self, doc_dir: PathLike) -> str:
        if not self._fs.exists(self._documents_path / doc_dir):
            doc_num = 1
        else:
            doc_num = max([
                int(Path(doc_name).stem) for doc_name in self._fs.ls(self._documents_path / doc_dir)
            ], default=0) + 1
        return f"{doc_num:03d}.json"
