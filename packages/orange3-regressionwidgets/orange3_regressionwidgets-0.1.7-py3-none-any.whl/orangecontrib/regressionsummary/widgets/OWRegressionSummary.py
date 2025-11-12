# File: OWRegressionSummary.py

from Orange.widgets import gui
from Orange.data.pandas_compat import table_to_frame
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.data import Table, Domain, ContinuousVariable, StringVariable
from PyQt5.QtWidgets import QTextEdit, QPushButton, QApplication, QComboBox, QFormLayout, QWidget
from PyQt5.QtGui import QFont
import statsmodels.api as sm
import numpy as np
import pandas as pd


class OWRegressionSummary(OWWidget):
    name = "Regression Summary"
    description = "Displays full regression summary statistics using statsmodels."
    icon = "icons/RegressionSummary.svg"
    priority = 10
    category = "Regression"

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        summary_table = Output("Summary Table", Table)

    want_main_area = True

    def __init__(self):
        super().__init__()
        self.data = None

        # Compact form layout like standard Orange widgets
        form = QFormLayout()
        container = QWidget()
        container.setLayout(form)
        self.controlArea.layout().addWidget(container)

        # Dropdown for regression type
        self.regression_type = QComboBox()
        self.regression_type.addItems(["OLS", "Logit"])
        form.addRow("Regression Type:", self.regression_type)

        # Orange-style button at bottom
        gui.button(self.buttonsArea, self, "Generate Summary", callback=self.generate_summary)

        # Text output in main area
        self.model_stats_box = gui.widgetBox(self.mainArea, "Regression Output")
        self.model_stats = QTextEdit()
        self.model_stats.setReadOnly(True)
        self.model_stats.setFont(QFont("Courier", 10))
        self.model_stats.setMinimumHeight(120)
        self.model_stats_box.layout().addWidget(self.model_stats)

    @Inputs.data
    def set_data(self, data):
        self.data = data

    def create_tsv_for_excel(self, model, var_names):
        header = "\t".join(["Variable", "Coefficient", "Std_Error", "T_Value", "P_Value", "CI_Lower", "CI_Upper"])
        rows = []
        for i, name in enumerate(var_names):
            row = [
                name,
                f"{model.params[i]:.4f}",
                f"{model.bse[i]:.4f}",
                f"{model.tvalues[i]:.4f}",
                f"{model.pvalues[i]:.4e}",
                f"{model.conf_int().iloc[i, 0]:.4f}",
                f"{model.conf_int().iloc[i, 1]:.4f}"
            ]
            rows.append("\t".join(row))
        return header + "\n" + "\n".join(rows)

    def generate_summary(self):
        if self.data is None:
            self.error("No data received.")
            return

        if self.data.domain.class_var is None:
            self.error("No target variable defined.")
            return

        # Extract feature and target names
        feature_names = [var.name for var in self.data.domain.attributes]
        target_name = self.data.domain.class_var.name

        df = table_to_frame(self.data)
        X_df = df[feature_names]
        y_df = df[[target_name]]

        X_df = pd.get_dummies(X_df, drop_first=True)
        combined_df = pd.concat([X_df, y_df], axis=1).dropna()

        if combined_df.empty:
            self.error("All rows contain missing values after preprocessing.")
            return

        X_clean = combined_df.drop(columns=target_name)
        y_clean = combined_df[target_name]

        use_logit = self.regression_type.currentText() == "Logit"
        is_binary = set(y_clean.unique()) <= {0, 1}

        X_with_const = sm.add_constant(X_clean, has_constant="add")
        X_with_const = X_with_const.apply(pd.to_numeric, errors='coerce')
        y_clean = pd.to_numeric(y_clean, errors='coerce')

        valid_idx = ~(X_with_const.isnull().any(axis=1) | y_clean.isnull())
        X_with_const = X_with_const[valid_idx]
        y_clean = y_clean[valid_idx]

        if use_logit:
            if not is_binary:
                self.error("Target variable is not binary for Logit regression.")
                return
            model = sm.Logit(y_clean, X_with_const).fit(disp=False)
        else:
            model = sm.OLS(y_clean, X_with_const).fit()

        self.Outputs.summary_table.send(self.create_output_table(model))

        summary_text = model.summary().as_text()
        var_names = X_with_const.columns.tolist()
        tsv_text = self.create_tsv_for_excel(model, var_names)

        self.model_stats.setPlainText(summary_text)

        # Remove and re-add buttons to avoid stacking
        for attr in ['copy_excel_btn', 'copy_button']:
            if hasattr(self, attr):
                btn = getattr(self, attr)
                self.controlArea.layout().removeWidget(btn)
                btn.deleteLater()

        self.copy_excel_btn = QPushButton("Copy Coefficients for Excel")
        self.copy_excel_btn.clicked.connect(lambda: QApplication.clipboard().setText(tsv_text))
        self.controlArea.layout().addWidget(self.copy_excel_btn)

        self.copy_button = QPushButton("Copy Regression Output")
        self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(summary_text))
        self.controlArea.layout().addWidget(self.copy_button)

    def create_output_table(self, model):
        params = model.params
        bse = model.bse
        tvals = model.tvalues
        pvals = model.pvalues
        conf_int = model.conf_int()

        var_names = ["Intercept"] + [var.name for var in self.data.domain.attributes]

        domain = Domain([
            ContinuousVariable("Coefficient"),
            ContinuousVariable("Std_Error"),
            ContinuousVariable("T_Value"),
            ContinuousVariable("P_Value"),
            ContinuousVariable("CI_Lower"),
            ContinuousVariable("CI_Upper")
        ], metas=[StringVariable("Variable")])

        rows = []
        for i in range(len(var_names)):
            row = [
                params[i],
                bse[i],
                tvals[i],
                pvals[i],
                conf_int.iloc[i, 0],
                conf_int.iloc[i, 1]
            ]
            rows.append(row)

        X = np.array(rows)
        metas = np.array([[name] for name in var_names], dtype=object)

        return Table(domain, X, metas=metas)