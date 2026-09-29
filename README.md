# Parking Lot Management System (Python + MySQL)

A clean, object-oriented command-line application for managing vehicle parking spots, issuing tickets, and calculating exit fees with a relational MySQL backend.

## Key Features
- **Object-Oriented Design:** Structured using core OOP concepts (`Vehicle`, `ParkingSpot`, `ParkingLotManager`).
- **Dynamic Spot Allocation:** Automatically searches and assigns free spots based on vehicle type (Compact / Large).
- **Automated Fee Calculation:** Computes hourly parking charges upon vehicle exit.
- **Data Persistence & Integrity:** Integrates with MySQL using explicit transactions (`COMMIT` and `ROLLBACK`).

## Tech Stack
- **Language:** Python 3.x
- **Database:** MySQL
- **Driver:** `mysql-connector-python`

## How to Run

1. **Setup Database:**
   Run the schema SQL script inside MySQL Workbench to build `parking_lot_db`.

2. **Install Dependencies:**
   ```bash
   pip install mysql-connector-python