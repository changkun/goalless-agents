import json
import io
import tempfile
import unittest
from pathlib import Path

import text_digest


SAMPLE = (
    "Rivers shape cities over time. Rivers support trade and farming. "
    "Cities near rivers often become major hubs."
)


class SummaryTests(unittest.TestCase):
    def test_split_sentences(self) -> None:
        self.assertEqual(len(text_digest.split_sentences(SAMPLE)), 3)

    def test_extract_keywords(self) -> None:
        keywords = text_digest.extract_keywords(SAMPLE, 3)
        self.assertEqual(keywords[0]["term"], "rivers")
        self.assertEqual(keywords[0]["count"], 3)

    def test_summarize_keeps_requested_sentences(self) -> None:
        result = text_digest.summarize(SAMPLE, sentence_limit=2, keyword_limit=2)
        self.assertEqual(
            result["summary"],
            "Rivers shape cities over time. Rivers support trade and farming.",
        )
        self.assertEqual(len(result["keywords"]), 2)


class CliTests(unittest.TestCase):
    def test_main_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.txt"
            path.write_text(SAMPLE, encoding="utf-8")

            with tempfile.TemporaryFile(mode="w+") as capture:
                import sys

                stdout = sys.stdout
                sys.stdout = capture
                try:
                    exit_code = text_digest.main([str(path), "--json", "--keywords", "2"])
                finally:
                    sys.stdout = stdout

                capture.seek(0)
                payload = json.loads(capture.read())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["sentence_count"], 3)
        self.assertEqual(len(payload["keywords"]), 2)

    def test_main_missing_file(self) -> None:
        import sys

        stderr = sys.stderr
        capture = io.StringIO()
        sys.stderr = capture
        try:
            exit_code = text_digest.main(["missing.txt"])
        finally:
            sys.stderr = stderr

        self.assertEqual(exit_code, 1)
        self.assertIn("file not found", capture.getvalue())


if __name__ == "__main__":
    unittest.main()
