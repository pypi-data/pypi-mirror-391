# Module name: youtube.py
# Author: (wattleflow@outlook.com)
# Copyright: © 2022–2025 WattleFlow. All rights reserved.
# License: Apache 2 Licence


from __future__ import annotations
import re
import yt_dlp
from typing import Dict, Generator
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript
from wattleflow.core import ITarget
from wattleflow.concrete import GenericProcessor, AuditException
from wattleflow.constants.enums import Event


# --------------------------------------------------------------------------- #
# IMPORTANT:
# This test case requires the openpyxl library.
# Ensure you have it installed using: pip install openpyxl
# The library is used to extract dataframes from excel worksheets.
# --------------------------------------------------------------------------- #


class YoutubeError(AuditException):
    pass


class YoutubeProcessor(GenericProcessor):
    def _extract_video_id(self, url: str) -> str:
        self.debug(
            msg=Event.Processing.value,
            step=Event.Started.value,
            name="_extract_video_id",
            url=url,
        )
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        self.debug(
            msg=Event.Processing.value,
            step=Event.Completed.value,
            name="_extract_video_id",
            url=url,
        )

        return match.group(1) if match else ""

    def _fetch_metadata(self, url: str) -> Dict:
        self.debug(
            msg=Event.Processing.value,
            step=Event.Started.value,
            name="_fetch_metadata",
            url=url,
        )
        info = {}
        try:
            opts = {"quiet": True, "skip_download": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(params=opts) as ydl:  # type: ignore
                info = ydl.extract_info(url, download=False)

            self.debug(
                msg=Event.Processing.value,
                step=Event.Completed.value,
                name="_fetch_metadata",
                info=info,  # type: ignore
            )

            return info  # type: ignore

        except Exception as e:
            self.debug(msg=Event.Error.value, error=str(e))
            raise YoutubeError(caller=self, error="Failed to fetch metadata") from e

    def _fetch_transcript(self, video_id: str) -> object:
        try:
            transcript: FetchedTranscript = YouTubeTranscriptApi().fetch(
                video_id, languages=["en"]
            )
            return transcript.to_raw_data()
        except Exception as e:
            self.exception(msg=Event.Error.value, error=str(e))
            raise YoutubeError(caller=self, error="Failed to fetch transcript") from e

    def create_generator(self) -> Generator[ITarget, None, None]:
        self.debug(
            msg=Event.Creating.value,
            step=Event.Started.value,
            fnc="create_generator",
        )

        for itm in self.videos:
            try:
                uri = itm.get("uri", None)
                if uri is None:
                    continue

                video_id = self._extract_video_id(uri)
                if not video_id:
                    self.warning("Video ID could not be extracted.", url=uri)
                    continue

                metadata = self._fetch_metadata(uri)
                content = self._fetch_transcript(video_id)

                self.info(
                    msg=Event.Processing.value,
                    name="create_generator",
                    uri=uri,
                    size=len(content),  # type: ignore
                    metadata=metadata,
                )

                yield self.blackboard.create(
                    self,
                    id=video_id,
                    uri=uri,
                    content=content,
                    metadata=metadata,
                )

            except TypeError as e:
                self.critical(msg=str(e))
                raise
            except YoutubeError as e:
                self.critical(msg=e.reason, itm=itm, error=str(e.error))
                raise
            except Exception as e:
                self.critical(msg="Unexpected error", itm=itm, error=str(e))
                raise

            self.debug(
                msg=Event.Creating.value,
                step=Event.Completed.value,
                fnc="create_generator",
            )
