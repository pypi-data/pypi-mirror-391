# Module name: filecontent_processor.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Generator
from wattleflow.core import ITarget
from wattleflow.concrete import GenericProcessor
from wattleflow.constants import Event
from wattleflow.drivers import DriverNotFound, LocalFileSystemDriver


class FileContentProcessor(GenericProcessor):
    @abstractmethod
    def get_file_content(self, filename: Path) -> object:
        pass

    def create_generator(self) -> Generator[ITarget, None, None]:
        self.debug(
            msg=Event.Iterating.value,
            step=Event.Started.value,
        )
        pattern = getattr(self, "pattern", None)
        if pattern is None:
            raise AttributeError(f"Missing 'pattern' attribute in {self.name}.")

        repository_path = getattr(self, "repository_path", None)
        if repository_path is None:
            raise AttributeError(f"Missing 'repository_path' attribute in {self.name}.")

        case_sensitive = getattr(self, "case_sensitive", False)
        recursive = getattr(self, "recursive", False)
        exclude_list = getattr(self, "exclude", [])

        driver: LocalFileSystemDriver = (
            self.driver
            if getattr(self, "driver", None)
            else LocalFileSystemDriver(
                repository_path=repository_path,
                level=self._level,
                handler=self._handler,
                create=False,
                normalised=False,
            )
        )

        if driver is None:
            raise DriverNotFound(self, f"No valid driver assigned for {self.name}.")

        for filename in driver.search(
            pattern=pattern, case_sensitive=case_sensitive, recursive=recursive
        ):
            self.info(msg=Event.Iterating.value, filename=str(filename))
            if filename.name in exclude_list:
                self.warning(
                    msg=Event.Generating.value,
                    error=f"Excluded file: {filename}.",
                )
                continue
            try:
                self.debug(
                    msg=Event.Iterating.value,
                    step=Event.Processing.value,
                    filename=str(filename),
                )

                yield self.blackboard.create(
                    caller=self,
                    filename=str(filename.absolute()),
                    content=self.get_file_content(filename=filename),
                )
            except Exception as e:
                self.error(
                    msg=Event.Iterating.value,
                    error=str(e),
                    filename=str(filename.absolute()),
                )
                raise

        self.debug(
            msg=Event.Iterating.value,
            step=Event.Completed.value,
        )
