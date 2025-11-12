#!/usr/bin/env python3
"""
Test the register() method with pandas DataFrame and PyArrow Table
"""

import sys
import os

# Add the parent directory to Python path to use local package source
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckrun
import pandas as pd
import pyarrow as pa


def test_register_pandas():
    """Test registering a pandas DataFrame"""
    print("\n" + "=" * 60)
    print("TEST 1: Register Pandas DataFrame")
    print("=" * 60)
    
    try:
        # Create a simple pandas DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 40, 45],
            'city': ['New York', 'London', 'Paris', 'Tokyo', 'Sydney']
        })
        
        print(f"Created pandas DataFrame with {len(df)} rows")
        print(df)
        
        # Connect to duckrun (no authentication needed for in-memory test)
        print("\nConnecting to DuckDB (in-memory)...")
        con = duckrun.Duckrun(
            workspace_id="test",
            lakehouse_id="test.lakehouse",
            schema="test",
            token_only=True
        )
        
        # Register the DataFrame
        print("\nRegistering DataFrame as 'people'...")
        con.register('people', df)
        
        # Test 1: Simple SELECT
        print("\n--- Test 1a: SELECT * FROM people ---")
        result = con.sql("SELECT * FROM people")
        result.show()
        
        # Test 2: Filtering
        print("\n--- Test 1b: Filter age > 30 ---")
        result = con.sql("SELECT * FROM people WHERE age > 30")
        result.show()
        
        # Test 3: Aggregation
        print("\n--- Test 1c: Average age by city ---")
        result = con.sql("SELECT city, AVG(age) as avg_age FROM people GROUP BY city ORDER BY avg_age DESC")
        result.show()
        
        # Test 4: Join with another DataFrame
        print("\n--- Test 1d: Join with another table ---")
        df2 = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'salary': [75000, 85000, 95000]
        })
        con.register('salaries', df2)
        
        result = con.sql("""
            SELECT p.name, p.age, p.city, s.salary
            FROM people p
            INNER JOIN salaries s ON p.name = s.name
            ORDER BY s.salary DESC
        """)
        result.show()
        
        con.close()
        print("\n✅ Pandas DataFrame test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Pandas DataFrame test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_register_arrow():
    """Test registering a PyArrow Table"""
    print("\n" + "=" * 60)
    print("TEST 2: Register PyArrow Table")
    print("=" * 60)
    
    try:
        # Create a PyArrow Table
        data = {
            'product_id': [101, 102, 103, 104, 105],
            'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Webcam'],
            'price': [999.99, 29.99, 79.99, 299.99, 89.99],
            'stock': [50, 200, 150, 75, 120]
        }
        arrow_table = pa.table(data)
        
        print(f"Created PyArrow Table with {len(arrow_table)} rows")
        print(arrow_table)
        
        # Connect to duckrun (no authentication needed for in-memory test)
        print("\nConnecting to DuckDB (in-memory)...")
        con = duckrun.Duckrun(
            workspace_id="test",
            lakehouse_id="test.lakehouse",
            schema="test",
            token_only=True
        )
        
        # Register the Arrow Table
        print("\nRegistering PyArrow Table as 'products'...")
        con.register('products', arrow_table)
        
        # Test 1: Simple SELECT
        print("\n--- Test 2a: SELECT * FROM products ---")
        result = con.sql("SELECT * FROM products")
        result.show()
        
        # Test 2: Filtering
        print("\n--- Test 2b: Filter price > 100 ---")
        result = con.sql("SELECT * FROM products WHERE price > 100 ORDER BY price DESC")
        result.show()
        
        # Test 3: Aggregation
        print("\n--- Test 2c: Total stock value ---")
        result = con.sql("""
            SELECT 
                COUNT(*) as product_count,
                SUM(stock) as total_units,
                SUM(price * stock) as total_value,
                AVG(price) as avg_price
            FROM products
        """)
        result.show()
        
        # Test 4: Expensive products
        print("\n--- Test 2d: Products over $100 ---")
        result = con.sql("""
            SELECT product_name, price, stock, (price * stock) as inventory_value
            FROM products
            WHERE price > 100
            ORDER BY inventory_value DESC
        """)
        result.show()
        
        con.close()
        print("\n✅ PyArrow Table test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ PyArrow Table test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mixed_sources():
    """Test using registered tables alongside other data sources"""
    print("\n" + "=" * 60)
    print("TEST 3: Mixed Data Sources (Pandas + Arrow + CSV)")
    print("=" * 60)
    
    try:
        # Connect to duckrun
        print("Connecting to DuckDB (in-memory)...")
        con = duckrun.Duckrun(
            workspace_id="test",
            lakehouse_id="test.lakehouse",
            schema="test",
            token_only=True
        )
        
        # Register pandas DataFrame
        customers_df = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003'],
            'customer_name': ['TechCorp', 'DataInc', 'CloudSys'],
            'country': ['USA', 'UK', 'Canada']
        })
        con.register('customers', customers_df)
        print(f"Registered pandas DataFrame 'customers' with {len(customers_df)} rows")
        
        # Register PyArrow Table
        orders_data = {
            'order_id': [1, 2, 3, 4, 5],
            'customer_id': ['C001', 'C002', 'C001', 'C003', 'C002'],
            'order_amount': [15000, 25000, 8000, 12000, 18000],
            'order_date': ['2024-01-15', '2024-01-20', '2024-02-01', '2024-02-10', '2024-02-15']
        }
        orders_table = pa.table(orders_data)
        con.register('orders', orders_table)
        print(f"Registered PyArrow Table 'orders' with {len(orders_table)} rows")
        
        # Test join across both sources
        print("\n--- Test 3a: Join pandas and arrow tables ---")
        result = con.sql("""
            SELECT 
                c.customer_name,
                c.country,
                o.order_id,
                o.order_amount,
                o.order_date
            FROM customers c
            INNER JOIN orders o ON c.customer_id = o.customer_id
            ORDER BY o.order_date, o.order_id
        """)
        result.show()
        
        # Test aggregation
        print("\n--- Test 3b: Customer order summary ---")
        result = con.sql("""
            SELECT 
                c.customer_name,
                c.country,
                COUNT(o.order_id) as total_orders,
                SUM(o.order_amount) as total_revenue,
                AVG(o.order_amount) as avg_order_value
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_name, c.country
            ORDER BY total_revenue DESC
        """)
        result.show()
        
        con.close()
        print("\n✅ Mixed sources test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Mixed sources test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 DUCKRUN REGISTER() METHOD TESTS")
    print("=" * 80)
    
    # Run all tests
    results = []
    
    results.append(("Pandas DataFrame", test_register_pandas()))
    results.append(("PyArrow Table", test_register_arrow()))
    results.append(("Mixed Sources", test_mixed_sources()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 80)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED")
        sys.exit(1)
