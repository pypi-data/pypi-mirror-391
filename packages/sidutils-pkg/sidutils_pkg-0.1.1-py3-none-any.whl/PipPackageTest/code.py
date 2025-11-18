import pandas as pd

class Calculator:
    """A simple calculator class with basic arithmetic operations."""

    def add(self, a: float, b: float) -> float:
        """Return the sum of a and b."""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Return the difference of a and b."""
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """Return the product of a and b."""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """Return the division of a by b. Raises ZeroDivisionError if b is zero."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b

    def power(self, base: float, exponent: float) -> float:
        """Return base raised to the power of exponent."""
        return base ** exponent

    def average(self, numbers: list[float]) -> float:
        """Return the average of a list of numbers."""
        if not numbers:
            raise ValueError("List is empty")
        return sum(numbers) / len(numbers)


def add_numbers(a, b) :
    return(a + b)        


class TextProcessor:
    """A simple class for basic text processing operations."""

    def __init__(self, text: str = ""):
        self.text = text

    def set_text(self, text: str):
        """Set the text to be processed."""
        self.text = text

    def word_count(self) -> int:
        """Return the number of words in the text."""
        return len(self.text.split())

    def char_count(self, include_spaces: bool = True) -> int:
        """Return the number of characters in the text.
        If include_spaces=False, spaces are not counted.
        """
        if include_spaces:
            return len(self.text)
        return len(self.text.replace(" ", ""))

    def reverse(self) -> str:
        """Return the reversed text."""
        return self.text[::-1]

    def uppercase(self) -> str:
        """Return the text in uppercase."""
        return self.text.upper()

    def lowercase(self) -> str:
        """Return the text in lowercase."""
        return self.text.lower()

