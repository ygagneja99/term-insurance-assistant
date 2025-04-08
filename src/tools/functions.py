import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import uuid

def set_dict_factory(conn: sqlite3.Connection):
    """
    Sets the row_factory of the SQLite connection to sqlite3.Row, 
    which allows row data to be accessible by column name.
    """
    conn.row_factory = sqlite3.Row
    
def visualise_basic_plan_and_premium_lookup(results, age, term, coverage_amount, income):
    # Convert results into a DataFrame
    df = pd.DataFrame(results)
    
    # If no results, print a message and exit
    if df.empty:
        print("No results found for the given parameters.")
        return

    # Transpose the DataFrame so that column names become row labels
    df_transposed = df.transpose()

    # Create a matplotlib figure sized appropriately based on the transposed table dimensions
    rows, cols = df_transposed.shape
    fig, ax = plt.subplots(figsize=(cols * 2, rows * 0.7 + 1))
    
    # Hide axes and create the table
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df_transposed.values,
                     rowLabels=df_transposed.index,
                     loc='center',
                     cellLoc='center')
    
    # Adjust font size and scale
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2)
    
    # Apply text wrapping to riders rows
    for (row, col), cell in table._cells.items():
        if df_transposed.index[row] in ['paid_riders', 'free_riders']:
            cell._text.set_wrap(True)
            cell.set_height(cell.get_height() * 2)  # Double the height for wrapped text
    
    # Set a title with parameter details for context
    plt.title(f"Plans Found For - Age = {age} Yrs, Term = {term} Yrs, Coverage = Rs. {coverage_amount}, Income = Rs. {income}")
    plt.tight_layout()
    
    # Save the figure as an image file
    file_path = f'output_{uuid.uuid4()}.png'
    plt.savefig(file_path, format='png', dpi=150)
    plt.close(fig)
    return file_path

def visualise_get_recommended_plans_based_on_priority_factors(results, age, term, coverage_amount, income):
    # Convert results into a DataFrame
    df = pd.DataFrame(results)
    
    # If no results, print a message and exit
    if df.empty:
        print("No results found for the given parameters.")
        return

    # Transpose the DataFrame so that column names become row labels
    df_transposed = df.transpose()
    
    # Move rank row to the top by reordering index
    if 'rank' in df_transposed.index:
        new_index = ['rank'] + [idx for idx in df_transposed.index if idx != 'rank']
        df_transposed = df_transposed.reindex(new_index)

    # Create a matplotlib figure with improved width for better horizontal spacing
    rows, cols = df_transposed.shape
    fig, ax = plt.subplots(figsize=(10, rows * 0.7 + 1))  # Increased width from 8 to 10
    
    # Hide axes and create the table
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df_transposed.values,
                     rowLabels=df_transposed.index,
                     loc='center',
                     cellLoc='center',
                     colWidths=[0.4] * cols)  # Set consistent column width
    
    # Adjust font size and scale
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.3, 1.2)  # Increased horizontal scale from 1.2 to 1.3
    
    # Set better horizontal spacing by adjusting column widths and row heights
    for (row, col), cell in table._cells.items():
        # Add padding/margin to cells by adjusting width
        if col >= 0:  # Data cells
            cell.set_width(0.35)  # Set width for data columns
        
        if row == -1:  # Row label column
            cell.set_width(0.3)  # Width for row labels
            
        # Special handling for rank row and rider rows
        if row >= 0:
            if df_transposed.index[row] == 'rank':
                cell.set_height(cell.get_height() * 1.5)  # Make rank row 1.5x taller
                cell._text.set_fontsize(14)  # Increase font size for rank values
            elif df_transposed.index[row] in ['paid_riders', 'free_riders']:
                cell._text.set_wrap(True)
                cell.set_height(cell.get_height() * 2)  # Double the height for wrapped text
    
    # Set a title with parameter details for context
    plt.title(f"Top Recommended Plans Based on Priority Factors - Age = {age} Yrs, Term = {term} Yrs, Coverage = Rs. {coverage_amount}, Income = Rs. {income}")
    
    # Add more spacing around the plot
    plt.tight_layout(pad=3.0)  # Increased padding from 2.0 to 3.0
    
    # Save the figure as an image file with extra margin
    file_path = f'output_{uuid.uuid4()}.png'
    plt.savefig(file_path, format='png', dpi=150, bbox_inches='tight', pad_inches=0.5)  # Added pad_inches
    plt.close(fig)
    return file_path


