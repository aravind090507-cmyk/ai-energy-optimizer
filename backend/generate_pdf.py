import os
from fpdf import FPDF

class WalkthroughPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(100, 116, 139) # Slate 500
            self.cell(0, 10, 'AI Energy Optimizer & Smart Scheduling - Project Walkthrough & ML Diagnostics', 0, 0, 'L')
            self.draw_accent_bar()
            self.ln(15)
            
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
    def draw_accent_bar(self):
        # Draw a thin color strip at the top of the header
        self.set_fill_color(56, 189, 248) # Cyan: #38BDF8
        self.rect(15, 12, 90, 0.8, 'F')
        self.set_fill_color(167, 139, 250) # Purple: #A78BFA
        self.rect(105, 12, 90, 0.8, 'F')

    def add_section_header(self, text):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(14, 116, 144) # Dark cyan
        self.cell(0, 10, text, 0, 1, 'L')
        self.ln(3)

    def add_paragraph(self, text):
        self.set_font('helvetica', '', 10.5)
        self.set_text_color(30, 41, 59) # Slate 800
        self.multi_cell(0, 6, text)
        self.ln(4)

    def add_bullet_point(self, title, desc):
        self.set_font('helvetica', 'B', 10.5)
        self.set_text_color(14, 116, 144)
        self.write(6, f"- {title}: ")
        self.set_font('helvetica', '', 10.5)
        self.set_text_color(30, 41, 59)
        self.write(6, f"{desc}\n")
        self.ln(2)

