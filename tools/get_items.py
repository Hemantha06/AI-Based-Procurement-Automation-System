from database import get_db_connection
import json
from datetime import datetime
from decimal import Decimal
import argparse

def serialize_value(value):
    """Convert non-serializable values to a JSON-friendly format."""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
    if isinstance(value, Decimal):
        return float(value)  # Convert decimal to float
    return value

def get_items(req_id):
    """
    Fetch product specifications based on req_id.

    Args:
        req_id (int): Requirement ID.

    Returns:
        str: JSON string of product specifications or error message.
    """
    try:
        #print(f"🔍 Fetching items for REQ_ID: {req_id}")

        # Ensure req_id is an integer before querying
        if not str(req_id).isdigit():
            return json.dumps({"status": "error", "message": f"Invalid req_id: {req_id}. Expected an integer."}, indent=2)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT ITEM_ID, REQ_ID, PROD_ID, DESCRIPTION, QUANTITY, BRAND, 
               OTHER_BRAND, HSN_CODE, REQUIRED_DATE
        FROM requirementitems WHERE REQ_ID = ?
        """
        
        cursor.execute(query, (int(req_id),))  # Convert req_id to int before executing
        data = cursor.fetchall()

        #print(f"✅ Query executed successfully. Fetched {len(data)} rows.")

        if data:
            # Convert to list of dictionaries with proper serialization
            result_list = [
                {column[0]: serialize_value(value) for column, value in zip(cursor.description, row)}
                for row in data
            ]

            return json.dumps({"status": "success", "data": result_list}, indent=2)
        else:
            return json.dumps({"status": "error", "message": f"No items found for Requirement ID {req_id}."}, indent=2)

    except ValueError as ve:
        return json.dumps({"status": "error", "message": f"Value Error: {str(ve)}"}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Database Error: {str(e)}"}, indent=2)
    finally:
        conn.close()

if __name__ == "__main__":
    # Set up argument parser to accept req_id as a command line argument
    parser = argparse.ArgumentParser(description="Fetch product specifications for a given requirement ID.")
    parser.add_argument("req_id", type=int, help="Requirement ID (REQ_ID) to fetch items for.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided req_id
    print(get_items(args.req_id))
