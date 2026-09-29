import mysql.connector
from datetime import datetime

# -------------------------------------------------------------
# OOP CLASSES: Domain Models
# -------------------------------------------------------------

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: str):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type  # 'Bike', 'Car', or 'Truck'


class ParkingSpot:
    def __init__(self, spot_id: int, spot_type: str, is_occupied: bool):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.is_occupied = is_occupied


# -------------------------------------------------------------
# DATABASE MANAGER & BUSINESS LOGIC
# -------------------------------------------------------------

class ParkingLotManager:
    def __init__(self):
        # Database connection setup
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'YOUR_MYSQL_PASSWORD',  # Change this to your MySQL password
            'database': 'parking_lot_db'
        }

    def get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def display_available_spots(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT spot_id, spot_type FROM parking_spots WHERE is_occupied = FALSE")
        spots = cursor.fetchall()
        
        print("\n--- AVAILABLE PARKING SPOTS ---")
        if not spots:
            print("Sorry, the parking lot is completely full!")
        else:
            for spot_id, spot_type in spots:
                print(f"Spot ID: {spot_id} | Type: {spot_type}")
        
        cursor.close()
        conn.close()

    def park_vehicle(self, vehicle: Vehicle):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Find an available spot suitable for the vehicle
        required_type = 'Large' if vehicle.vehicle_type.lower() == 'truck' else 'Compact'
        
        cursor.execute(
            "SELECT spot_id FROM parking_spots WHERE spot_type = %s AND is_occupied = FALSE LIMIT 1",
            (required_type,)
        )
        spot = cursor.fetchone()

        if not spot:
            print(f"\nNo available spot for vehicle type: {vehicle.vehicle_type}")
            cursor.close()
            conn.close()
            return

        spot_id = spot[0]
        entry_time = datetime.now()

        try:
            # 1. Update spot status to occupied
            cursor.execute("UPDATE parking_spots SET is_occupied = TRUE WHERE spot_id = %s", (spot_id,))
            
            # 2. Issue a ticket
            cursor.execute(
                "INSERT INTO parking_tickets (license_plate, vehicle_type, spot_id, entry_time) VALUES (%s, %s, %s, %s)",
                (vehicle.license_plate, vehicle.vehicle_type, spot_id, entry_time)
            )
            conn.commit()
            
            ticket_id = cursor.lastrowid
            print("\n==========================================")
            print("        PARKING TICKET ISSUED SUCCESS      ")
            print("==========================================")
            print(f"Ticket ID     : {ticket_id}")
            print(f"Vehicle No    : {vehicle.license_plate}")
            print(f"Vehicle Type  : {vehicle.vehicle_type}")
            print(f"Assigned Spot : Spot #{spot_id}")
            print(f"Entry Time    : {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("==========================================")

        except Exception as e:
            conn.rollback()
            print(f"\nAn error occurred while parking: {e}")
        finally:
            cursor.close()
            conn.close()

    def exit_vehicle(self, ticket_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Fetch active ticket
        cursor.execute(
            "SELECT ticket_id, spot_id, entry_time FROM parking_tickets WHERE ticket_id = %s AND exit_time IS NULL",
            (ticket_id,)
        )
        ticket = cursor.fetchone()

        if not ticket:
            print(f"\nInvalid or already paid Ticket ID: {ticket_id}")
            cursor.close()
            conn.close()
            return

        ticket_id, spot_id, entry_time = ticket
        exit_time = datetime.now()

        # Calculate Fee: Flat ₹30 base fee + ₹20/hr
        duration_seconds = (exit_time - entry_time).total_seconds()
        duration_hours = max(1, int(duration_seconds // 3600) + (1 if duration_seconds % 3600 > 0 else 0))
        parking_fee = 30.0 + (duration_hours - 1) * 20.0

        try:
            # 1. Free up the parking spot
            cursor.execute("UPDATE parking_spots SET is_occupied = FALSE WHERE spot_id = %s", (spot_id,))

            # 2. Close ticket record with exit time and fee
            cursor.execute(
                "UPDATE parking_tickets SET exit_time = %s, parking_fee = %s WHERE ticket_id = %s",
                (exit_time, parking_fee, ticket_id)
            )
            conn.commit()

            print("\n==========================================")
            print("        VEHICLE EXIT & RECEIPT            ")
            print("==========================================")
            print(f"Ticket ID     : {ticket_id}")
            print(f"Freed Spot    : Spot #{spot_id}")
            print(f"Total Duration: ~{duration_hours} Hour(s)")
            print(f"Total Fee Due : ₹{parking_fee:.2f}")
            print("==========================================")

        except Exception as e:
            conn.rollback()
            print(f"\nAn error occurred during exit: {e}")
        finally:
            cursor.close()
            conn.close()


# -------------------------------------------------------------
# COMMAND LINE INTERFACE MENU
# -------------------------------------------------------------

def main():
    manager = ParkingLotManager()

    while True:
        print("\n--- PARKING LOT MANAGEMENT SYSTEM ---")
        print("1. View Available Parking Spots")
        print("2. Park a Vehicle (Generate Ticket)")
        print("3. Exit Vehicle (Calculate Fee & Unpark)")
        print("4. Exit Program")

        choice = input("Select an option (1-4): ").strip()

        if choice == '1':
            manager.display_available_spots()
        elif choice == '2':
            plate = input("Enter License Plate Number (e.g., TS09AB1234): ").strip()
            v_type = input("Enter Vehicle Type (Bike/Car/Truck): ").strip().capitalize()
            if v_type in ['Bike', 'Car', 'Truck']:
                vehicle = Vehicle(plate, v_type)
                manager.park_vehicle(vehicle)
            else:
                print("Invalid vehicle type! Please choose Bike, Car, or Truck.")
        elif choice == '3':
            try:
                t_id = int(input("Enter Ticket ID: ").strip())
                manager.exit_vehicle(t_id)
            except ValueError:
                print("Please enter a valid numeric Ticket ID.")
        elif choice == '4':
            print("\nExiting system. Thank you!")
            break
        else:
            print("Invalid option! Please select between 1 and 4.")


if __name__ == "__main__":
    main()