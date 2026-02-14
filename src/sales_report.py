"""Weekly sales report generator for Bronze Tier AI Employee.

Demonstrates file-based report generation within vault constraints.
"""
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List


def generate_sample_sales_data(vault_path: Path) -> Path:
    """
    Generate sample sales data file for demonstration.

    Args:
        vault_path: Root path of the vault

    Returns:
        Path to created sales data file
    """
    data_dir = vault_path / "data"
    data_dir.mkdir(exist_ok=True)

    sales_file = data_dir / "sales-data.csv"

    # Sample data for the week
    sample_data = """Date,Product,Quantity,Revenue
2026-02-10,Widget A,15,1500.00
2026-02-10,Widget B,8,800.00
2026-02-11,Widget A,22,2200.00
2026-02-11,Widget C,5,750.00
2026-02-12,Widget B,12,1200.00
2026-02-12,Widget A,18,1800.00
2026-02-13,Widget C,9,1350.00
2026-02-13,Widget A,25,2500.00
2026-02-14,Widget B,14,1400.00
2026-02-14,Widget C,7,1050.00
"""

    sales_file.write_text(sample_data, encoding='utf-8')
    return sales_file


def parse_sales_data(sales_file: Path) -> List[Dict[str, str]]:
    """
    Parse CSV sales data file.

    Args:
        sales_file: Path to sales data CSV

    Returns:
        List of sales records as dictionaries
    """
    lines = sales_file.read_text(encoding='utf-8').strip().split('\n')
    headers = lines[0].split(',')

    records = []
    for line in lines[1:]:
        values = line.split(',')
        record = dict(zip(headers, values))
        records.append(record)

    return records


def calculate_metrics(records: List[Dict[str, str]]) -> Dict:
    """
    Calculate sales metrics from records.

    Args:
        records: List of sales records

    Returns:
        Dictionary of calculated metrics
    """
    total_revenue = sum(float(r['Revenue']) for r in records)
    total_quantity = sum(int(r['Quantity']) for r in records)

    # Revenue by product
    product_revenue = {}
    product_quantity = {}
    for record in records:
        product = record['Product']
        revenue = float(record['Revenue'])
        quantity = int(record['Quantity'])

        product_revenue[product] = product_revenue.get(product, 0) + revenue
        product_quantity[product] = product_quantity.get(product, 0) + quantity

    return {
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'product_revenue': product_revenue,
        'product_quantity': product_quantity,
        'num_transactions': len(records)
    }


def generate_report(metrics: Dict, week_start: str, week_end: str) -> str:
    """
    Generate formatted sales report.

    Args:
        metrics: Calculated metrics dictionary
        week_start: Week start date (YYYY-MM-DD)
        week_end: Week end date (YYYY-MM-DD)

    Returns:
        Formatted report as markdown string
    """
    report = f"""# Weekly Sales Report

**Report Period**: {week_start} to {week_end}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

- **Total Revenue**: ${metrics['total_revenue']:,.2f}
- **Total Units Sold**: {metrics['total_quantity']} units
- **Total Transactions**: {metrics['num_transactions']}
- **Average Transaction Value**: ${metrics['total_revenue'] / metrics['num_transactions']:,.2f}

---

## Sales by Product

"""

    # Sort products by revenue (descending)
    sorted_products = sorted(
        metrics['product_revenue'].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for product, revenue in sorted_products:
        quantity = metrics['product_quantity'][product]
        avg_price = revenue / quantity
        report += f"### {product}\n\n"
        report += f"- **Revenue**: ${revenue:,.2f}\n"
        report += f"- **Units Sold**: {quantity}\n"
        report += f"- **Average Price**: ${avg_price:,.2f}\n\n"

    report += """---

## Notes

This report was generated automatically by the Bronze Tier AI Employee system using file-based data within the vault boundary. All calculations are based on sales data stored in `data/sales-data.csv`.

**Data Source**: `data/sales-data.csv`
**Report Generator**: `src/sales_report.py`
"""

    return report


def create_weekly_sales_report(vault_path: Path) -> Path:
    """
    Main function to create weekly sales report.

    Args:
        vault_path: Root path of the vault

    Returns:
        Path to generated report file
    """
    # Generate sample data (in production, this would read existing data)
    sales_file = generate_sample_sales_data(vault_path)
    print(f"Using sales data: {sales_file}")

    # Parse data
    records = parse_sales_data(sales_file)

    # Calculate metrics
    metrics = calculate_metrics(records)

    # Determine week period
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    week_end = today.strftime('%Y-%m-%d')

    # Generate report
    report_content = generate_report(metrics, week_start, week_end)

    # Save report
    reports_dir = vault_path / "Reports"
    reports_dir.mkdir(exist_ok=True)

    report_file = reports_dir / f"weekly-sales-report-{week_end}.md"
    report_file.write_text(report_content, encoding='utf-8')

    print(f"Report generated: {report_file}")
    return report_file


if __name__ == "__main__":
    vault = Path("E:/AI_Employee_Vault")
    create_weekly_sales_report(vault)
