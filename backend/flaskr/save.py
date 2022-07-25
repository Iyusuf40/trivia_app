import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    categories = Category.query.all()
    dict_of_categories = {}
    for item in categories:
        dict_of_categories[str(item.id)] = item.type
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            return jsonify({
            "categories" : dict_of_categories
            })
        except:
            abort(405)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def questions_endpoint():
        try:
            questions = Question.query.order_by(Question.id).all()
            page = request.args.get("page", 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            slice_of_questions = questions[start:end]
            list_of_formated_questions = [item.format() for item in slice_of_questions]
            total_questions = len(questions)
            currentCategory_id = int(slice_of_questions[0].category)
            currentCategory = Category.query.filter(Category.id==currentCategory_id).first().type
            categories = dict_of_categories
            return jsonify({
            "questions" : list_of_formated_questions,
            "totalQuestions" : total_questions,
            "categories" : categories,
            "currentCategory" : currentCategory
            })
        except:
            abort (404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id==id).first()
            question.delete()
            return jsonify({
            "id" : question.id
            })
        except:
            if question is None:
                abort(404)
            abort (422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def post_question():
        try:
            if request.get_json().get("searchTerm", 1) == 1:
                question_ = request.get_json().get("question")
                answer_ = request.get_json().get("answer")
                difficulty_ = request.get_json().get("difficulty")
                category_ = request.get_json().get("category")
                if answer_ == None:
                    abort(422)
                new_question = Question(question=question_, answer=answer_, category=category_, difficulty=difficulty_)
                new_question.insert()
                return jsonify({
                "success" : True
                })
            else:
                searchTerm = request.get_json().get("searchTerm")
                questions = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()
                if not len(questions):
                    return jsonify({"no results": "question not found"})
                category = Category.query.filter(Category.id==questions[0].category).first().type
                return jsonify({
                "questions" : [item.format() for item in questions],
                "totalQuestions" : len(questions),
                "currentCategory" : category
                })
        except:
            abort (422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_question_by_category(id):
        try:
            category = Category.query.filter(Category.id==id).first()
            questions = Question.query.filter(Question.category==str(category.id)).all()
            if len(questions) == 0:
                abort(404)
            list_of_formated_questions = [item.format() for item in questions]
            totalQuestions = len(questions)
            currentCategory = category.type
            return jsonify({
            "questions" : list_of_formated_questions,
            "totalQuestions" : totalQuestions,
            "currentCategory" : currentCategory
            })
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_next_question():
        try:
            previous_questions_list = request.get_json().get("previous_questions")
            quiz_category = request.get_json().get("quiz_category")
            quiz_category = Category.query.filter(Category.type==quiz_category).first()
            if not quiz_category:
                error = 404
                abort(404)
            quiz_category_id = str(quiz_category.id)
            list_of_questions_by_category = Question.query.filter(Question.category==quiz_category_id).all()
            random.shuffle(list_of_questions_by_category)

            for item in list_of_questions_by_category:
                if item.id not in previous_questions_list:
                    return jsonify({
                    "question" : item.format()
                    })
            return jsonify({
            "question" : "bravo! already answered all questions in this category"
            })
        except:
            if error == 404:
                abort(404)
            else:
                abort (405)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def page_not_found(error):
        return (jsonify({
        "success" : False,
        "error": 404,
        "message" : "resource not found"
        }), 404)

    @app.errorhandler(405)
    def bad_request(error):
        return (jsonify({
        "success": False,
        "error": 405,
        "message" : "method not allowed"
        }), 405)

    @app.errorhandler(422)
    def not_processable(error):
        return (jsonify({
        "success": False,
        "error": 422,
        "message" : "request not processable"
        }), 422)

    return app
