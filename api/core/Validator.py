import re
from api.core.exceptions import ValidationException
from api.core.db.query import DB


class Rule:
    def __init__(self, value, name, param, field):
        self.value = value
        self.name = name
        self.param = param
        self.field = field

    def _set_validator(self, validator):
        self.validator = validator
        return self

    @property
    def label(self):
        return f"{self.field} field"

    @classmethod
    def _make(cls, validator, rule, value, field):
        parts = rule.split(':')
        name = parts[0]
        try:
            param = parts[1]
        except IndexError:
            param = None

        return Rule(value, name, param, field)._set_validator(validator)

    def required(self):

        return self._make_error(
            not self.is_null(),
            f'{self.label} is required'
        )

    def email(self):
        is_email = re.match(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            str(self.value)
        )
        return self._make_error(is_email, f"{self.label} is not a valid email")

    def unique(self):
        is_unique = DB.table(self.param).where(
            {self.field: self.value}
        ).exists()

        return self._make_error(
            not is_unique, f"{self.field} has already been taken"
        )

    def confirmed(self):
        confirmed = self.validator.values.get(f"{self.field}_confirmation")

        return self._make_error(
            self.value == confirmed,
            f"{self.label} confirmation doesn't match"
        )

    def is_null(self):
        # 0 is an false but not a null value
        return (self.value == '' or self.value is None)

    def min_length(self):
        return self._validatelen(lambda a, b: a < b, "at least")

    def max_length(self):
        return self._validatelen(lambda a, b: a > b, "more than")

    def length(self):
        return self._validatelen(lambda a, b: a == b)

    def _validatelen(self, callback, prefix=""):
        value_len = len(str(self.value))
        length = int(self.param)
        error = f"{self.label} must be {prefix} {length} characters"
        return self._make_error(callback(length, value_len), error)

    @classmethod
    def _make_error(self, condition, message):
        if condition:
            return None
        return message

    def run(self):
        return getattr(self, self.name)()


class Validator:
    def __init__(self, values):
        self.values = values
        self.errors = dict()
        self.rules = []

    def _set_rules(self, field, rules):
        value = self.values.get(field, None)
        for rule in str(rules).split("|"):
            self.rules.append(Rule._make(self, rule, value, field))

    def _normalize_rules(self, rules):
        for field in rules:
            self._set_rules(field, rules[field])

    def validate(self, rules):
        self._normalize_rules(rules)
        for rule in self.rules:
            self._run_rule(rule)

        if len(self.errors):
            raise ValidationException(self.errors)
        # return the validated keys
        return list(rules.keys())

    def _run_rule(self, rule):
        error = rule.run()
        if not error:
            return
        existing = self.errors.get(rule.field, [])
        existing.append(error)
        self.errors[rule.field] = existing
