import pathlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from youtube_transcript_api import NoTranscriptFound

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from scripts.sync import best_effort_transcript


class BestEffortTranscriptTests(unittest.TestCase):
    def test_success(self):
        dummy_transcript = MagicMock()
        dummy_transcript.fetch.return_value = [{"text": "hello"}, {"text": "world"}]
        dummy_list = MagicMock()
        dummy_list.find_manually_created_transcript.return_value = dummy_transcript

        with patch(
            "scripts.sync.YouTubeTranscriptApi.list_transcripts",
            return_value=dummy_list,
            create=True,
        ):
            result = best_effort_transcript("vid")
        self.assertEqual(result, "hello\n\nworld")

    def test_no_transcript(self):
        with patch(
            "scripts.sync.YouTubeTranscriptApi.list_transcripts",
            side_effect=NoTranscriptFound("vid", ["en"], {}),
            create=True,
        ):
            result = best_effort_transcript("vid")
        self.assertEqual(result, "*No transcript available yet*")

    @patch("time.sleep", return_value=None)
    def test_retry_failure(self, _sleep):
        with patch(
            "scripts.sync.YouTubeTranscriptApi.list_transcripts",
            side_effect=RuntimeError("boom"),
            create=True,
        ):
            with patch(
                "scripts.sync.YouTubeTranscriptApi.get_transcript",
                side_effect=Exception("fail"),
                create=True,
            ) as gt:
                result = best_effort_transcript("vid")
                self.assertEqual(result, "*Transcript fetch error – will retry later*")
                self.assertEqual(gt.call_count, 3)


if __name__ == "__main__":
    unittest.main()
