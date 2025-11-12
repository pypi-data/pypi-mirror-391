# Module name: youtube.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


from __future__ import annotations
import os
import logging
import pandas as pd
import tempfile as tmp
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import Optional
from wattleflow.core import IPipeline, IProcessor, IRepository, ITarget, IWattleflow
from wattleflow.concrete import (
    AuditLogger,
    DocumentFacade,
    GenericBlackboard,
    GenericRepository,
    GenericPipeline,
    StrategyCreate,
    StrategyRead,
    StrategyWrite,
)
from wattleflow.constants import Event
from wattleflow.documents import DataFrameDocument
from wattleflow.drivers.local_file_system_driver import FileTypes, LocalFileSystemDriver
from wattleflow.helpers import Attribute, TextFileStream
from wattleflow.helpers.normaliser import CaseText
from wattleflow.processors.youtube import YoutubeProcessor


# Strategies ------------------------------------------------------------------
class RepositoryReadDocument(StrategyRead):
    def get_filepath(self, storage_path: str, name: str, ext: str) -> str:
        name_pattern = "{path}{sep}{name:lower}.{ext:lower}"
        return name_pattern.format(
            path=CaseText(storage_path),
            sep=os.path.sep,
            name=CaseText(name),
            ext=CaseText(ext),
        )

    def execute(
        self, caller: IRepository, facade: ITarget, **kwargs
    ) -> Optional[ITarget]:
        self.debug(
            msg=Event.ProcessingTask.value,
            facade=facade,
            caller=caller.name,
            kwargs=kwargs,
        )

        return facade
        document = facade.reques()
        repository_path = getattr(caller, "repository_path", "")
        filename = getattr(document, "filename", "")
        file_path = self.get_filepath(repository_path, filename, "csv")
        self.debug(f"repository_path: {repository_path}, file_path: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        content: pd.DataFrame = pd.read_csv(file_path)
        self.debug(msg=f"columns: {content.columns}")
        # content["text"] = content["text"].apply(lambda s: s.replace("\n", " "))

        document = DocumentFacade(DataFrameDocument(document))
        document.update_content(content)

        self.info(
            msg=Event.Created.value,
            id=document.identifier,
            size=len(content),
        )

        return document

class CreateDataframeDocument(StrategyCreate):
    def execute(self, processor, *args, **kwargs) -> ITarget:
        Attribute.evaluate(caller=self, target=processor, expected_type=IProcessor)
        Attribute.mandatory(caller=self, name="filename", cls=str, **kwargs)
        Attribute.mandatory(caller=self, name="content", cls=list, **kwargs)

        self.debug(
            msg=Event.Creating.value,
            filename=self.filename,  # type: ignore
            size=len(self.content),  # type: ignore
        )

        document = DataFrameDocument(
            content=pd.DataFrame(self.document),  # type: ignore
            level=self._level,
            handler=self._handler,
        )

        self.info(
            msg=Event.Created.value,
            document=document,
            size=document.size,
        )

        return DocumentFacade(document)

class WriteDataFrameDocument(StrategyWrite):
    def get_filepath(self, storage_path: str, name: str, ext: str) -> str:
        name_pattern = "{path}{sep}{name:lower}.{ext:lower}"
        return name_pattern.format(
            path=CaseText(storage_path),
            sep=os.path.sep,
            name=CaseText(name),
            ext=CaseText(ext),
        )

    def execute(self, caller: IWattleflow, facade: ITarget, *args, **kwargs) -> bool:
    
        Attribute.evaluate(self, caller, IPipeline)
        Attribute.mandatory(self, "repository", GenericRepository, **kwargs)

        subdir = caller.name.lower()
        document = facade.request()
        filename = getattr(document, "filename", document.identifier)  # type: ignore

        self.debug(
            msg=Event.ProcessingTask.value,
            document=document,
            subdir=subdir,
            filename=filename,
        )

        if not document.size > 0:  # type: ignore
            self.warning(
                msg=Event.ProcessingTask.value,
                document=document,
                size=document.size,  # type: ignore
            )
            return False

        write_kwargs = kwargs.get("write_kwargs", {})
        output = self.repository.driver.write(  # type: ignore
            filename="",
            ftype=FileTypes.DATAFRAME,
            data=document.content,  # type: ignore
            **write_kwargs,
        )

        self.debug(
            msg=Event.TaskCompleted.value,
            document=document,
            output=output,
        )

        return True

# Pipelines -------------------------------------------------------------------
class DataFrameCleanupPipeline(GenericPipeline):
    def process(
        self,
        processor: IProcessor,
        facade: ITarget,
        *args,
        **kwargs,
    ) -> None:
        super().process(processor=processor, facade=facade, *args, **kwargs)

        document = facade.request()  # type: ignore
        Attribute.evaluate(caller=self, target=document.content, expected_type=pd.DataFrame)  # type: ignore

        if not document.size > 0:  # type: ignore
            self.warning(
                msg="Dataframe is feeling a bit empty today.",
                document=document,
                size=document.size,  # type: ignore
            )
            return

        content = document.content.fillna("")  # type: ignore
        facade.update_content(content)  # type: ignore
        
        uid = processor.blackboard.write(  # type: ignore
            pipeline=self, document=document, processor=processor,
        )

        self.debug(
            msg=Event.Process.value,
            step=Event.Completed.value,
            uid = uid,
        )

class DataFrameSummarisePipeline(GenericPipeline):
    def process(
        self,
        processor: IProcessor,
        facade: ITarget,
        *args,
        **kwargs,
    ) -> None:
        super().process(processor=processor, facade=facade, *args, **kwargs)

        document = facade.request()  # type: ignore
        Attribute.evaluate(caller=self, document.content, pd.DataFrame)  # type: ignore
        if not document.size > 0:  # type: ignore
            self.warning(
                msg="Dataframe is feeling a bit empty today.",
                document=document,
                size=document.size,  # type: ignore
            )
            return

        content = document.content.fillna("")  # type: ignore
        facade.update_content(content)  # type: ignore
        
        uid = processor.blackboard.write(  # type: ignore
            pipeline=self, document=document, processor=processor,
        )

        self.debug(
            msg=Event.Process.value,
            step=Event.Completed.value,
            uid = uid,
        )

# Model -----------------------------------------------------------------------
class YoutubeTranscriptModel(AuditLogger):
    def __init__(
        self,
        url: str,
        level: int = logging.NOTSET,
        handler: Optional[logging.Handler] = None,
    ):
        AuditLogger.__init__(self, level=level, handler=handler)

        self.url = url
        self.storage_path = tmp.gettempdir()

        self.info(f"url: {url}")
        self.debug(f"storage path: {self.storage_path}")

        self.blackboard = GenericBlackboard(
            strategy_create=CreateDataframeDocument(
                level=self._level, handler=self._handler
            ),
            defer_flush=False,
            level=self._level,
            handler=self._handler,
        )

        # driver configuration & repository
        driver_config = {
            "repository_path": "",
            "level": self._level,
            "handler": self._handler,
            "create": True,
            "normalised": True,
        }
        self.blackboard.register(
            repository=GenericRepository(
                driver=LocalFileSystemDriver(**driver_config),
                strategy_read=RepositoryReadDocument(),
                strategy_write=WriteDataFrameDocument(),
                repository_path=self.storage_path,
                level=self._level,
                handler=self._handler,
            )
        )

        # youtube processor
        processor = YoutubeProcessor(
            blackboard=self.blackboard,
            pipelines=[
                DataFrameCleanupPipeline(level=self._level, handler=self._handler),
                DataFrameSummarisePipeline(level=self._level, handler=self._handler),
            ],
            storage_path=self.storage_path,
            allowed=["videos"],
            videos=[url],
            level=self._level,
            handler=self._handler,
        )
        processor.process_tasks()

    def view(self) -> HTMLResponse:
        view_html = Path(__file__).with_name("view").joinpath("youtube.html")
        self.debug(
            msg=Event.View.value, 
            view_html=view_html,
        )
        
        for identifier in self.blackboard._storage:
            facade = self.blackboard.read(identifier=identifier)
            document = facade.request()
            Attribute.evaluate(caller=self, document.content, pd.DataFrame)  # type: ignore

            df = document.content  # type: ignore
            # df.drop(columns=['start', 'duration'], inplace=True)
            self.debug(df.columns)
            html = TextFileStream(
                file_path=str(view_html.absolute()),
                macros=[
                    ("@TITLE", "Transcript[YouTube]"),
                    ("@H1", ""),
                    ("@URL", self.url),
                    ("@CONTENT", df.to_html(index=False)),
                    ("@FOOTER", __file__),
                ],
            )
            return HTMLResponse(content=html.content)

        return HTMLResponse(content={"error": "transcript not found."})
