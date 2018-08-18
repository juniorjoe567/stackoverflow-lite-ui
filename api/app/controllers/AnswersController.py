from flask import jsonify, request
from api.app.models import Question, Answer


class AnswersController:
    @classmethod
    def index(cls, question_id):
        question = Question.find_or_fail(question_id).load("answers")
        return jsonify(dict(data=question["answers"]))

    @classmethod
    def show(cls, question_id, answer_id):
        answer = Answer.where(
            question_id=question_id,
            id=answer_id
        ).first_or_fail()

        return jsonify(dict(data=answer)), 200

    @classmethod
    def store(cls, question_id):
        question = Question.find_or_fail(question_id)
        answer = question.answers().create(request.validate({
            "body": "required"
        }))
        return jsonify(dict(data=answer)), 201
