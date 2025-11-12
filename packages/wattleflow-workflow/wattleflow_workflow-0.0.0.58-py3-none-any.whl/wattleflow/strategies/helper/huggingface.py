# Module name: huggingface.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


import logging
import shutil
import sys

from pathlib import Path
from wattleflow.core import IStrategy

# from transformers.file_utils import TRANSFORMERS_CACHE


logger = logging.getLogger(str(Path(__file__).name))
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # - %(filename)s:%(lineno)d",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# TRANSFORMERS_CACHE


class StrategyCopyHuggingfaceModels(IStrategy):
    def file_size(self, path: str | Path) -> str:
        if isinstance(path, str):
            path = Path(path)

        if path.exists() is False:
            raise FileNotFoundError(str(path.absolute()))

        size = path.stat().st_size

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

        return "0 bytes"

    def execute(
        self,
        source_dir: str,
        destination_dir: str,
    ):
        source: Path = Path(source_dir)
        destination: Path = Path(destination_dir)

        logger.debug("source: %s", source)
        logger.debug("destination: %s", destination)

        if not source.exists() or not source.is_dir():
            msg = f"Source directory not found or not a directory: {source.resolve()}"
            logger.error(msg, stack_info=True)
            raise FileNotFoundError(msg)

        destination.mkdir(parents=True, exist_ok=True)
        count = 0
        for path in source.rglob("*"):  # nema "**/*"; rglob je već rekurzivan
            if path.is_dir():
                continue
            rel = path.relative_to(source)
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(path, target, follow_symlinks=True)
            logger.info("Copied %s -> %s", path, target)
            count += 1

        logger.info("Complete. [%s]", count)
