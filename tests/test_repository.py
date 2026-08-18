import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.repository import ActivityRepository


class ActivityRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "test.db"
        self.seed_path = Path(__file__).parents[1] / "src" / "activities.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_registrations_persist_across_repository_instances(self):
        repository = ActivityRepository(self.database_path, self.seed_path)
        repository.signup("Chess Club", "new.student@mergington.edu")

        restarted_repository = ActivityRepository(self.database_path, self.seed_path)
        activities = restarted_repository.list_activities()

        self.assertIsInstance(activities["Chess Club"]["id"], int)
        self.assertIn(
            "new.student@mergington.edu",
            activities["Chess Club"]["participants"],
        )
        with self.assertRaises(sqlite3.IntegrityError):
            restarted_repository.signup(
                "Chess Club", "new.student@mergington.edu"
            )


if __name__ == "__main__":
    unittest.main()