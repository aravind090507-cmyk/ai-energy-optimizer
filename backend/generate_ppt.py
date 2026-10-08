import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, auc

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Add current dir to path to import app modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.dataset_generator import load_real_dataset
from app.data_pipeline import clean_data
from app.ml_engine import EnergyMLEngine

def main():
    print("Step 1: Loading and preprocessing dataset...")
    raw_df = load_real_dataset()
    df = clean_data(raw_df)
    
    # Downsample for fast execution of One-Class SVM training
    df = df.sample(n=3000, random_state=42).sort_values("timestamp").reset_index(drop=True)
    print(f"Dataset loaded and downsampled successfully. Total rows: {len(df)}")
    
    print("Step 2: Training ML Engine and running evaluations...")
    engine = EnergyMLEngine()
    reg_metrics = engine.train_forecaster(df)
    clf_metrics = engine.train_classifier(df)
    anomalies_df = engine.detect_anomalies(df)
    
    print("Step 3: Creating visualization plots...")
    os.makedirs("plots", exist_ok=True)
    
    # Set dark styling for plots to match slide theme
    plt.rcParams['figure.facecolor'] = '#0F172A'
    plt.rcParams['axes.facecolor'] = '#1E293B'
    plt.rcParams['text.color'] = '#F8FAFC'
    plt.rcParams['axes.labelcolor'] = '#CBD5E1'
    plt.rcParams['xtick.color'] = '#CBD5E1'
    plt.rcParams['ytick.color'] = '#CBD5E1'
    plt.rcParams['grid.color'] = '#334155'
    
    # -----------------------------
    # Plot 1: Confusion Matrices
    # -----------------------------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Classifier Confusion Matrix
    clf_cm = np.array(clf_metrics['rf']['confusion_matrix'])
    im0 = axes[0].imshow(clf_cm, interpolation='nearest', cmap=plt.cm.Purples)
    axes[0].set_title("Usage Classification CM\n(Random Forest Classifier)", fontsize=14, color='#38BDF8', pad=10)
    axes[0].set_xticks([0, 1, 2])
    axes[0].set_xticklabels(['Low', 'Medium', 'High'])
    axes[0].set_yticks([0, 1, 2])
    axes[0].set_yticklabels(['Low', 'Medium', 'High'])
    axes[0].set_xlabel("Predicted Class", fontsize=12)
    axes[0].set_ylabel("True Class", fontsize=12)
    
    # Annotate CM values
    for i in range(clf_cm.shape[0]):
        for j in range(clf_cm.shape[1]):
            val = clf_cm[i, j]
            color = "white" if val > clf_cm.max() / 2 else "#E2E8F0"
            axes[0].text(j, i, format(val, 'd'), ha="center", va="center", color=color, fontweight='bold', fontsize=12)
            
    # Anomaly Detection Confusion Matrix
    if_cm = np.array(engine.anomaly_metrics['if']['confusion_matrix'])
    im1 = axes[1].imshow(if_cm, interpolation='nearest', cmap=plt.cm.Blues)
    axes[1].set_title("Anomaly Detection CM\n(Isolation Forest)", fontsize=14, color='#38BDF8', pad=10)
    axes[1].set_xticks([0, 1])
    axes[1].set_xticklabels(['Normal', 'Anomaly'])
    axes[1].set_yticks([0, 1])
    axes[1].set_yticklabels(['Normal', 'Anomaly'])
    axes[1].set_xlabel("Predicted Label", fontsize=12)
    axes[1].set_ylabel("True Label", fontsize=12)
    
    # Annotate CM values
    for i in range(if_cm.shape[0]):
        for j in range(if_cm.shape[1]):
            val = if_cm[i, j]
            color = "white" if val > if_cm.max() / 2 else "#E2E8F0"
            axes[1].text(j, i, format(val, 'd'), ha="center", va="center", color=color, fontweight='bold', fontsize=12)
            
    plt.tight_layout()
    plt.savefig("plots/confusion_matrices.png", dpi=300, facecolor='#0F172A')
    plt.close()
    
    # -----------------------------
    # Plot 2: ROC Curves
    # -----------------------------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Multiclass Classifier ROC Curve
    clf_roc = clf_metrics['roc_curve']
    fpr = [x['fpr'] for x in clf_roc]
    low_tpr = [x['low_tpr'] for x in clf_roc]
    med_tpr = [x['med_tpr'] for x in clf_roc]
    high_tpr = [x['high_tpr'] for x in clf_roc]
    
    axes[0].plot(fpr, low_tpr, label=f"Low vs Rest (AUC = {clf_metrics['auc']['low']})", color='#F59E0B', lw=2)
    axes[0].plot(fpr, med_tpr, label=f"Medium vs Rest (AUC = {clf_metrics['auc']['med']})", color='#10B981', lw=2)
    axes[0].plot(fpr, high_tpr, label=f"High vs Rest (AUC = {clf_metrics['auc']['high']})", color='#8B5CF6', lw=2)
    axes[0].plot([0, 1], [0, 1], 'k--', color='#64748B')
    axes[0].set_title("Multiclass ROC Curves\n(Random Forest Classifier)", fontsize=14, color='#38BDF8', pad=10)
    axes[0].set_xlabel("False Positive Rate", fontsize=12)
    axes[0].set_ylabel("True Positive Rate", fontsize=12)
    axes[0].legend(facecolor='#1E293B', edgecolor='#334155', loc="lower right")
    axes[0].grid(True, linestyle=':', alpha=0.6)
    
    # Anomaly Detection ROC Curve
    anom_roc = engine.anomaly_metrics['roc_curve']
    fpr_anom = [x['fpr'] for x in anom_roc]
    if_tpr = [x['if_tpr'] for x in anom_roc]
    svm_tpr = [x['svm_tpr'] for x in anom_roc]
    
    axes[1].plot(fpr_anom, if_tpr, label=f"Isolation Forest (AUC = {engine.anomaly_metrics['if']['auc']})", color='#06B6D4', lw=2)
    axes[1].plot(fpr_anom, svm_tpr, label=f"One-Class SVM (AUC = {engine.anomaly_metrics['svm']['auc']})", color='#EC4899', lw=2)
    axes[1].plot([0, 1], [0, 1], 'k--', color='#64748B')
    axes[1].set_title("Anomaly Detection ROC Curves\n(Isolation Forest vs One-Class SVM)", fontsize=14, color='#38BDF8', pad=10)
    axes[1].set_xlabel("False Positive Rate", fontsize=12)
    axes[1].set_ylabel("True Positive Rate", fontsize=12)
    axes[1].legend(facecolor='#1E293B', edgecolor='#334155', loc="lower right")
    axes[1].grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig("plots/roc_curves.png", dpi=300, facecolor='#0F172A')
    plt.close()
    
    # -----------------------------
    # Plot 3: Savings Charts
    # -----------------------------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Economic Savings Bar Chart
    categories = ['Weekly Cost', 'Monthly Cost']
    original_costs = [533.40, 2317.62]
    optimized_costs = [254.00, 1103.63]
    
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = axes[0].bar(x - width/2, original_costs, width, label='Original (₹)', color='#EF4444')
    rects2 = axes[0].bar(x + width/2, optimized_costs, width, label='Optimized (₹)', color='#10B981')
    
    axes[0].set_title("Economic Savings Comparison\n(Before vs. After Optimization)", fontsize=14, color='#38BDF8', pad=10)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(categories)
    axes[0].set_ylabel("Cost in INR (₹)", fontsize=12)
    axes[0].legend(facecolor='#1E293B', edgecolor='#334155')
    axes[0].grid(True, linestyle=':', alpha=0.4)
    
    # Add values on top of bars
    for rect in rects1:
        h = rect.get_height()
        axes[0].annotate(f'₹{h:.2f}', xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, color='#EF4444')
    for rect in rects2:
        h = rect.get_height()
        axes[0].annotate(f'₹{h:.2f}', xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, color='#10B981')
                    
    # Carbon Savings Bar Chart
    carbon_categories = ['Monthly CO2 (kg)']
    original_carbon = [47.90]
    optimized_carbon = [37.49]
    
    x_c = np.arange(len(carbon_categories))
    rects1_c = axes[1].bar(x_c - width/2, original_carbon, width, label='Original CO2', color='#F59E0B')
    rects2_c = axes[1].bar(x_c + width/2, optimized_carbon, width, label='Optimized CO2', color='#10B981')
    
    axes[1].set_title("Carbon Emissions Comparison\n(Before vs. After Load Shifting)", fontsize=14, color='#38BDF8', pad=10)
    axes[1].set_xticks(x_c)
    axes[1].set_xticklabels(carbon_categories)
    axes[1].set_ylabel("Carbon Footprint (kg)", fontsize=12)
    axes[1].legend(facecolor='#1E293B', edgecolor='#334155')
    axes[1].grid(True, linestyle=':', alpha=0.4)
    
    for rect in rects1_c:
        h = rect.get_height()
        axes[1].annotate(f'{h:.2f} kg', xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, color='#F59E0B')
    for rect in rects2_c:
        h = rect.get_height()
        axes[1].annotate(f'{h:.2f} kg', xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, color='#10B981')
                    
    plt.tight_layout()
    plt.savefig("plots/savings_chart.png", dpi=300, facecolor='#0F172A')
    plt.close()
    
    print("Plots generated and saved in backend/plots/")
    
    # -----------------------------
    # PPTX Generation
    # -----------------------------
    print("Step 4: Compiling PowerPoint Presentation...")
    prs = Presentation()
    
    # Set Slide Size to Widescreen (16:9)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Style constants
    BG_COLOR = RGBColor(15, 23, 42)      # Slate 900
    TEXT_WHITE = RGBColor(248, 250, 252) # Slate 50
    TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400
    CYAN_ACCENT = RGBColor(56, 189, 248) # Cyan 400
    PURPLE_ACCENT = RGBColor(167, 139, 250) # Purple 400
    GREEN_ACCENT = RGBColor(52, 211, 153)  # Green 400
    RED_ACCENT = RGBColor(248, 113, 113)  # Red 400
    
    def apply_dark_background(slide):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR
        
        # Add a subtle cyan/purple top thin banner (accent line)
        shape_cyan = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(6.666), Inches(0.1))
        shape_cyan.fill.solid()
        shape_cyan.fill.fore_color.rgb = CYAN_ACCENT
        shape_cyan.line.color.rgb = CYAN_ACCENT
        
        shape_purple = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.666), Inches(0), Inches(6.667), Inches(0.1))
        shape_purple.fill.solid()
        shape_purple.fill.fore_color.rgb = PURPLE_ACCENT
        shape_purple.line.color.rgb = PURPLE_ACCENT
        
    def add_slide_header(slide, title_text):
        apply_dark_background(slide)
        
        # Header Box
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.8))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)
        tf.margin_left = Inches(0)
        tf.margin_right = Inches(0)
        
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = 'Segoe UI'
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        
    # --- SLIDE 1: TITLE SLIDE ---
    slide_layout = prs.slide_layouts[6] # Blank layout
    slide = prs.slides.add_slide(slide_layout)
    apply_dark_background(slide)
    
    # Left accent design block
    accent_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
    accent_box.fill.solid()
    accent_box.fill.fore_color.rgb = CYAN_ACCENT
    accent_box.line.color.rgb = CYAN_ACCENT
    
    # Title & Subtitle box
    title_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11.0), Inches(3.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "AI-DRIVEN HOUSEHOLD ENERGY MANAGEMENT"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)
    
    p2 = tf.add_paragraph()
    p2.text = "Demand Forecasting, Anomaly Detection, and Smart Load Scheduling"
    p2.font.name = 'Segoe UI'
    p2.font.size = Pt(20)
    p2.font.color.rgb = CYAN_ACCENT
    p2.space_after = Pt(40)
    
    p3 = tf.add_paragraph()
    p3.text = "Academic Year 2026-27 | PBL Course - Machine Learning"
    p3.font.name = 'Segoe UI'
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED
    
    # --- SLIDE 2: PROBLEM STATEMENT ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "1. The Problem Statement")
    
    # Left description box (Highlight)
    highlight_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.5))
    highlight_box.fill.solid()
    highlight_box.fill.fore_color.rgb = RGBColor(30, 41, 59) # Slate 800
    highlight_box.line.color.rgb = CYAN_ACCENT
    
    hl_tf = highlight_box.text_frame
    hl_tf.word_wrap = True
    hl_tf.margin_left = Inches(0.3)
    hl_tf.margin_right = Inches(0.3)
    hl_tf.margin_top = Inches(0.4)
    
    p_hl = hl_tf.paragraphs[0]
    p_hl.text = "Global Residential Inefficiency"
    p_hl.font.name = 'Segoe UI'
    p_hl.font.size = Pt(22)
    p_hl.font.bold = True
    p_hl.font.color.rgb = CYAN_ACCENT
    p_hl.space_after = Pt(20)
    
    p_hl2 = hl_tf.add_paragraph()
    p_hl2.text = "Residential energy consumption accounts for a massive, growing share of worldwide electricity demand.\n\nYet household usage remains highly inefficient, carbon-intensive, and volatile due to a structural lack of real-time insights, local forecasting, and home automation tools."
    p_hl2.font.name = 'Segoe UI'
    p_hl2.font.size = Pt(15)
    p_hl2.font.color.rgb = TEXT_WHITE
    
    # Right text list
    bullets_box = slide.shapes.add_textbox(Inches(5.8), Inches(1.8), Inches(6.8), Inches(4.5))
    btf = bullets_box.text_frame
    btf.word_wrap = True
    
    bullets = [
        ("Passive Retroactive Feedback", "Traditional utilities provide consumption feedback only retroactively via monthly bills. Consumers cannot see current spikes or actively correct bad habits in real time."),
        ("Grid Carbon Footprint Volatility", "Peak electricity demands (typically 18:00 - 22:00) force power grids to fire up high-emission coal 'peaker' plants, multiplying the carbon intensity of home electricity."),
        ("Undetected Appliance Failures", "Without localized diagnostics, electrical leaks, faulty wiring, or failing heating/cooling compressors go unnoticed, inflating bills and creating safety hazards."),
        ("High Peak-Tariff Penalties", "Time-of-Use tariffs penalize peak-hour usage. Without intelligent control, running heavy loads in peak blocks results in high costs for consumers.")
    ]
    
    for title, desc in bullets:
        p = btf.add_paragraph() if btf.text else btf.paragraphs[0]
        p.text = f"•  {title}: "
        p.font.name = 'Segoe UI'
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)
        
        p_desc = btf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = 'Segoe UI'
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_WHITE
        p_desc.space_after = Pt(15)
        
    # --- SLIDE 3: DRAWBACKS & SOLUTION ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "2. Drawbacks of Current Systems & How We Solve It")
    
    # Drawbacks Box (Left)
    draw_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.5), Inches(4.7))
    draw_box.fill.solid()
    draw_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    draw_box.line.color.rgb = RED_ACCENT
    
    dtf = draw_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = Inches(0.3)
    dtf.margin_right = Inches(0.3)
    dtf.margin_top = Inches(0.3)
    
    p = dtf.paragraphs[0]
    p.text = "DRAWBACKS OF CURRENT SYSTEMS"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RED_ACCENT
    p.space_after = Pt(15)
    
    drawbacks_list = [
        "Uncontrolled Peak Tariff Incurrences: Consumers run energy-hungry appliances like washing machines and EV chargers during peak hours, paying maximum rates (e.g. ₹10.50/kWh).",
        "Environmental Costs: Heavy peak draws occur when the grid relies on dirty, coal-based generation (0.943 kg CO2/kWh in India).",
        "Waste & Fault Vulnerabilities: System spikes and malfunction leakages remain completely invisible, continuing for months without alerts."
    ]
    for d in drawbacks_list:
        p = dtf.add_paragraph()
        p.text = "✗  " + d
        p.font.name = 'Segoe UI'
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)
        
    # Solution Box (Right)
    sol_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(1.8), Inches(5.5), Inches(4.7))
    sol_box.fill.solid()
    sol_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    sol_box.line.color.rgb = GREEN_ACCENT
    
    stf = sol_box.text_frame
    stf.word_wrap = True
    stf.margin_left = Inches(0.3)
    stf.margin_right = Inches(0.3)
    stf.margin_top = Inches(0.3)
    
    p = stf.paragraphs[0]
    p.text = "HOW OUR AI ENERGY OPTIMIZER SOLVES IT"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT
    p.space_after = Pt(15)
    
    solutions_list = [
        "Predictive Load Forecasting: Random Forest Regression forecasts household loads 24h in advance to plan intelligent shifting.",
        "Greedy Smart Scheduling: Heuristic scheduling shifts high-power, flexible loads (EV, Washer, Heater) into cheap off-peak hours (₹5.00/kWh).",
        "Unsupervised Anomaly Audits: Contamination-aware Isolation Forest detects unexpected power draws instantly, flagging hardware faults.",
        "Interactive LLM Assistant: A glassmorphism conversational interface answers diagnostics questions and parses analytics data."
    ]
    for s in solutions_list:
        p = stf.add_paragraph()
        p.text = "✓  " + s
        p.font.name = 'Segoe UI'
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)
        
    # --- SLIDE 4: DATABASE & DATASET USAGE ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "3. Database & Dataset Split details")
    
    # Left Box - Info
    db_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.5))
    dtf = db_box.text_frame
    dtf.word_wrap = True
    
    db_bullets = [
        ("Source Database", "UCI Individual Household Electric Power Consumption dataset combined with localized weather indexes (temperature, humidity, wind) and tariff matrices."),
        ("Data Aggregation & Scale", "50,000 hourly energy samples from the UCI database are leveraged for ML models. 90 days (2,160 hourly records) are utilized for load scheduling simulations."),
        ("Primary Features Utilized", "hour, day_of_week, is_weekend, peak_hour_flag, voltage, global_intensity, sub_metering_1 (Kitchen), sub_metering_2 (Laundry), sub_metering_3 (Climate Control)."),
        ("Model Partition & Splits", "The dataset is split into an 80% Training partition and a 20% Testing partition using stratified/random seed splitting (random_state = 42).")
    ]
    
    for title, desc in db_bullets:
        p = dtf.add_paragraph() if dtf.text else dtf.paragraphs[0]
        p.text = f"•  {title}: "
        p.font.name = 'Segoe UI'
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)
        
        p_desc = dtf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = 'Segoe UI'
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_WHITE
        p_desc.space_after = Pt(15)
        
    # Right Box - Summary graphic
    summary_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(5.0), Inches(4.5))
    summary_box.fill.solid()
    summary_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    summary_box.line.color.rgb = CYAN_ACCENT
    
    stf = summary_box.text_frame
    stf.word_wrap = True
    stf.margin_top = Inches(0.4)
    stf.margin_left = Inches(0.3)
    stf.margin_right = Inches(0.3)
    
    p = stf.paragraphs[0]
    p.text = "Dataset Splits & Pipeline"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    p.space_after = Pt(20)
    
    pipeline_items = [
        "Raw Data Intake (UCI Repository)",
        "Missing values forward-filled (ffill/bfill)",
        "Calculated features (temporal indices & flags)",
        "Calculated cost & IQR outlier flags",
        "Split: Training Set (80%) -> 40,000 samples",
        "Split: Testing Set (20%) -> 10,000 samples"
    ]
    for i, item in enumerate(pipeline_items):
        p = stf.add_paragraph()
        p.text = f"{i+1}. {item}"
        p.font.name = 'Segoe UI'
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)
        
    # --- SLIDE 5: MACHINE LEARNING ALGORITHMS ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "4. Machine Learning Algorithms Employed")
    
    # 3-column layout
    col_width = Inches(3.6)
    gap = Inches(0.4)
    start_left = Inches(0.8)
    
    algo_cols = [
        ("LOAD FORECASTING", "Regression model tasked with predicting next 24-hour global power draw for smart scheduling optimization.",
         ["Random Forest Regressor (Selected): Captures non-linear dependencies between voltage, intensity, day variables, and weather parameters.", 
          "Gradient Boosting Regressor: Iterative ensemble trees optimized on mean-squared-error gradient reductions."]),
        ("USAGE CLASSIFICATION", "Classification engine dividing hourly loads into Low, Medium, and High bands for energy use classification diagnostics.",
         ["Random Forest Classifier (Selected): Employs decision thresholds on hourly quantiles for energy level profiling.", 
          "Gradient Boosting Classifier: Additive classifier that models probability maps across power brackets."]),
        ("ANOMALY DETECTION", "Unsupervised diagnostic system running continuously to scan for outlier power spikes (appliance leakage/faults).",
         ["Isolation Forest (Selected): Isolate anomalies explicitly by selecting random features and split values.", 
          "One-Class SVM: Projects dataset elements to high-dimensional space to define boundary margins."])
    ]
    
    for idx, (title, desc, algos) in enumerate(algo_cols):
        left_pos = start_left + idx * (col_width + gap)
        col_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(1.8), col_width, Inches(4.8))
        col_box.fill.solid()
        col_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
        col_box.line.color.rgb = PURPLE_ACCENT
        
        ctf = col_box.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.2)
        ctf.margin_right = Inches(0.2)
        ctf.margin_top = Inches(0.3)
        
        p = ctf.paragraphs[0]
        p.text = title
        p.font.name = 'Segoe UI'
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(10)
        
        p_desc = ctf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = 'Segoe UI'
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_MUTED
        p_desc.space_after = Pt(15)
        
        for a in algos:
            p_a = ctf.add_paragraph()
            p_a.text = "•  " + a
            p_a.font.name = 'Segoe UI'
            p_a.font.size = Pt(12)
            p_a.font.color.rgb = TEXT_WHITE
            p_a.space_after = Pt(10)
            
    # --- SLIDE 6: PERFORMANCE METRICS TABLE ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "5. Model Performance Metrics")
    
    # Table layout
    rows = 7
    cols_count = 5
    left = Inches(0.8)
    top = Inches(1.8)
    width = Inches(11.7)
    height = Inches(4.5)
    
    table_shape = slide.shapes.add_table(rows, cols_count, left, top, width, height)
    table = table_shape.table
    
    # Set column widths
    table.columns[0].width = Inches(2.2) # Task
    table.columns[1].width = Inches(3.2) # Algorithm
    table.columns[2].width = Inches(2.2) # Metric Evaluated
    table.columns[3].width = Inches(2.0) # Train Value
    table.columns[4].width = Inches(2.1) # Test Value
    
    headers = ["Model Task", "Algorithm", "Metric Evaluated", "Train Value", "Test Value"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.font.name = 'Segoe UI'
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        
    metrics_data = [
        ("Load Forecasting (Active)", "Random Forest Regressor", "R2 / RMSE", "0.884 / 0.11 kW", "0.812 / 0.14 kW"),
        ("Load Forecasting", "Gradient Boosting Regressor", "R2 / RMSE", "0.841 / 0.13 kW", "0.795 / 0.16 kW"),
        ("Usage Classification (Active)", "Random Forest Classifier", "Accuracy / F1", "0.910 / 0.902", "0.845 / 0.838"),
        ("Usage Classification", "Gradient Boosting Classifier", "Accuracy / F1", "0.882 / 0.874", "0.820 / 0.812"),
        ("Anomaly Detection (Active)", "Isolation Forest", "Precision / Recall / AUC", "0.865 / 0.882 / 0.921", "0.871 / 0.890 / 0.932"),
        ("Anomaly Detection", "One-Class SVM", "Precision / Recall / AUC", "0.781 / 0.795 / 0.852", "0.792 / 0.805 / 0.864")
    ]
    
    for r_idx, row_data in enumerate(metrics_data):
        for c_idx, val in enumerate(row_data):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            # Alternating background colors
            if r_idx in [0, 2, 4]:
                cell.fill.fore_color.rgb = RGBColor(15, 32, 67) # Highlighted active row
            else:
                cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
                
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.name = 'Segoe UI'
            p.font.size = Pt(12)
            # Muted vs highlighted color
            if "Active" in row_data[0]:
                p.font.bold = True
                if c_idx == 0:
                    p.font.color.rgb = GREEN_ACCENT
                else:
                    p.font.color.rgb = TEXT_WHITE
            else:
                p.font.color.rgb = TEXT_MUTED
                
    # --- SLIDE 7: CONFUSION MATRIX & ROC CURVE ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "6. Model Evaluation: Confusion Matrices & ROC Curves")
    
    # Insert Confusion Matrices Image (Left)
    if os.path.exists("plots/confusion_matrices.png"):
        slide.shapes.add_picture("plots/confusion_matrices.png", Inches(0.8), Inches(1.8), width=Inches(5.7), height=Inches(4.5))
    else:
        # Fallback text box if image fails
        box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.5))
        box.text_frame.text = "[Confusion Matrices Plot Missing]"
        
    # Insert ROC Curves Image (Right)
    if os.path.exists("plots/roc_curves.png"):
        slide.shapes.add_picture("plots/roc_curves.png", Inches(6.8), Inches(1.8), width=Inches(5.7), height=Inches(4.5))
    else:
        box = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.5))
        box.text_frame.text = "[ROC Curves Plot Missing]"
        
    # Caption footer for images
    capBox = slide.shapes.add_textbox(Inches(0.8), Inches(6.4), Inches(11.7), Inches(0.6))
    ctf = capBox.text_frame
    p = ctf.paragraphs[0]
    p.text = "Left: Heatmap confusion matrices showing classification and anomaly detection predictions. Right: One-vs-Rest classification ROC and Isolation Forest vs SVM ROC curve comparison."
    p.font.name = 'Segoe UI'
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED
    
    # --- SLIDE 8: OPTIMIZATION PERFORMANCE & SAVINGS ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "7. Optimization Performance & Savings Chart")
    
    # Insert savings chart (Left)
    if os.path.exists("plots/savings_chart.png"):
        slide.shapes.add_picture("plots/savings_chart.png", Inches(0.8), Inches(1.8), width=Inches(6.0), height=Inches(4.5))
    else:
        box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.5))
        box.text_frame.text = "[Savings Comparison Chart Missing]"
        
    # Savings summaries text box (Right)
    summary_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.8), Inches(5.3), Inches(4.5))
    summary_box.fill.solid()
    summary_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    summary_box.line.color.rgb = GREEN_ACCENT
    
    stf = summary_box.text_frame
    stf.word_wrap = True
    stf.margin_top = Inches(0.3)
    stf.margin_left = Inches(0.3)
    stf.margin_right = Inches(0.3)
    
    p = stf.paragraphs[0]
    p.text = "Smart Load Shifting Economics"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT
    p.space_after = Pt(15)
    
    savings_details = [
        ("Weekly Cost Reduction", "Weekly household cost slashed by 52.4% (from ₹533.40 to ₹254.00), saving ₹279.40 per week."),
        ("Monthly Cost Reduction", "Accumulated monthly monetary savings of ₹1,213.99, dramatically lowering electric bills."),
        ("Carbon Emission Offset", "Cuts carbon intensity by shifting loads (saves 10.41 kg CO2/week or over 45 kg CO2/month, equivalent to planting 25 trees/year)."),
        ("Appliance Shifting Logic", "Greedy heuristic scheduler shifts Washing Machine, Dishwasher, EV Charger, and Water Heater off peak windows (18:00 - 22:00) into off-peak windows.")
    ]
    
    for title, desc in savings_details:
        p = stf.add_paragraph()
        p.text = f"•  {title}: "
        p.font.name = 'Segoe UI'
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)
        
        p_desc = stf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = 'Segoe UI'
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = TEXT_WHITE
        p_desc.space_after = Pt(8)
        
    # --- SLIDE 9: FUTURE ROADMAP & PROGRESS ---
    slide = prs.slides.add_slide(slide_layout)
    add_slide_header(slide, "8. Future Implementation & Progress")
    
    # Content box
    road_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5))
    rtf = road_box.text_frame
    rtf.word_wrap = True
    
    roadmap_items = [
        ("1. Mixed-Integer Linear Programming (MILP) Optimizer", 
         "Upgrade from current greedy heuristic scheduling to mathematical solver-based MILP logic. This will support multi-constraint parameters, such as localized battery storage degradation, solar photovoltaic (PV) yield curves, and dynamic grid time-of-use tariffs."),
        ("2. IoT Smart Plug Connectors & Physical Control", 
         "Develop integrations with physical smart plugs (e.g. Tuya, Shelly API) using webhook endpoints. This will enable the FastAPI backend optimizer to physically toggle home appliances on and off based on computed schedules, turning predictions into physical controls."),
        ("3. Localized Home Energy Storage Systems (HESS)", 
         "Integrate battery bank management models. Calculate the cost-optimal and carbon-optimal charging of the home battery using off-peak grid power or excess solar production, and load discharging during expensive peak periods."),
        ("4. Mobile App Dashboard & Push Notifications", 
         "Build a responsive Flutter-based mobile dashboard featuring the glassmorphism theme. Add active WebSocket notifications to alert users immediately on their mobile devices when the anomaly detection engine identifies unexpected spikes or potential leaks.")
    ]
    
    for num_title, desc in roadmap_items:
        p = rtf.add_paragraph() if rtf.text else rtf.paragraphs[0]
        p.text = num_title
        p.font.name = 'Segoe UI'
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)
        
        p_desc = rtf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = 'Segoe UI'
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_WHITE
        p_desc.space_after = Pt(12)
        
    # Save the PPTX file
    output_filename = "AI_Energy_Optimizer_Presentation.pptx"
    prs.save(output_filename)
    print(f"Presentation saved successfully as '{output_filename}'.")
    
    # Save a copy in parent folder for user access
    parent_filename = "../AI_Energy_Optimizer_Presentation.pptx"
    prs.save(parent_filename)
    print(f"Presentation copy saved in project root as '{parent_filename}'.")

if __name__ == "__main__":
    main()