###############################
# 1. BASIC PLAN & PREMIUM LOOKUP
###############################
def basic_plan_and_premium_lookup(conn: sqlite3.Connection, age: int, term: int, coverage_amount: int, income: int):
    """
    Retrieve a list of (insurer, plan, premium) records for a user 
    with given (age, term, coverage_amount, income),
    ensuring:
    - user meets min_age, max_age, min_term, max_term, min_cover, max_cover
    - required_min_income <= income
    """
    set_dict_factory(conn)
    sql = """
    SELECT 
        i.name AS insurer_name,
        t.plan_name,
        p.annual_premium,
        t.free_riders,
        t.paid_riders
    FROM premiums p
    JOIN term_plans t ON p.plan_id = t.plan_id
    JOIN insurers i ON t.insurer_id = i.insurer_id
    WHERE p.age_min <= ?
      AND p.age_max > ?
      AND p.term_min <= ?
      AND p.term_max > ?
      AND p.coverage_min <= ?
      AND p.coverage_max > ?
      AND p.required_min_income <= ?
      AND t.min_age <= ?
      AND t.max_age > ?
      AND t.min_term <= ?
      AND t.max_term > ?
      AND t.min_cover <= ?
      AND t.max_cover > ?
    """
    params = (age, age, term, term, coverage_amount, coverage_amount, income, age, age, term, term, coverage_amount, coverage_amount)
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    
    results = [dict(row) for row in rows]
    image_path = visualise_basic_plan_and_premium_lookup(results, age, term, coverage_amount, income)
    
    return results, image_path

###############################
# 7. LIST INSURERS AND METRICS
###############################
def list_insurers_and_metrics(conn: sqlite3.Connection):
    """
    Returns all insurers with their claim_settlement_ratio, amount_settlement_ratio, and complaints_volume.
    """
    set_dict_factory(conn)
    sql = """
    SELECT 
      name,
      claim_settlement_ratio,
      amount_settlement_ratio,
      complaints_volume
    FROM insurers
    """
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_recommended_plans_based_on_priority_factors(conn: sqlite3.Connection, age: int, income: int, coverage_amount: int, term: int, priority_factors: list):
    """
    Find the best recommended plans based on user's age, income, coverage needs and prioritized factors.
    Priority factors can be: "premium" (lowest price), "csr" (claim settlement ratio), 
    "asr" (amount settlement ratio), "complaints" (low complaint ratio)
    Returns a ranked list of recommended plans or empty list if no eligible plans found.
    """
    set_dict_factory(conn)
    
    # Base query to get eligible plans
    sql = """
    WITH eligible_plans AS (
        SELECT 
            i.name AS insurer_name,
            t.plan_name,
            p.annual_premium,
            i.claim_settlement_ratio,
            i.amount_settlement_ratio,
            i.complaints_volume,
            t.free_riders,
            t.paid_riders,
            ROW_NUMBER() OVER (ORDER BY
    """
    
    # Add ordering based on priority factors
    order_clauses = []
    for factor in priority_factors:
        if factor == "premium":
            order_clauses.append("p.annual_premium ASC")
        elif factor == "csr":
            order_clauses.append("i.claim_settlement_ratio DESC")
        elif factor == "asr":
            order_clauses.append("i.amount_settlement_ratio DESC")
        elif factor == "complaints":
            order_clauses.append("i.complaints_volume ASC")
            
    sql += ", ".join(order_clauses)
    
    sql += """) as rank
        FROM premiums p
        JOIN term_plans t ON p.plan_id = t.plan_id 
        JOIN insurers i ON t.insurer_id = i.insurer_id
        WHERE p.age_min <= ?
          AND p.age_max > ?
          AND p.term_min <= ?
          AND p.term_max > ?
          AND p.coverage_min <= ?
          AND p.coverage_max > ?
          AND p.required_min_income <= ?
          AND t.min_age <= ?
          AND t.max_age > ?
          AND t.min_cover <= ?
          AND t.max_cover > ?
          AND t.min_term <= ?
          AND t.max_term > ?
        LIMIT 2
    )
    SELECT * FROM eligible_plans ORDER BY rank
    """
    
    params = (age, age, term, term, coverage_amount, coverage_amount, income, age, age, coverage_amount, coverage_amount, term, term)
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    
    results = [dict(row) for row in rows]
    image_path = visualise_get_recommended_plans_based_on_priority_factors(results, age, term, coverage_amount, income)
    
    return results, image_path

