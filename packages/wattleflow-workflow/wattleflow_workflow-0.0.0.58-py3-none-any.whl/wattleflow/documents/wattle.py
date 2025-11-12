# Module name: wattle.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


from __future__ import annotations
import logging
from enum import Enum
from datetime import datetime
from typing import Iterable, Optional
from rdflib import Graph, Namespace, URIRef, Node, Literal
from rdflib.namespace import DCAT, DCTERMS, PROV, RDF
from uuid import uuid4
from wattleflow.core import IWattleflow
from wattleflow.concrete import Document
from wattleflow.constants import Event


class MimeType(Enum):
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"
    APPLICATION_ZIP = "application/zip"
    # APPLICATION_RECORD = "application/vnd.%s.record+json"
    APPLICATION_YOUTUBE_TRANSCRIPT = "application/vnd.youtube.transcript+json"
    IMAGE_BMP = "image/bmp"
    IMAGE_GIF = "image/gif"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    TEXT_CSV = "text/csv"
    TEXT_HTML = "text/html"
    TEXT_PLAIN = "text/plain"
    AUDIO_MPEG = "audio/mpeg"
    VIDEO_MP4 = "video/mp4"


class ProvenanceHandler(Enum):
    Processor = "Processor"
    Pipeline = "Pipeline"
    CreateStrategy = "Create Strategy"
    WriteStrategy = "Write Strategy"


class Wattle(Document[Graph]):
    def __init__(
        self,
        caller: IWattleflow,
        mime: MimeType,
        uri: str,
        level: int = logging.NOTSET,
        handler: Optional[logging.Handler] = None,
    ):

        WG = Namespace("urn:wattle:vocab#")
        RES = Namespace("urn:wattle:resource:")
        # DCAT = Namespace("http://www.w3.org/ns/dcat#")
        # PROV = Namespace("http://www.w3.org/ns/prov#")
        NFO = Namespace("http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#")

        identifier = uuid4()
        graph = Graph(identifier=URIRef(f"urn:wattleflow:graph:{identifier}"))

        for pfx, ns in [
            ("WG", WG),
            ("RES", RES),
            ("DCAT", DCAT),
            ("PROV", PROV),
            ("NFO", NFO),
            ("DCTERMS", DCTERMS),
        ]:
            graph.bind(pfx, ns)

        subject = RES["wattle"]

        # processor
        graph.add((subject, RDF.type, WG.Processor))
        graph.add((subject, WG.Processor, Literal(caller.name)))

        # graph type
        graph.add((subject, RDF.type, WG.Artifact))
        graph.add((subject, RDF.type, DCAT.Distribution))

        # record
        graph.add((subject, RDF.type, DCAT.record))
        graph.add((subject, DCAT.record, Literal(mime.name)))

        # created
        graph.add((subject, RDF.type, WG.Created))
        graph.add((subject, WG.runId, Literal(str(self.utc_time_stamp()))))

        # format
        graph.add((RES[mime.name], DCTERMS.format, Literal(mime.value)))

        # steps
        graph.add((RES[caller.name], RDF.type, WG.Step))
        graph.add((RES[caller.name], WG.hasStep, Literal("Creation")))

        # connection
        graph.add((RES[caller.name], PROV.used, RES[mime.name]))
        graph.add((RES[caller.name], PROV.generated, RES[mime.value]))

        # # content
        # graph.add((RES[caller.name], RDF.type, WG.Content))
        # graph.add((RES[caller.name], WG.hasContent, Literal("")))

        Document.__init__(self, content=graph, level=level, handler=handler)
        self._identifier = str(identifier)

        self.debug(
            msg=Event.Constructor.value,
            step=Event.Started.value,
            identifier=self.identifier,
            level=level,
            handler=handler,
            uri=uri,
        )

        self.update_metadata("subject", subject)
        self.update_metadata("WG", WG)
        self.update_metadata("RES", RES)
        self.update_metadata("DCAT", DCAT)
        self.update_metadata("PROV", PROV)
        self.update_metadata("NFO", NFO)

        self.debug(
            msg=Event.Constructor.value,
            step=Event.Completed.value,
        )

    @property
    def namespaces(self) -> Iterable[tuple[str, URIRef]]:
        return self.content.namespace_manager.namespaces()

        # def namespacemap(self):
        # ns_map = dict(self.content.namespace_manager.namespaces())
        # ns = ns_map.get("schema")
        # for _, uri in ns_map.items():
        #     u = str(uri).rstrip("/")
        #     if u in ("http://schema.org", "https://schema.org"):
        #         return Namespace(uri)
        # raise ValueError("Schema is not found!")

    @property
    def size(self) -> int:
        if isinstance(self.content, Graph):
            return len(self.content)
        return 0

    @property
    def uri(self) -> str:
        return str(self.metadata.get("uri", ""))

    def specific_request(self) -> "Wattle":
        return self

    def add(self, subject: Namespace, predicate: URIRef, value: str):
        self._content.add((subject, predicate, Literal(value)))  # type: ignore
        self._lastchange = datetime.now()

    def add_predicate(self, predicate: URIRef, value: str):
        self._content.add((self.subject, predicate, Literal(value)))  # type: ignore
        self._lastchange = datetime.now()

    def remove(self, predicate: URIRef, value: object):
        self._content.remove((self._subject, predicate, Literal(value)))  # type: ignore
        self._lastchange = datetime.now()

    def clear(self):
        self._content.remove((None, None, None))  # type: ignore
        self._content = Graph(identifier=self.subject)  # type: ignore
        self._lastchange = datetime.now()

    def get(self, predicate: URIRef, default: Optional[Node] = None) -> Optional[Node]:
        try:
            result = self._content.value(  # type: ignore
                subject=self.subject,  # type: ignore
                predicate=predicate,
                default=default,
            )
            return result
        except Exception as e:
            self.error(msg=Event.Getting.value, error=str(e))
            return default

    def update_graph(self, new_graph: Graph):
        copied = Graph(identifier=new_graph.identifier)

        for triple in new_graph:
            copied.add(triple)

        for prefix, ns in new_graph.namespaces():
            copied.bind(prefix, ns, override=True)

        self.update_content(copied)

    def __getattr__(self, name: str) -> object:
        obj = self.metadata.get(name, None)
        if obj is None:
            raise ValueError(f"Property: {name} does not exist in the document!")
        return obj
