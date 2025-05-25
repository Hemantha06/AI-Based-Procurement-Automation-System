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

def get_quotations(req_id):
    """
    Fetch all vendor quotations submitted within the valid timeframe for a given requirement ID (REQ_ID).

    Args:
        req_id (int): Requirement ID.

    Returns:
        str: JSON string of filtered quotations, or an error message if something goes wrong.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure req_id is an integer before querying
        if not str(req_id).isdigit():
            return json.dumps({"error": f"Invalid req_id: {req_id}. Expected an integer."})

        # Fetch REQ_POSTED_ON and QUOTATION_FREEZ_TIME for the given REQ_ID
        cursor.execute("""
            SELECT REQ_POSTED_ON, QUOTATION_FREEZ_TIME
            FROM requirementdetails
            WHERE REQ_ID = ?
        """, (int(req_id),))
        req_details = cursor.fetchone()

        if not req_details:
            return json.dumps({"error": f"Requirement ID {req_id} not found."})

        req_posted_on, quotation_freez_time = req_details

        # Convert datetime values to strings
        if isinstance(req_posted_on, datetime):
            req_posted_on_str = req_posted_on.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.dumps({"error": "Invalid format for REQ_POSTED_ON."})

        if isinstance(quotation_freez_time, datetime):
            quotation_freez_time_str = quotation_freez_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.dumps({"error": "Invalid format for QUOTATION_FREEZ_TIME."})

        # Fetch all item IDs associated with the given REQ_ID
        cursor.execute("""
            SELECT DISTINCT ITEM_ID
            FROM quotations 
            WHERE REQ_ID = ?
        """, (int(req_id),))
        items = cursor.fetchall()

        if not items:
            return json.dumps({"error": f"No items found for Requirement ID {req_id}."})

        # Prepare the result to hold quotations per item
        result = {}

        for item in items:
            item_id = item[0]

            # Fetch quotations submitted within the valid timeframe
            query = """
            SELECT QUOT_ID, ITEM_ID, REQ_ID, U_ID, PRICE, UNIT_PRICE, BRAND, 
                   DELIVERY_DATE, TAX, C_GST, S_GST, I_GST, AMC, ITEM_WARRANTY
            FROM quotations 
            WHERE REQ_ID = ? AND ITEM_ID = ?
            """
            #AND DATE_CREATED BETWEEN ? AND ?
            cursor.execute(query, (int(req_id), item_id))
                                                        #, req_posted_on_str, quotation_freez_time_str
            data = cursor.fetchall()

            if data:
                item_quotations = []
                columns = [column[0] for column in cursor.description]

                for row in data:
                    row_dict = dict(zip(columns, row))

                    # Use serialize_value to handle datetime and Decimal conversion
                    for key, value in row_dict.items():
                        row_dict[key] = serialize_value(value)

                    item_quotations.append(row_dict)

                result[item_id] = item_quotations
            else:
                result[item_id] = []  # No quotations found for this item within the valid timeframe

        return json.dumps(result, indent=2)  # Return the data as a formatted JSON string

    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})  # Return error as JSON string
    finally:
        conn.close()

if __name__ == "__main__":
    # Set up argument parser to accept req_id as a command line argument
    parser = argparse.ArgumentParser(description="Fetch vendor quotations within the valid timeframe for a given requirement ID.")
    parser.add_argument("req_id", type=int, help="Requirement ID (REQ_ID) to fetch quotations for.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided req_id
    print(get_quotations(args.req_id))