def get_insurer_details(insurer_name, conn):
    """
    Fetch details of a specific insurer using approximate name matching.
    
    Args:
        insurer_name (str): Name or partial name of the insurer to look up
        conn: Database connection object
        
    Returns:
        dict: Insurer details if found, otherwise error message
    """
    # Set up dictionary factory
    set_dict_factory(conn)
    
    # Use LIKE with wildcards for fuzzy name matching
    sql = """
    SELECT 
        name,
        claim_settlement_ratio,
        amount_settlement_ratio,
        complaints_volume
    FROM insurers 
    WHERE LOWER(name) LIKE LOWER(?)
    OR LOWER(name) LIKE LOWER(?)
    OR LOWER(?) LIKE CONCAT('%', LOWER(name), '%')
    """
    
    # Create search patterns
    search_patterns = (
        f"%{insurer_name}%",  # Contains the name
        f"{insurer_name}%",   # Starts with the name
        insurer_name          # Full name is contained within
    )
    
    cursor = conn.execute(sql, search_patterns)
    results = cursor.fetchone()
    
    if not results:
        return {"error": f"No insurers found matching '{insurer_name}'"}
    
    # Row should already be a dict if set_dict_factory is used
    return dict(results)

def get_plan_details(plan_name, conn):
    """
    Fetch details of a specific insurance plan using approximate name matching.
    
    Args:
        plan_name (str): Name or partial name of the plan to look up
        conn: Database connection object
        
    Returns:
        dict: Plan details if found, otherwise error message
    """
    # Set up dictionary factory
    set_dict_factory(conn)
    
    sql = """
    SELECT 
        p.plan_name,
        i.name as insurer_name,
        i.claim_settlement_ratio,
        i.amount_settlement_ratio,
        i.complaints_volume,
        p.free_riders,
        p.paid_riders,
        p.plan_link
    FROM term_plans p
    JOIN insurers i ON p.insurer_id = i.insurer_id
    WHERE LOWER(p.plan_name) LIKE LOWER(?)
    OR LOWER(p.plan_name) LIKE LOWER(?)
    OR LOWER(?) LIKE CONCAT('%', LOWER(p.plan_name), '%')
    """
    
    # Create search patterns
    search_patterns = (
        f"%{plan_name}%",  # Contains the name
        f"{plan_name}%",   # Starts with the name
        plan_name          # Full name is contained within
    )
    
    cursor = conn.execute(sql, search_patterns)
    results = cursor.fetchone()
    
    if not results:
        return {"error": f"No plans found matching '{plan_name}'"}
    
    # Row should already be a dict if set_dict_factory is used
    return dict(results)





def execute_function(function_name, function_args):
    """
    Execute the specified function with the provided arguments.
    Returns a tuple of (result, image_path) where image_path may be None.
    """
    conn = None
    try:
        # Try to connect to database and execute real function
        conn = sqlite3.connect('data/term_insurance.db')
        
        # Map of function names to actual functions
        function_map = {
            "get_plan_details": get_plan_details,
            "get_insurer_details": get_insurer_details,
            "get_recommended_plans_based_on_priority_factors": get_recommended_plans_based_on_priority_factors,
            "list_insurers_and_metrics": list_insurers_and_metrics,
            "basic_plan_and_premium_lookup": basic_plan_and_premium_lookup
        }

        if function_name not in function_map:
            return {"error": f"Function {function_name} not implemented"}, None

        # Add conn to function arguments and execute
        args = {**function_args, "conn": conn}
        function_result = function_map[function_name](**args)
        
        # Handle the special case for basic_plan_and_premium_lookup which returns a tuple
        if function_name == "basic_plan_and_premium_lookup" or function_name == "get_recommended_plans_based_on_priority_factors":
            return function_result  # This function already returns (result, image_path)
        else:
            # For all other functions, return the result with None for image_path
            return function_result, None

    except sqlite3.Error as e:
        # Handle database errors
        print(f"Database error occurred: {str(e)}")
        return {"error": "Database error occurred"}, None
        
    except Exception as e:
        # Handle other errors
        print(f"Error executing function: {str(e)}")
        return {"error": "Error executing function"}, None
        
    finally:
        # Always close connection if it exists
        if conn:
            conn.close()