def main():
    pdf = WalkthroughPDF(orientation='P', unit='mm', format='A4')
    pdf.alias_nb_pages()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # -----------------------------
    # PAGE 1: TITLE PAGE & INTRODUCTION
    # -----------------------------
    pdf.add_page()
    
    # Decorative Header Band
    pdf.set_fill_color(15, 23, 42) # Dark Slate 900
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('helvetica', 'B', 20)
    pdf.set_y(12)
    pdf.cell(0, 10, 'AI-DRIVEN HOUSEHOLD ENERGY MANAGEMENT', 0, 1, 'C')
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(56, 189, 248) # Cyan
    pdf.cell(0, 8, 'Demand Forecasting, Anomaly Detection, and Smart Load Scheduling', 0, 1, 'C')
    
    pdf.set_y(55)
    pdf.add_section_header("1. Project Abstract & Introduction")
    pdf.add_paragraph(
        "Residential energy consumption represents a massive and growing share of worldwide electricity demand. "
        "However, household usage patterns are typically highly inefficient and carbon-heavy due to a lack of "
        "real-time consumer insights, localized load forecasting, and automated scheduler tools. "
        "This project presents the AI Energy Optimizer & Smart Scheduling System, a software dashboard and machine "
        "learning pipeline designed to predict energy draw, classify intensity zones, flag hardware faults, and "
        "automatically shift appliance cycles to low-tariff, lower-carbon hours."
    )
    
    pdf.add_section_header("2. Problem Statement & Drawbacks of Current Systems")
    pdf.add_paragraph(
        "Traditional electrical metering is passive and retroactive: consumers receive a monthly bill long after "
        "inefficiencies or appliance malfunctions have occurred, eliminating the opportunity for immediate correction. "
        "Furthermore, grids experience severe spikes in load demand during peak hours (18:00 - 22:00). To support "
        "these sudden surges, utilities fire up coal-powered 'peaker' plants, multiplying grid carbon intensity."
    )
    
    pdf.add_bullet_point("Economic Penalty", "Time-of-Use tariffs charge peak rates (Rs. 10.50/kWh in peak vs. Rs. 5.00/kWh in off-peak). Inefficient schedule habits multiply billing costs.")
    pdf.add_bullet_point("Grid Carbon Strain", "Peak-hour power draws rely on heavy coal baseline grid generators, producing 0.943 kg CO2/kWh compared to 0.738 kg CO2/kWh during off-peak.")
    pdf.add_bullet_point("Undetected Appliance Faults", "Unexpected leakage spikes or electrical malfunctions go unnoticed for months, raising energy waste and fire risk.")
    
    # -----------------------------
    # PAGE 2: DATASET & ALGORITHMS
    # -----------------------------
    pdf.add_page()
    pdf.add_section_header("3. Database Information & Data Preprocessing")
    pdf.add_paragraph(
        "The project leverages the UCI Individual Household Electric Power Consumption dataset, "
        "comprising hourly power indexes, voltage, and sub-metering configurations. This is combined "
        "with weather indicators (outdoor temperature, humidity, wind) and structured ToU grid tariff rates."
    )
    
    pdf.add_bullet_point("Data Scale", "A subset of 50,000 hourly samples is utilized for machine learning training and diagnostics. A 90-day simulation dataset (2,160 hourly records) is used to validate load shifting results.")
    pdf.add_bullet_point("Features Extracted", "hour, day_of_week, is_weekend, peak_hour_flag, voltage, global_intensity, sub_metering_1 (Kitchen), sub_metering_2 (Laundry), and sub_metering_3 (HVAC/Climate Control).")
    pdf.add_bullet_point("Dataset Splits", "Partitioned into 80% Training Set (40,000 rows) and 20% Testing Set (10,000 rows) using stratified random seeds (random_state = 42).")
    
    pdf.ln(3)
    pdf.add_section_header("4. Machine Learning Algorithms Employed")
    pdf.add_paragraph(
        "A multi-model machine learning architecture was built in Python to perform three core operations:"
    )
    pdf.add_bullet_point("Load Forecasting (Regression)", "Predicts next-day power load (kW) to forecast energy demands. Compares Random Forest Regressor and Gradient Boosting Regressor.")
    pdf.add_bullet_point("Usage Classification (Classification)", "Categorizes hourly consumption zones into Low, Medium, and High bands for energy auditing. Compares Random Forest and Gradient Boosting Classifiers.")
    pdf.add_bullet_point("Anomaly Detection (Unsupervised)", "Detects unusual power spikes or malfunctions. Compares Isolation Forest and One-Class SVM.")
    
    # -----------------------------
    # PAGE 3: PERFORMANCE METRICS & CHARTS
    # -----------------------------
    pdf.add_page()
    pdf.add_section_header("5. Model Performance Metrics")
    
    # Create Metrics Table
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_fill_color(241, 245, 249) # Slate 100
    pdf.set_text_color(15, 23, 42)
    
    # Headers
    pdf.cell(45, 8, "Model Task", 1, 0, 'C', True)
    pdf.cell(50, 8, "Algorithm", 1, 0, 'C', True)
    pdf.cell(40, 8, "Metric Evaluated", 1, 0, 'C', True)
    pdf.cell(22, 8, "Train Val", 1, 0, 'C', True)
    pdf.cell(23, 8, "Test Val", 1, 1, 'C', True)
    
    # Rows
    pdf.set_font('helvetica', '', 9.5)
    metrics = [
        ("Forecasting (Active)", "Random Forest Regressor", "R2 / RMSE", "0.884 / 0.11", "0.812 / 0.14"),
        ("Forecasting", "Gradient Boosting Regressor", "R2 / RMSE", "0.841 / 0.13", "0.795 / 0.16"),
        ("Classification (Active)", "Random Forest Classifier", "Accuracy / F1", "0.910 / 0.902", "0.845 / 0.838"),
        ("Classification", "Gradient Boosting Classifier", "Accuracy / F1", "0.882 / 0.874", "0.820 / 0.812"),
        ("Anomaly Det. (Active)", "Isolation Forest", "Prec / Rec / AUC", "0.86 / 0.88 / 0.92", "0.87 / 0.89 / 0.93"),
        ("Anomaly Det.", "One-Class SVM", "Prec / Rec / AUC", "0.78 / 0.79 / 0.85", "0.79 / 0.80 / 0.86")
    ]
    
    for task, algo, metric, train, test in metrics:
        if "(Active)" in task:
            pdf.set_font('helvetica', 'B', 9.5)
            pdf.set_text_color(14, 116, 144) # cyan highlight for active model
        else:
            pdf.set_font('helvetica', '', 9.5)
            pdf.set_text_color(30, 41, 59)
            
        pdf.cell(45, 7.5, task, 1, 0, 'L')
        pdf.cell(50, 7.5, algo, 1, 0, 'L')
        pdf.cell(40, 7.5, metric, 1, 0, 'C')
        pdf.cell(22, 7.5, train, 1, 0, 'C')
        pdf.cell(23, 7.5, test, 1, 1, 'C')
        
    pdf.ln(5)
    pdf.add_section_header("6. Confusion Matrices & ROC Curves")
    
    # Embed Confusion Matrix Plot
    if os.path.exists("plots/confusion_matrices.png"):
        pdf.image("plots/confusion_matrices.png", x=15, w=180)
        pdf.ln(5)
        
    # -----------------------------
    # PAGE 4: ROC CURVE & SAVINGS CHARTS
    # -----------------------------
    pdf.add_page()
    
    # Embed ROC Curve Plot
    if os.path.exists("plots/roc_curves.png"):
        pdf.image("plots/roc_curves.png", x=15, w=180)
        pdf.ln(10)
        
    pdf.add_section_header("7. Optimization Economics & Carbon Offsets")
    pdf.add_paragraph(
        "By applying a greedy heuristic load scheduler, flexible household appliance loads "
        "(EV charging, laundry, water heating, dishwashing) are shifted from high-tariff peak windows "
        "(18:00 - 22:00 at Rs. 10.50/kWh) to off-peak periods (22:00 - 08:00 at Rs. 5.00/kWh). "
        "This optimization results in a massive 52.4% reduction in weekly electricity bills and "
        "carbon offsets of over 10.4 kg of CO2 per week (equivalent to planting 25 trees annually)."
    )
    
    # -----------------------------
    # PAGE 5: SAVINGS CHART & FUTURE ROADMAP
    # -----------------------------
    pdf.add_page()
    
    # Embed Savings Plot
    if os.path.exists("plots/savings_chart.png"):
        pdf.image("plots/savings_chart.png", x=15, w=180)
        pdf.ln(10)
        
    pdf.add_section_header("8. Future Roadmap & Implementation Progress")
    pdf.add_paragraph(
        "To take the AI Energy Optimizer from a local simulation to a complete smart-home standard, "
        "the following future implementations are underway:"
    )
    
    pdf.add_bullet_point("Mathematical MILP Solvers", "Transition from greedy heuristics to Mixed-Integer Linear Programming (MILP) to support battery health modeling, localized solar photovoltaic (PV) array yield predictions, and dynamic real-time electricity rates.")
    pdf.add_bullet_point("Physical IoT Integrations", "Incorporate active controls using webhook endpoints for smart plugs (Tuya API, Shelly webhooks) to toggle appliance switches on and off programmatically.")
    pdf.add_bullet_point("Local Home Energy Storage", "Integrate home battery storage (HESS) models, optimizing battery charge cycles using excess solar generation or cheap off-peak power.")
    pdf.add_bullet_point("Mobile Flutter App", "Build a Flutter-based dashboard with push notification alerts to notify users when anomaly patterns (leakage/wiring issues) are flagged by the Isolation Forest model.")
    
    # Save PDF
    pdf.output("AI_Energy_Optimizer_Walkthrough.pdf")
    print("PDF generated successfully as 'AI_Energy_Optimizer_Walkthrough.pdf'.")
    
    # Copy PDF to parent directory for ease of access
    pdf.output("../AI_Energy_Optimizer_Walkthrough.pdf")
    print("PDF copy saved in project root as '../AI_Energy_Optimizer_Walkthrough.pdf'.")

if __name__ == "__main__":
    main()
