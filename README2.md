# Asset Management Dashboard & Reporting Module

This module provides a comprehensive, interactive dashboard and reporting system for the Asset Management project. It is built using **Streamlit** for the web interface, **Pandas** for data manipulation, and **Plotly** for rich, interactive data visualizations.

## 🎯 Contribution to the Project

The core purpose of this module is to provide decision-makers, IT managers, and data scientists with a centralized hub to monitor the lifecycle and status of all organizational assets. By transforming raw asset data into actionable insights, this module contributes to the project by:

1. **Improving Visibility**: The KPI cards immediately highlight the total number of assets and their current statuses (Available, Assigned, Under Maintenance). 
2. **Identifying Bottlenecks**: The visualizations (Pie and Bar charts) make it easy to spot imbalances, such as an over-accumulation of assets under maintenance or a lack of available inventory.
3. **Cost Tracking**: The monthly maintenance cost trend chart helps in budgeting and identifying periods of unusually high expenditure.
4. **Actionable Alerts**: The "Smart Insights" section proactively flags overdue maintenance (e.g., assets unmaintained for over 180 days), ensuring compliance and reducing the risk of sudden equipment failure.
5. **Data Export & Reporting**: Stakeholders can filter data by status and category, and easily export the customized reports to CSV for external audits or presentations .

## 📂 File Structure and Purpose

- **`app.py`**: The main entry point for the Streamlit application. It configures the multipage app and provides a welcoming landing page.
- **`pages/dashboard.py`**: The core dashboard view containing high-level KPIs, interactive Plotly charts, and the AI-driven Smart Insights section.
- **`pages/reports.py`**: A detailed data exploration page allowing users to filter the asset database, view summary statistics, and download custom CSV reports.
- **`utils/charts.py`**: A utility module containing reusable Plotly chart generator functions to keep the frontend code clean and modular.
- **`utils/data.py`**: A helper script that generates robust, randomized dummy data to ensure the dashboard can be demonstrated immediately without requiring a pre-existing database.

## 🚀 How to Run

Ensure you have the required dependencies installed:
```bash
pip install streamlit pandas plotly numpy
```

To launch the dashboard, run the following command from the root of the project:
```bash
streamlit run app.py
```

This will start a local server and open the application in your default web browser. You can navigate between the Dashboard and Reports using the sidebar.
