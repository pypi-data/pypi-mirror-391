# Module name: tesseract.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


from __future__ import annotations
import os
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Generator
from wattleflow.core import ITarget
from wattleflow.concrete import GenericProcessor
from wattleflow.constants import Event
from wattleflow.constants.errors import ERROR_PATH_NOT_FOUND
from wattleflow.helpers import Attribute, TextStream


# --------------------------------------------------------------------------- #
# IMPORTANT:
# This test case requires the pytesseract library.
# Ensure you have it installed using:
#
#       pip install pytesseract
#
# --------------------------------------------------------------------------- #


class ImageToTextProcessor(GenericProcessor):
    def create_iterator(self) -> Generator[ITarget, None, None]:
        self.debug(
            msg=Event.Iterating.value,
            step=Event.Started.value,
        )

        Attribute.evaluate(caller=self, target=self.pattern, expected_type=str)
        Attribute.evaluate(caller=self, target=self.search_path, expected_type=str)
        Attribute.evaluate(caller=self, target=self.case_sensitive, expected_type=bool)
        Attribute.evaluate(caller=self, target=self.recursive, expected_type=bool)

        search_path = Path(self.search_path)
        if search_path.exists() is False:
            raise FileNotFoundError(ERROR_PATH_NOT_FOUND % str(search_path))

        kwargs = {
            "pattern": "**/*" if not self.pattern else self.pattern,
            "case_sensitive": self.case_sensitive,
            "recurse_symlinks": self.recursive,
        }

        file_iterator = (
            search_path.rglob(**kwargs)
            if self.recursive
            else search_path.glob(**kwargs)
        )

        for filename in file_iterator:
            self.debug(msg=Event.Iterating.value, filename=str(filename))
            try:
                if os.access(filename, os.R_OK) and os.stat(filename).st_size > 0:
                    image = Image.open(str(filename.absolute()))
                    content = TextStream(
                        pytesseract.image_to_string(image),
                        macros=self.macros,
                    )

                    yield self.blackboard.create(
                        caller=self,
                        filename=str(filename.absolute()),
                        content=content,
                    )

                else:
                    self.warning(
                        msg="File not accessible",
                        filename=str(filename.absolute()),
                    )
            except Exception as e:
                self.critical(msg=str(e))
                raise
            finally:
                self.debug(
                    msg=Event.Iterating.value,
                    step=Event.Completed.value,
                )
