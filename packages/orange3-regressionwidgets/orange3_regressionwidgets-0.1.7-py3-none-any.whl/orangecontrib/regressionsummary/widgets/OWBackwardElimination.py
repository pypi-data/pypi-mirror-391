# File: OWBackwardElimination.py

from Orange.widgets import gui 
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.settings import Setting
from Orange.widgets.gui import button

from Orange.data import Table, Domain
from Orange.data.pandas_compat import table_to_frame

from PyQt5.QtWidgets import (
    QTextEdit,
    QComboBox,
    QFormLayout,
    QDoubleSpinBox,
    QLabel
)

from PyQt5.QtGui import QFont

import statsmodels.api as sm
import pandas as pd

class OWBackwardElimination(OWWidget):
    name = "Backward Elimination"
    description = "Stepwise feature selection based on p-value or AIC for OLS or Logit"
    icon = "icons/backward_elimination.svg"
    priority = 20
    category = "Regression"

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        reduced_data = Output("Reduced Data", Table)
        model_summary = Output("Model Summary", str)

    want_main_area = True

    method = Setting("p-value")
    threshold = Setting(0.05)
    model_type = Setting("OLS")

    def __init__(self):
        super().__init__()
        self.data = None

        # --- Group all controls in one vertical box ---
        controls_box = gui.widgetBox(self.controlArea, box=None)

        # Create form layout inside that box
        form_layout = QFormLayout()
        controls_box.layout().addLayout(form_layout)

        # --- Regression Type ---
        self.reg_type_cb = QComboBox()
        self.reg_type_cb.addItems(["OLS", "Logit"])
        self.reg_type_cb.setCurrentText(str(self.model_type))
        self.reg_type_cb.currentTextChanged.connect(lambda t: setattr(self, "model_type", t))
        form_layout.addRow("Regression Type:", self.reg_type_cb)

        # --- Elimination Criterion ---
        self.criterion_cb = QComboBox()
        self.criterion_cb.addItems(["p-value", "AIC"])
        self.criterion_cb.setCurrentText(str(self.method))
        self.criterion_cb.currentTextChanged.connect(lambda t: setattr(self, "method", t))
        form_layout.addRow("Elimination Criterion:", self.criterion_cb)

        # --- p-value Threshold ---
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.001, 1.0)
        self.threshold_spin.setSingleStep(0.01)
        self.threshold_spin.setValue(float(self.threshold))
        self.threshold_spin.valueChanged.connect(lambda v: setattr(self, "threshold", v))
        form_layout.addRow("p-value Threshold:", self.threshold_spin)
        
        # Run button
        #run_button = QPushButton("Run Backward Elimination")
        #run_button.clicked.connect(self.run_elimination)
        #self.controlArea.layout().addWidget(run_button)

        # Log window
        self.mainArea.layout().addWidget(QLabel("Elimination Log:"))
        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setFont(QFont("Courier", 10))
        self.mainArea.layout().addWidget(self.info_box)
        # Orange-style button
        button(self.buttonsArea, self, "Run Backward Elimination", callback=self.run_elimination)

    @Inputs.data
    def set_data(self, data):
        self.data = data
        if self.data is not None:
            self.info_box.setPlainText("Data received. Ready to run elimination.")
            # Optional auto-run on data input:
            # self.run_elimination()
        else:
            self.info_box.setPlainText("No data received. Connect a dataset to begin.")

    def run_elimination(self):
        if self.data is None:
            self.info_box.setPlainText("No data input.")
            return

        if self.data.domain.class_var is None:
            self.info_box.setPlainText("No target variable (class_var) defined in dataset.")
            return

        df = table_to_frame(self.data)
        target_name = self.data.domain.class_var.name
        X = df.drop(columns=[target_name])
        y = df[target_name]

        # Encode and clean
        X = pd.get_dummies(X, drop_first=True)
        X = sm.add_constant(X, has_constant="add")
        X = X.apply(pd.to_numeric, errors='coerce')
        y = pd.to_numeric(y, errors='coerce')
        valid_idx = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[valid_idx]
        y = y[valid_idx]

        method = self.criterion_cb.currentText()
        model_type = self.reg_type_cb.currentText()
        threshold = self.threshold_spin.value()
        log = ""

        def fit_model(X, y):
            if model_type == "Logit":
                unique_vals = sorted(y.dropna().unique())
                if unique_vals != [0, 1] and unique_vals != [1, 0]:
                    raise ValueError("Target variable is not binary (0/1) for Logit.")
                return sm.Logit(y, X).fit(disp=False)
            return sm.OLS(y, X).fit()

        try:
            eliminated = []
            current_X = X.copy()

            while True:
                model = fit_model(current_X, y)

                if method == "p-value":
                    pvals = model.pvalues.drop("const", errors="ignore")
                    max_p = pvals.max()
                    if max_p > threshold:
                        drop_var = pvals.idxmax()
                        log += f"Removing {drop_var} with p-value {max_p:.4f}\n"
                        current_X = current_X.drop(columns=drop_var)
                        eliminated.append(drop_var)
                    else:
                        break

                elif method == "AIC":
                    best_aic = model.aic
                    worst_var = None
                    for var in current_X.columns:
                        if var == "const":
                            continue
                        temp_X = current_X.drop(columns=var)
                        temp_model = fit_model(temp_X, y)
                        if temp_model.aic < best_aic:
                            best_aic = temp_model.aic
                            worst_var = var
                    if worst_var:
                        log += f"Removing {worst_var} to reduce AIC to {best_aic:.2f}\n"
                        current_X = current_X.drop(columns=worst_var)
                        eliminated.append(worst_var)
                    else:
                        break

            self.info_box.setPlainText(log)
            final_model = fit_model(current_X, y)
            summary_str = final_model.summary().as_text()
            self.Outputs.model_summary.send(summary_str)

            # Build reduced domain
            kept_vars = [col for col in current_X.columns if col != "const"]
            reduced_attrs = [var for var in self.data.domain.attributes if var.name in kept_vars]
            reduced_domain = Domain(reduced_attrs, self.data.domain.class_var)
            reduced_table = Table.from_table(reduced_domain, self.data)
            self.Outputs.reduced_data.send(reduced_table)

        except Exception as e:
            self.info_box.setPlainText("Error:\n" + str(e))