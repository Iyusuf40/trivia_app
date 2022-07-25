import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import TEST_DB_NAME, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = TEST_DB_NAME
        self.database_path = 'postgresql://{}:{}@localhost:5432/{}'\
            .format(DB_USER, DB_PASSWORD, TEST_DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for
    expected errors.
    """

    def test_get_categories(self):
        res = self.client.get("/categories")
        self.assertEqual(res.status_code, 200)

    def test_405_get_categories_wrong_method(self):
        res = self.client.post("/categories", json={"id": 4})
        self.assertEqual(res.status_code, 405)

    def test_get_questions(self):
        res = self.client.get("/questions")
        response_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(response_body["questions"]))

    def test_404_questions_page_out_of_range(self):
        res = self.client.get("/questions?page=12")
        response_body = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(response_body["message"], "resource not found")

    def test_post_new_question(self):
        res = self.client.post("/questions", json={
                               "question": "do you know me?",
                               "answer": "well! maybe",
                               "category": "2",
                               "difficulty": 5
                               })
        response_body = json.loads(res.data)
        self.assertTrue(response_body["success"])
        self.assertEqual(res.status_code, 200)

    def test_422_post_new_question_with_wrong_parameters(self):
        res = self.client.post("/questions", json={
                               "questio": "do you know me?",
                               "answe": "well! maybe",
                               "categor": "2",
                               "difficult": 5
                               })
        response_body = json.loads(res.data)
        self.assertEqual(response_body["success"], False)
        self.assertEqual(res.status_code, 422)

    def test_search_for_questions(self):
        res = self.client.post("/questions", json={"searchTerm": "clay"})
        response_body = json.loads(res.data)
        self.assertTrue(response_body["totalQuestions"])
        self.assertEqual(res.status_code, 200)

    def test_delete_question(self):
        deleted_question = Question.query.filter(Question.id == 37).first()
        res = self.client.delete("/questions/37")

        if deleted_question:
            deleted_question = None
            self.assertEqual(res.status_code, 200)
            self.assertEqual(deleted_question, None)

    def test_404_no_question_to_delete(self):
        res = self.client.delete("/questions/3333")
        self.assertEqual(res.status_code, 404)

    def test_get_questions_by_category(self):
        res = self.client.get("/categories/4/questions")
        response_body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(response_body["questions"]))

    def test_404_get_questions_by_non_existent_category(self):
        res = self.client.get("/categories/50000/questions")
        response_body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(response_body["success"])

    def test_get_next_question(self):
        res = self.client.post("/quizzes", json={"quiz_category": "History",
                               "previous_questions": [1, 2]})
        response_body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(response_body["question"])

    def test_404_get_next_question(self):
        res = self.client.post("/quizzes", json={
                               "quiz_category": "wrong_category",
                               "previous_questions": [1, 2]
                               })
        self.assertEqual(res.status_code, 404)

    def test_405_get_next_question(self):
        res = self.client.delete("/quizzes", json={"quiz_category": "History",
                                                   "previous_questions": [1, 2]
                                                   })
        self.assertEqual(res.status_code, 405)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
