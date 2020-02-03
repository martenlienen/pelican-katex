from html_template import HTMLTemplate


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, HTMLTemplate) and isinstance(right, str) and op == "==":
        return left.describe(right)
