from enum import Enum


class UserRole(str, Enum):
    student = "student"
    admin = "admin"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionType(str, Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    fill_blank = "fill_blank"
    multiple_answer = "multiple_answer"
    matching = "matching"
    short_answer = "short_answer"
