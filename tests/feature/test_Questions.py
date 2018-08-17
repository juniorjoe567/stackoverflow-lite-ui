from tests.feature import BaseTestCase


class TestQuestions(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.question = dict(
            title="Whats your take on Joining Andela",
            description="Give a description on what your take on"
            "Joinong andela would be"
        )

    def test_it_returns_a_200_response_for_index_route(self):
        rv = self.get("/questions")
        self.assertEqual(rv.status_code, 200)

    def test_it_returns_a_422_response_for_invalid_data(self):
        rv = self.post("/questions", {})
        self.assertEqual(rv.status_code, 422)

    def test_it_returns_a_201_response_for_valid_data(self):
        rv = self.post("/questions", self.question)
        self.assertEqual(rv.status_code, 201)

    def test_it_returns_a_json_data_with_a_valid_question(self):
        rv = self.post("/questions", self.question)
        self.assertDictContainsSubset(self.question, rv.get_json()["data"])

    def test_it_gives_an_message_with_invalid_data(self):
        rv = self.post("/questions", {})
        data = rv.get_json()
        self.assertEqual(data["message"], "Validation Failed")
