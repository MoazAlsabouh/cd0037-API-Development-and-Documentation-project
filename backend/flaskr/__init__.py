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
    CORS(app, resources={r"/api/*": {"origins": "*"}})


# get questions to one page 10
    def paginate(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current = questions[start:end]

        return current

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def request_header(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def categories():
        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type

        if (len(categories_dictionary) == 0):
            abort(404)
        else :
            return jsonify({
                'success': True,
                'categories': categories_dictionary
            })

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

    @app.route('/questions')
    def questions():
        selection = Question.query.all()
        total_questions = len(selection)
        current = paginate(request, selection)

        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type

        if (len(current) == 0):
            abort(404)
        else :
            return jsonify({
                'success': True,
                'questions': current,
                'total_questions': total_questions,
                'categories': categories_dictionary
            })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id=question_id).one_or_none()

            if question is None:
                abort(404)
            else:
                question.delete()

                return jsonify({
                    'success': True,
                    'deleted': question_id
                })

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        if (
            (new_question is None) or
            (new_answer is None) or
            (new_difficulty is None) or
            (new_category is None)
        ):
            abort(422)
        
        else:
            try:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category
                )
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')

        if search_term:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')
            ).all()

            if len(selection) == 0:
                abort(404)
            else:
                paginated = paginate(request, selection)

                return jsonify({
                    'success': True,
                    'questions': paginated,
                    'total_questions': len(Question.query.all())
                })

        else:
            abort(400)





    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()

        if (category is None):
            abort(400)
        else: 
            selection = Question.query.filter_by(category=category.id).all()

            paginated = paginate(request, selection)

            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all()),
                'current_category': category.type
            })
        
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

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = quiz_category['id']

            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()
            question = None
            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except:
            abort(422)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400


    return app

