from flask import Flask, jsonify, request, session
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
app.secret_key = "movers"
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Connect to MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="pinchez420",
        password="Rasbazu254.",
        database="movers_transport_system"
    )

# Route for the root URL
@app.route('/')
def home():
    return "Movers Transport System API!"

# Users
@app.route('/users', methods=['GET'])
def get_users():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    try:
        db = connect_db()
        cursor = db.cursor()
        
        user_data = request.json  
        
        if user_data is None:
            print("Error: No JSON data received.")
            return jsonify({"error": "No data provided"}), 400

        query = "INSERT INTO users (Username, Password, Role) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_data['Username'], user_data['Password'], user_data['Role']))
        db.commit()

        cursor.close()
        db.close()
        return jsonify({"message": "User added successfully"}), 201
    except mysql.connector.Error as db_error:
        print(f"Database error occurred: {db_error}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


# Update user information
@app.route('/users/<int:UserID>', methods=['PUT'])
def update_user(UserID):
    db = connect_db()  
    cursor = db.cursor()
    user_data = request.json
    
    # Optional: Log the incoming user data for debugging
    print("User Data received:", user_data)

    try:
        # Check if 'Password' is provided in user_data; handle cases where it's empty
        if 'Password' in user_data and user_data['Password']:
            query = "UPDATE users SET Username = %s, Password = %s, Role = %s WHERE UserID = %s"
            params = (user_data['Username'], user_data['Password'], user_data['Role'], UserID)
        else:
            # If no password is provided, omit the password update
            query = "UPDATE users SET Username = %s, Role = %s WHERE UserID = %s"
            params = (user_data['Username'], user_data['Role'], UserID)
        
        # Log the query and parameters for debugging
        print("Executing query:", query)
        print("With parameters:", params)

        cursor.execute(query, params)
        db.commit()

        # Check if any row was actually updated
        if cursor.rowcount == 0:
            return jsonify({"message": "User not found or no changes made"}), 404

    except Exception as e:
        # Rollback in case of any errors
        db.rollback()
        
        # Log the exception for debugging
        print("Error occurred while updating user:", str(e))
        
        return jsonify({"message": "Error updating user", "error": str(e)}), 500

    finally:
        cursor.close()
        db.close()

    return jsonify({"message": "User updated successfully"}), 200


# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE UserID = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Drivers
@app.route('/drivers', methods=['GET'])
def get_drivers():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM drivers")
    drivers = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(drivers)

@app.route('/drivers', methods=['POST'])
def add_drivers():
    db = connect_db()
    cursor = db.cursor()
    drivers_data = request.json
    query = "INSERT INTO drivers (DriverName, Phone, Availability) VALUES (%s, %s, %s)"
    cursor.execute(query, (drivers_data['DriverName'], drivers_data['Phone'], drivers_data['Availability']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Driver added successfully"}), 201

@app.route('/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    try:
        data = request.get_json()
        driver_name = data.get('DriverName')
        phone = data.get('Phone')
        availability = data.get('Availability')

        conn = connect_db()  
        cursor = conn.cursor()

        # Update driver in the database
        cursor.execute(""" 
            UPDATE drivers 
            SET DriverName = %s, Phone = %s, Availability = %s 
            WHERE DriverID = %s
        """, (driver_name, phone, availability, driver_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Driver updated successfully!"}), 200

    except Exception as e:
        print(f"Error updating driver: {e}")
        return jsonify({"error": "An error occurred while updating the driver."}), 500




# Vehicles
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(vehicles)

@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    db = connect_db()
    cursor = db.cursor()
    vehicles_data = request.json
    query = "INSERT INTO vehicles (LicenseNumber, VehicleModel, Weight, status) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (vehicles_data['LicenseNumber'], vehicles_data['VehicleModel'], vehicles_data['Weight'], vehicles_data['status']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Vehicle added successfully"}), 201

@app.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    db = connect_db()
    cursor = db.cursor()
    data = request.get_json()
    
    query = """
        UPDATE vehicles 
        SET LicenseNumber = %s, VehicleModel = %s, Weight = %s, status = %s 
        WHERE VehicleID = %s
    """
    
    try:
        cursor.execute(query, (data['LicenseNumber'], data['VehicleModel'], data['Weight'], data['status'], vehicle_id))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'message': 'Vehicle not found'}), 404
        
        return jsonify({'message': 'Vehicle updated successfully'})
    except Exception as e:
        db.rollback()  
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()


# Customers
@app.route('/customers', methods=['GET'])
def get_customers():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    # Selecting only the required columns
    cursor.execute("SELECT CustomersID, CustomerName, Phone, Location FROM customers")
    customers = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(customers)


@app.route('/customers', methods=['POST'])
def add_customers():
    db = connect_db()
    cursor = db.cursor()
    customers_data = request.json
    query = "INSERT INTO customers (CustomerName, Phone, Location) VALUES (%s, %s, %s)"
    cursor.execute(query, (customers_data['CustomerName'], customers_data['Phone'], customers_data['Location']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Customer added successfully"}), 201

@app.route('/delete_customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM customers WHERE CustomersID = %s", (customer_id,))
        connection.commit()
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"message": "Error deleting customer", "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# Dispatchers
@app.route('/dispatchers', methods=['GET'])
def get_dispatchers():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dispatchers")
    dispatchers = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(dispatchers)

@app.route('/dispatchers', methods=['POST'])
def add_dispatchers():
    db = connect_db()
    cursor = db.cursor()
    dispatchers_data = request.json
    query = "INSERT INTO dispatchers (DispatcherName, Phone) VALUES (%s, %s)"
    cursor.execute(query, (dispatchers_data['DispatcherName'], dispatchers_data['Phone']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Dispatchers added successfully"}), 201

# Routes
@app.route('/routes', methods=['GET'])
def get_routes():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM routes")
    routes = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(routes)

@app.route('/routes', methods=['POST'])
def add_routes():
    db = connect_db()
    cursor = db.cursor()
    
    try:
        routes_data = request.json
        
        # Validate incoming data
        if not all(key in routes_data for key in ('StartLocation', 'EndLocation', 'Payments', 'RouteName')):
            return jsonify({"message": "Missing data fields!"}), 400  # Bad request if any field is missing
        
        query = "INSERT INTO routes (StartLocation, EndLocation, Payments, RouteName) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (routes_data['StartLocation'], routes_data['EndLocation'], routes_data['Payments'], routes_data['RouteName']))
        db.commit()
        
        return jsonify({"message": "Route added successfully"}), 201  # Created status
    except Exception as e:
        print(f"Error adding route: {e}")  # Log the error for debugging
        return jsonify({"message": "Failed to add route."}), 500  # Internal server error
    finally:
        cursor.close()
        db.close()

@app.route('/routes/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # SQL query to delete the route
        query = "DELETE FROM routes WHERE RouteID = %s"
        cursor.execute(query, (route_id,))
        
        # Commit the changes
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({"message": "Route deleted successfully"}), 200
        else:
            return jsonify({"message": "Route not found"}), 404
            
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({"message": str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()


# Trip Details
@app.route('/tripdetails', methods=['GET'])
def get_tripdetails():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tripdetails")
    tripdetails = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(tripdetails)


@app.route('/tripdetails', methods=['POST'])
def request_trip():
    db = connect_db()
    cursor = db.cursor()

    try:
        # Extract trip data from the request
        trip_data = request.json
        CustomerName = trip_data['CustomerName']
        StartLocation = trip_data['StartLocation']
        EndLocation = trip_data['EndLocation']
        Weight_tonnes = trip_data['Weight_tonnes']

        # Insert into tripdetails table
        query = """
            INSERT INTO tripdetails (CustomerName, StartLocation, EndLocation, Weight_tonnes)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (CustomerName, StartLocation, EndLocation, Weight_tonnes))
        db.commit()

        return jsonify({"message": "Trip requested successfully"}), 201

    except Exception as e:
        db.rollback()
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()



# Trips
@app.route('/trips', methods=['GET'])
def get_trips():
    db = connect_db()  
    cursor = db.cursor()

    try:
        search_query = request.args.get('search', '')  # Get search parameter
        
        # Prepare the SQL query to select specific columns with optional filtering
        sql_query = """
        SELECT TripID, CustomerName, RouteName, DriverName, Phone, LicenseNumber, Status, Payments 
        FROM trips
        """
        
        if search_query:
            sql_query += " WHERE CustomerName LIKE %s OR DriverName LIKE %s"
            cursor.execute(sql_query, ('%' + search_query + '%', '%' + search_query + '%'))
        else:
            cursor.execute(sql_query)

        trips = cursor.fetchall()
        trips_list = []
        for trip in trips:
            trips_list.append({
                'TripID': trip[0],
                'CustomerName': trip[1],
                'RouteName': trip[2],
                'DriverName': trip[3],
                'Phone': trip[4],
                'LicenseNumber': trip[5],
                'Status': trip[6],
                'Payments': trip[7],
            })

        return jsonify(trips_list)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        db.close()


@app.route('/add_trip', methods=['POST'])
def add_trip():
    db = connect_db()  
    cursor = db.cursor()
    
    # Get the trip data from the request
    trip_data = request.json

    try:
        # Prepare the SQL query to insert trip details
        query = """
            INSERT INTO trips (CustomerName, RouteName, DriverName, Phone, LicenseNumber, Status, Payments)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query with the data
        cursor.execute(query, (
            trip_data['CustomerName'],           
            trip_data['RouteName'],     
            trip_data['DriverName'],         
            trip_data['Phone'],        
            trip_data['LicenseNumber'],         
            trip_data['Status'],            
            trip_data['Payments']
        ))

        # Commit the changes to the database
        db.commit()

        return jsonify({"message": "Trip added successfully"}), 201

    except Exception as e:
        db.rollback()  # Rollback in case of error
        print("Error while adding trip:", e)  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close() 
        db.close()      

@app.route('/update_trip/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    db = connect_db() 
    cursor = db.cursor()

    # Get the trip data from the request
    trip_data = request.json

    try:
        # Prepare the SQL query to update trip details
        query = """
            UPDATE trips
            SET CustomerName = %s, RouteName = %s, DriverName = %s, Phone = %s,
                LicenseNumber = %s, Status = %s, Payments = %s
            WHERE TripID = %s
        """
        cursor.execute(query, (
            trip_data['CustomerName'],
            trip_data['RouteName'],
            trip_data['DriverName'],
            trip_data['Phone'],
            trip_data['LicenseNumber'],
            trip_data['Status'],
            trip_data['Payments'],
            trip_id
        ))
        db.commit()
        return jsonify(message="Trip updated successfully"), 200
    except Exception as e:
        db.rollback()
        return jsonify(message="Error updating trip: " + str(e)), 500
    finally:
        cursor.close()
        db.close()


# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Extract credentials from request
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"message": "Missing credentials!"}), 400  # Bad request if any field is missing

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Fetch user based on the username and role
        cursor.execute("SELECT * FROM users WHERE Username = %s AND Role = %s", (username, role))
        user = cursor.fetchone()

        if user:
            if user['Password'] == password:  # Check password
                session['UserID'] = user['UserID']
                return jsonify({"message": "Login successful!", "user": user}), 200  # Successful login
            else:
                return jsonify({"message": "Invalid password!"}), 401  # Password doesn't match
        else:
            return jsonify({"message": "Invalid credentials!"}), 401  # Username or role doesn't match
    except Exception as e:
        print(f"Error during login: {str(e)}")  # Log error for debugging purposes
        return jsonify({"message": "Server error occurred."}), 500  # Return 500 Internal Server Error
    finally:
        cursor.close()
        db.close()


# Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"message": "Missing credentials!"}), 400

    db = connect_db()
    cursor = db.cursor()

    try:
        # Insert user into the database with plain text password
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, role))
        db.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        print(f"Error during signup: {str(e)}")
        return jsonify({"message": "Error during signup"}), 500
    finally:
        cursor.close()
        db.close()

def get_logged_in_DriverID():
    
    return session.get('DriverID')  

# Unified API endpoint to fetch all data
@app.route('/all_data', methods=['GET'])
def get_all_data():
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # Fetch Customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    # Fetch Drivers
    cursor.execute("SELECT * FROM drivers")
    drivers = cursor.fetchall()

    # Fetch Dispatchers
    cursor.execute("SELECT * FROM dispatchers")
    dispatchers = cursor.fetchall()

    # Fetch Vehicles
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()

    # Fetch Routes
    cursor.execute("SELECT * FROM routes")
    routes = cursor.fetchall()

    # Fetch Trip Details
    cursor.execute("SELECT * FROM tripdetails")
    tripdetails = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify({
        "customers": customers,
        "drivers": drivers,
        "dispatchers": dispatchers,
        "vehicles": vehicles,
        "routes": routes,
        "tripdetails": tripdetails
    })

def get_user_name_from_session():
    # Assuming user info is stored in the session after login
    if 'UserID' in session:
        UserID = session['UserID']
        return "Ignatius Lumosi"  
    return None

@app.route('/getUserName', methods=['GET'])
def get_user_name():
    
    user_name = get_user_name_from_session()
    if user_name:
        return jsonify({"name": user_name}), 200
    else:
        return jsonify({"error": "User not logged in"}), 401


if __name__ == "__main__":
    app.run(debug=False)
