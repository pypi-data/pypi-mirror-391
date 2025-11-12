# Module name: postgress.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


from __future__ import annotations
import pandas as pd
from typing import Generator
from wattleflow.core import ITarget
from wattleflow.concrete import ConnectionManager, DocumentFacade, GenericProcessor
from wattleflow.constants.enums import Event
from wattleflow.helpers import Attribute


class PostgresReadProcessor(GenericProcessor):
    def _get_uri(self, sql) -> str:
        return "postgres://%s/%s" % self.connection_name % hash(sql)

    def _get_content(self, sql):
        with self.manager.get_connection(self.connection_name) as db:
            with db.connect():
                return pd.read_sql_query(sql, db.connection)
        return pd.DataFrame({})

    def create_iterator(self) -> Generator[ITarget, None, None]:
        Attribute.mandatory(self, "connection_name", str, **self)
        Attribute.mandatory(self, "queries", list, **self)
        Attribute.mandatory(self, "manager", ConnectionManager, **self)
        self.debug(
            msg=Event.Iterating.value,
            step=Event.Started.value,
            connection_name=self.connection_name,
            queries=len(self.queries),
            manager=self.manager,
        )

        try:
            for sql in self.queries:
                uri = self._get_uri(sql=sql)
                content = self._get_content(sql=sql).to_dict()
                self.debug(msg=Event.Processing.value, uri=uri, size=len(content))

                facade: DocumentFacade = self.blackboard.create(  # type: ignore
                    caller=self,
                    processor=self,
                    uri=uri,
                    content=content,
                )
                yield facade
        except Exception as e:
            error = "Error caught in cycle %s %s" % self.cycle % str(e)
            self.error(msg=Event.Iterating.value, error=error, cycle=self.cycle)
            raise
        finally:
            self.debug(
                msg=Event.Iterating.value,
                step=Event.Completed.value,
                cycle=self.cycle,
            )
