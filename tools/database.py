import pyodbc
from config import DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_DRIVER

def get_db_connection():
    conn_str = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD};Encrypt=no;TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

def fetch_requirement_details(req_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure req_id is an integer before passing it to the SQL query
        if not str(req_id).isdigit():
            raise ValueError(f"Invalid req_id: {req_id}. Expected an integer.")

        query = """
        SELECT REQ_ID, REQ_TITLE, REQ_DESC, REQ_POSTED_ON, REQ_CATEGORY, REQ_URGENCY, 
               REQ_BUDGET, REQ_DELIVERY_LOC, REQ_TAXES, REQ_PAYMENT_TERMS
        FROM requirementdetails
        WHERE REQ_ID = ?
        """
        
        cursor.execute(query, int(req_id))  # Convert req_id to int before executing
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return dict(zip([column[0] for column in cursor.description], result))
        else:
            return {"error": f"Requirement ID {req_id} not found."}

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": str(e)}

def fetch_requirement_items(req_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure req_id is an integer before querying
        if not str(req_id).isdigit():
            raise ValueError(f"Invalid req_id: {req_id}. Expected an integer.")

        query = """
        SELECT ITEM_ID, REQ_ID, PROD_ID, DESCRIPTION, QUANTITY, BRAND, 
               OTHER_BRAND, HSN_CODE, REQUIRED_DATE
        FROM requirementitems WHERE REQ_ID = ?
        """
        cursor.execute(query, int(req_id))  # Convert req_id to int before executing
        data = cursor.fetchall()
        conn.close()

        return [dict(zip([column[0] for column in cursor.description], row)) for row in data]

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": str(e)}

def fetch_quotations(req_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure req_id is an integer before querying
        if not str(req_id).isdigit():
            raise ValueError(f"Invalid req_id: {req_id}. Expected an integer.")

        query = """
        SELECT QUOT_ID, ITEM_ID, REQ_ID, U_ID, PRICE, UNIT_PRICE, BRAND, 
               DELIVERY_DATE, TAX, C_GST, S_GST, I_GST, AMC, ITEM_WARRANTY
        FROM quotations WHERE REQ_ID = ?
        """
        cursor.execute(query, int(req_id))  # Convert req_id to int before executing
        data = cursor.fetchall()
        conn.close()

        return [dict(zip([column[0] for column in cursor.description], row)) for row in data]

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": str(e)}