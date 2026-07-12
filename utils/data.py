import pandas as pd
import numpy as np

def get_dummy_data() -> pd.DataFrame:
    """Generate dummy asset data for the dashboard."""
    np.random.seed(42)
    categories = ['Laptops', 'Desktops', 'Monitors', 'Peripherals']
    statuses = ['Available', 'Assigned', 'Under Maintenance', 'Retired']
    n = 100
    
    # Generate dates correctly to ensure n length
    dates1 = pd.date_range(start='2022-01-01', periods=n, freq='W')
    dates2 = pd.date_range(start='2023-01-01', periods=n, freq='10D')
    
    data = pd.DataFrame({
        'asset_id': [f"AST-{i:04d}" for i in range(1, n + 1)],
        'category': np.random.choice(categories, n),
        'status': np.random.choice(statuses, n, p=[0.4, 0.4, 0.15, 0.05]),
        'value': np.random.uniform(100, 2000, n).round(2),
        'maintenance_cost': np.random.uniform(0, 500, n).round(2),
        'purchase_date': dates1,
        'last_maintenance_date': dates2
    })
    return data
