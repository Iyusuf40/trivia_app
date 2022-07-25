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
    CORS(app)

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

    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            return jsonify({
                "categories": dict_of_categories
                })
        except Exception:
            abort(405)

    @app.route("/questions", methods=["GET"])
    def questions_endpoint():
        try:
            questions = Question.query.order_by(Question.id).all()
            page = request.args.get("page", 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            slice_of_questions = questions[start:end]
            list_of_formated_questions = [item.format() for item in
                                          slice_of_questions]
            total_questions = len(questions)
            currentCategory_id = int(slice_of_questions[0].category)
            currentCategory = Category.query.filter(Category.id ==
                                                    currentCategory_id)\
                .first().type
            categories = dict_of_categories
            return jsonify({
                "questions": list_of_formated_questions,
                "totalQuestions": total_questions,
                "categories": categories,
                "currentCategory": currentCategory
                })
        except Exception:
            abort(404)

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).first()
            question.delete()
            return jsonify({
                "id": question.id
                })
        except Exception:
            if question is None:
                abort(404)
            abort(422)

    @app.route("/questions", methods=["POST"])
    def post_question():
        try:
            if request.get_json().get("searchTerm", 1) == 1:
                question_ = request.get_json().get("question")
                answer_ = request.get_json().get("answer")
                difficulty_ = request.get_json().get("difficulty")
                category_ = request.get_json().get("category")
                if answer_ is None or difficulty_ is None:
                    abort(422)
                if category_ is None or question_ is None:
                    abort(422)
                new_question = Question(question=question_,
                                        answer=answer_,
                                        category=category_,
                                        difficulty=difficulty_)
                new_question.insert()
                return jsonify({
                    "success": True
                    })
            else:
                searchTerm = request.get_json().get("searchTerm")
                questions = Question.query.filter(Question.question.
                                                  ilike(f"%{searchTerm}%"))\
                    .all()
                if not len(questions):
                    return jsonify({"no results": "question not found"})
                category = Category.query.filter(Category.id == questions[0]
                                                 .category).first().type
                return jsonify({
                    "questions": [item.format() for item in questions],
                    "totalQuestions": len(questions),
                    "currentCategory": category
                    })
        except Exception:
            abort(422)

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_question_by_category(id):
        try:
            if id == 0:
                questions = Question.query.order_by(Question.id).all()
                page = request.args.get("page", 1, type=int)
                start = (page - 1) * QUESTIONS_PER_PAGE
                end = start + QUESTIONS_PER_PAGE
                slice_of_questions = questions[start:end]
                list_of_formated_questions = [item.format() for item in
                                              slice_of_questions]
                total_questions = len(questions)
                currentCategory_id = int(slice_of_questions[0].category)
                currentCategory = Category.query.filter(Category.id ==
                                                        currentCategory_id)\
                    .first().type
                categories = dict_of_categories
                return jsonify({
                    "questions": list_of_formated_questions,
                    "totalQuestions": total_questions,
                    "categories": categories,
                    "currentCategory": currentCategory
                    })
            category = Category.query.filter(Category.id == id).first()
            questions = Question.query.filter(Question.category ==
                                              str(category.id)).all()
            if len(questions) == 0:
                abort(404)
            list_of_formated_questions = [item.format() for item in questions]
            totalQuestions = len(questions)
            currentCategory = category.type
            return jsonify({
                "questions": list_of_formated_questions,
                "totalQuestions": totalQuestions,
                "currentCategory": currentCategory
                })
        except Exception:
            abort(404)

    @app.route("/quizzes", methods=["POST"])
    def get_next_question():
        cat = None
        try:
            previous_questions_list = request.get_json()\
                .get("previous_questions")
            quiz_category = request.get_json().get("quiz_category")
            try:
                cat = quiz_category.get("type")
            except Exception:
                pass
            if cat is not None:
                if cat == "click":
                    list_of_options = ["Science", "Geography", "History",
                                       "Entertainment", "Sports", "Art"]
                    random.shuffle(list_of_options)
                    cat = list_of_options[0]
                quiz_category = Category.query.filter(Category.type ==
                                                      cat).first()
                quiz_category_id = str(quiz_category.id)
                list_of_questions_by_category = Question.query.\
                    filter(Question.category == quiz_category_id).all()
                random.shuffle(list_of_questions_by_category)
                item = list_of_questions_by_category[0]
                return jsonify({
                        "question": item.format()
                        })

            quiz_category = Category.query.filter(Category.type ==
                                                  quiz_category).first()
            if not quiz_category or not previous_questions_list:
                error = 404
                abort(404)
            quiz_category_id = str(quiz_category.id)
            list_of_questions_by_category = Question.query.\
                filter(Question.category == quiz_category_id).all()
            random.shuffle(list_of_questions_by_category)

            for item in list_of_questions_by_category:
                if item.id not in previous_questions_list:
                    return jsonify({
                        "question": item.format()
                        })
            abort(404)
        except Exception:
            if error == 404:
                abort(404)
            else:
                abort(405)

    @app.errorhandler(404)
    def page_not_found(error):
        return (jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404)

    @app.errorhandler(405)
    def bad_request(error):
        return (jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
            }), 405)

    @app.errorhandler(422)
    def not_processable(error):
        return (jsonify({
            "success": False,
            "error": 422,
            "message": "request not processable"
            }), 422)

    return app
