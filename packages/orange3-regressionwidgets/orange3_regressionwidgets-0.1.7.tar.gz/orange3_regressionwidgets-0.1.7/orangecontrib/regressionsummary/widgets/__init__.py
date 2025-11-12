import os

NAME = "Regression"
DESCRIPTION = "Regression Tools"
BACKGROUND = "#D5E8D4"
ICON = os.path.join(os.path.dirname(__file__), "icons", "category.svg")
PRIORITY = 10

WIDGETS = ("OWRegressionSummary", "OWBackwardElimination")