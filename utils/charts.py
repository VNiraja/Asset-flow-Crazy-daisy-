import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_status_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Pie chart of asset status."""
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig = px.pie(
        status_counts, 
        values='Count', 
        names='Status', 
        title='Asset Status Distribution',
        color='Status',
        color_discrete_map={
            'Available': '#2ecc71',
            'Assigned': '#3498db',
            'Under Maintenance': '#f1c40f',
            'Retired': '#e74c3c'
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_category_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of asset categories."""
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    fig = px.bar(
        category_counts, 
        x='Category', 
        y='Count', 
        title='Assets by Category',
        color='Category', 
        template='plotly_white'
    )
    return fig

def create_monthly_maintenance_cost_chart(df: pd.DataFrame) -> go.Figure:
    """Monthly maintenance cost chart."""
    df_maint = df.dropna(subset=['last_maintenance_date', 'maintenance_cost']).copy()
    df_maint['Month'] = pd.to_datetime(df_maint['last_maintenance_date']).dt.to_period('M').astype(str)
    
    monthly_costs = df_maint.groupby('Month')['maintenance_cost'].sum().reset_index()
    
    fig = px.line(
        monthly_costs, 
        x='Month', 
        y='maintenance_cost', 
        title='Monthly Maintenance Cost',
        markers=True, 
        template='plotly_white'
    )
    fig.update_layout(yaxis_title='Cost ($)', xaxis_title='Month')
    return fig
