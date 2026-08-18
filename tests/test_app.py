import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from src import app
from src.repository import ActivityRepository


class ActivityApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "test.db"
        seed_path = Path(__file__).parents[1] / "src" / "activities.json"
        self.repository = ActivityRepository(database_path, seed_path)
        self.repository_patch = patch.object(app, "repository", self.repository)
        self.repository_patch.start()

    def tearDown(self):
        self.repository_patch.stop()
        self.temp_directory.cleanup()

    def test_signup_preserves_api_behavior(self):
        result = app.signup_for_activity(
            "Chess Club", "new.student@mergington.edu"
        )

        self.assertEqual(
            result,
            {"message": "Signed up new.student@mergington.edu for Chess Club"},
        )
        self.assertIn(
            "new.student@mergington.edu",
            app.get_activities()["Chess Club"]["participants"],
        )

    def test_duplicate_signup_returns_bad_request(self):
        with self.assertRaises(HTTPException) as context:
            app.signup_for_activity("Chess Club", "michael@mergington.edu")

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Student is already signed up")


if __name__ == "__main__":
    unittest.main()