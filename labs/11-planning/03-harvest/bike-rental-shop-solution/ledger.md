# Ledger

## How to write here

1. Each harvester adds ONE section, with a "## <source>" heading, in a single append at the end of its run.
2. A section is bullets only. Every bullet states one observed fact and ends with a citation in parentheses: the file path, plus the sheet and cell, or the symbol or line, it came from.
3. Facts only: no recommendations, no judgement of what is missing.
4. A harvester writes no other file.

## shop-app code

- app.py defines main() as an argparse entry point with four subcommands: add-bike, rent, return, open (shop-app/app.py:7 main).
- The add-bike subcommand takes positional arguments label and frame_size (shop-app/app.py:11-13 main).
- The rent subcommand takes positional arguments label, name and phone, plus an optional --days integer defaulting to 1 (shop-app/app.py:15-19 main).
- The return subcommand takes one positional argument, label (shop-app/app.py:21-22 main).
- The open subcommand takes no arguments (shop-app/app.py:24 main).
- main() calls init_db() after parsing arguments and before dispatching the subcommand (shop-app/app.py:26-27 main).
- add-bike prints "added <label>" (shop-app/app.py:30-31 main).
- rent prints "<label> due <due date in ISO format>" (shop-app/app.py:33-34 main).
- return prints "<label> returned, late fee" followed by the fee in cents divided by 100 with two decimal places (shop-app/app.py:36-37 main).
- open prints one tab-separated line per row with label, name, phone and due_at (shop-app/app.py:38-40 main).
- DB_PATH is shop.db in the same folder as db.py (shop-app/db.py:4).
- SCHEMA_PATH is schema.sql in the same folder as db.py (shop-app/db.py:5).
- get_connection() opens a sqlite3 connection with row_factory set to sqlite3.Row (shop-app/db.py:8-11 get_connection).
- init_db() runs the contents of the schema file through executescript (shop-app/db.py:14-16 init_db).
- LATE_FEE_PER_DAY_CENTS is 400 (shop-app/fees.py:3).
- LATE_FEE_CAP_CENTS is 4000 (shop-app/fees.py:4).
- days_late() returns max((returned_at - due_at).days, 0) (shop-app/fees.py:7-8 days_late).
- late_fee_cents() returns min(days_late(due_at, returned_at) * 400, 4000), using the two named constants (shop-app/fees.py:11-13 late_fee_cents).
- add_bike() inserts a row into bikes with label and frame_size and returns the new row id (shop-app/rentals.py:7-12 add_bike).
- find_or_create_customer() returns the id of the customer with the given phone, or inserts a customer with name and phone when none matches (shop-app/rentals.py:15-25 find_or_create_customer).
- rent_bike() sets due to today plus the days argument (shop-app/rentals.py:28-30 rent_bike).
- rent_bike() calls find_or_create_customer() before it looks up the bike (shop-app/rentals.py:31 rent_bike).
- rent_bike() raises ValueError with the text "no bike <label>" when no bike has the label (shop-app/rentals.py:33-37 rent_bike).
- rent_bike() raises ValueError with the text "bike <label> is <status>" when the bike status is not "available" (shop-app/rentals.py:38-39 rent_bike).
- rent_bike() inserts a rentals row with rented_at set to today and due_at set to the due date, then sets the bike status to 'rented' (shop-app/rentals.py:40-44 rent_bike).
- rent_bike() returns the due date as a date object (shop-app/rentals.py:45 rent_bike).
- return_bike() selects the rental with returned_at IS NULL for the given bike label (shop-app/rentals.py:51-55 return_bike).
- return_bike() raises ValueError with the text "bike <label> is not rented" when no open rental is found (shop-app/rentals.py:56-57 return_bike).
- return_bike() computes the fee with late_fee_cents(due_at, today) (shop-app/rentals.py:58 return_bike).
- return_bike() writes returned_at and late_fee_cents to the rental, sets the bike status to 'available', and returns the fee (shop-app/rentals.py:59-64 return_bike).
- list_open() returns label, name, phone and due_at for rentals with returned_at IS NULL, ordered by due_at (shop-app/rentals.py:67-73 list_open).
- The setUp method in test_rent.py points db.DB_PATH at a temporary directory, calls init_db(), and adds bike CITY-01 with frame size M (shop-app/tests/test_rent.py:13-17 setUp).
- test_rent_marks_bike_rented rents CITY-01 for 2 days and asserts that list_open() returns one row (shop-app/tests/test_rent.py:22-24 test_rent_marks_bike_rented).
- test_rent_twice_fails asserts that a second rent of CITY-01 raises ValueError (shop-app/tests/test_rent.py:26-29 test_rent_twice_fails).
- test_rent_twice_fails checks only the exception type, not the message (shop-app/tests/test_rent.py:28-29 test_rent_twice_fails).
- test_rent_marks_bike_rented does not assert the due date returned by rent_bike() (shop-app/tests/test_rent.py:22-24 test_rent_marks_bike_rented).
- The two tests in test_rent.py call rent_bike() and list_open() only; neither calls return_bike() (shop-app/tests/test_rent.py:22-29 RentTests).
- No test in test_rent.py calls late_fee_cents(), days_late() or any constant from fees.py (shop-app/tests/test_rent.py:1-34 RentTests).
- test_rent.py imports only db and rentals, so app.py and its argparse commands are not imported by any test (shop-app/tests/test_rent.py:8-9).
- No test in test_rent.py exercises the "bike <label> is not rented" path of return_bike() (shop-app/tests/test_rent.py:22-29 RentTests).
- No test in test_rent.py exercises the "no bike <label>" path of rent_bike() (shop-app/tests/test_rent.py:22-29 RentTests).

## process and spreadsheet

- The process notes cover one week of rentals, 5 to 9 October 2026 (shop-sources/process-notes.md line 3).
- The process notes are recorded by Mara Huber, Shop Owner (shop-sources/process-notes.md line 3).
- The Monday step rents a city bike for three days (shop-sources/process-notes.md line 7).
- The owner writes the Monday rental into the Rentals sheet (shop-sources/process-notes.md line 7).
- The owner takes a 50 euro cash deposit at the Monday rental (shop-sources/process-notes.md line 7).
- The Monday rental step uses Excel and the cash box and takes 6 minutes (shop-sources/process-notes.md line 7).
- The Monday rental is also typed into the shop app so the bike shows as rented (shop-sources/process-notes.md line 8).
- The shop app rental entry step takes 4 minutes (shop-sources/process-notes.md line 8).
- On Tuesday the owner calls every customer whose bike is due the next day, taken from the Due column, to remind them (shop-sources/process-notes.md line 9).
- The Tuesday reminder step uses phone and Excel and takes 25 minutes (shop-sources/process-notes.md line 9).
- A bike comes back one day late (shop-sources/process-notes.md line 10).
- On Wednesday the owner reads the Late Fee column in Excel and takes the fee with the deposit refund (shop-sources/process-notes.md line 10).
- The Wednesday late fee step uses Excel and the cash box and takes 8 minutes (shop-sources/process-notes.md line 10).
- On Wednesday the owner marks the bike returned in the shop app (shop-sources/process-notes.md line 11).
- The Wednesday return step uses the shop app and takes 3 minutes (shop-sources/process-notes.md line 11).
- On Thursday the owner checks the Service sheet for bikes whose next service date has passed and pulls them off the floor by hand (shop-sources/process-notes.md line 12).
- The Thursday service check uses Excel and takes 15 minutes (shop-sources/process-notes.md line 12).
- On Friday the owner counts the week's late fees from the Rentals sheet for the owner report (shop-sources/process-notes.md line 13).
- The Friday late fee count uses Excel and takes 20 minutes (shop-sources/process-notes.md line 13).
- The notes name the reminder calls as what costs the most (shop-sources/process-notes.md line 15).
- The notes state that nothing tells the owner who is due tomorrow except filtering the sheet (shop-sources/process-notes.md line 15).
- Deposits are not written into the shop app (shop-sources/process-notes.md line 15).
- The notes state that the cash box and the Rentals sheet are the only record of deposits (shop-sources/process-notes.md line 15).
- The workbook has two sheets, Rentals and Service, in that order (shop-sources/rentals-tracker.xlsx Rentals!A1, Service!A1).
- The Rentals sheet used range is A1:I5 (shop-sources/rentals-tracker.xlsx Rentals!A1:I5).
- The Rentals headers in A1:I1 are Bike, Customer, Phone, Out, Due, Returned, Days Late, Late Fee, Deposit (shop-sources/rentals-tracker.xlsx Rentals!A1:I1).
- The Service sheet used range is A1:D5 (shop-sources/rentals-tracker.xlsx Service!A1:D5).
- The Service headers in A1:D1 are Bike, Last Service, Next Service, Overdue (shop-sources/rentals-tracker.xlsx Service!A1:D1).
- The Rentals Bike values in A2:A5 are CITY-01, CITY-02, TREK-03, CITY-04 (shop-sources/rentals-tracker.xlsx Rentals!A2:A5).
- The Rentals Out values in D2:D5 are 2026-10-05, 2026-10-06, 2026-10-07, 2026-10-08 (shop-sources/rentals-tracker.xlsx Rentals!D2:D5).
- The Rentals Due values in E2:E5 are 2026-10-08, 2026-10-07, 2026-10-14, 2026-10-10 (shop-sources/rentals-tracker.xlsx Rentals!E2:E5).
- The Rentals Returned value in F2 is 2026-10-09 (shop-sources/rentals-tracker.xlsx Rentals!F2).
- The Rentals Returned cells F3 and F4 are empty (shop-sources/rentals-tracker.xlsx Rentals!F3:F4).
- The Rentals Returned value in F5 is 2026-10-10 (shop-sources/rentals-tracker.xlsx Rentals!F5).
- The Rentals Deposit values in I2:I5 are the numbers 50, 50, 100, 50 (shop-sources/rentals-tracker.xlsx Rentals!I2:I5).
- The Rentals date cells D2:F5 are stored as text strings, not date values (shop-sources/rentals-tracker.xlsx Rentals!D2:F5).
- The Service Bike values in A2:A5 are CITY-01, CITY-02, TREK-03, CITY-04 (shop-sources/rentals-tracker.xlsx Service!A2:A5).
- The Service Last Service values in B2:B5 are the text strings 2026-07-02, 2026-09-15, 2026-06-20, 2026-08-30 (shop-sources/rentals-tracker.xlsx Service!B2:B5).
- Rentals!G2 contains the formula `=IF(F2="","",MAX(DATEVALUE(F2)-DATEVALUE(E2),0))` (shop-sources/rentals-tracker.xlsx Rentals!G2).
- Rentals!G3 contains the formula `=IF(F3="","",MAX(DATEVALUE(F3)-DATEVALUE(E3),0))` (shop-sources/rentals-tracker.xlsx Rentals!G3).
- Rentals!G4 contains the formula `=IF(F4="","",MAX(DATEVALUE(F4)-DATEVALUE(E4),0))` (shop-sources/rentals-tracker.xlsx Rentals!G4).
- Rentals!G5 contains the formula `=IF(F5="","",MAX(DATEVALUE(F5)-DATEVALUE(E5),0))` (shop-sources/rentals-tracker.xlsx Rentals!G5).
- Rentals!H2 contains the formula `=IF(G2="","",MIN(G2*5,50))` (shop-sources/rentals-tracker.xlsx Rentals!H2).
- Rentals!H3 contains the formula `=IF(G3="","",MIN(G3*5,50))` (shop-sources/rentals-tracker.xlsx Rentals!H3).
- Rentals!H4 contains the formula `=IF(G4="","",MIN(G4*5,50))` (shop-sources/rentals-tracker.xlsx Rentals!H4).
- Rentals!H5 contains the formula `=IF(G5="","",MIN(G5*5,50))` (shop-sources/rentals-tracker.xlsx Rentals!H5).
- Service!C2 contains the formula `=DATEVALUE(B2)+90` (shop-sources/rentals-tracker.xlsx Service!C2).
- Service!C3 contains the formula `=DATEVALUE(B3)+90` (shop-sources/rentals-tracker.xlsx Service!C3).
- Service!C4 contains the formula `=DATEVALUE(B4)+90` (shop-sources/rentals-tracker.xlsx Service!C4).
- Service!C5 contains the formula `=DATEVALUE(B5)+90` (shop-sources/rentals-tracker.xlsx Service!C5).
- Service!D2 contains the formula `=IF(C2<TODAY(),"yes","no")` (shop-sources/rentals-tracker.xlsx Service!D2).
- Service!D3 contains the formula `=IF(C3<TODAY(),"yes","no")` (shop-sources/rentals-tracker.xlsx Service!D3).
- Service!D4 contains the formula `=IF(C4<TODAY(),"yes","no")` (shop-sources/rentals-tracker.xlsx Service!D4).
- Service!D5 contains the formula `=IF(C5<TODAY(),"yes","no")` (shop-sources/rentals-tracker.xlsx Service!D5).
- All 16 cells in Rentals!G2:H5 and Service!C2:D5 contain formulas and no typed values (shop-sources/rentals-tracker.xlsx Rentals!G2:H5, Service!C2:D5).

## shop-app schema

- Every table is created by init_db, which runs schema.sql through executescript with CREATE TABLE IF NOT EXISTS, and init_db is called from main on every app.py command (shop-app/db.py:14 init_db, shop-app/app.py:27 main).
- The bikes table declares columns id, label, frame_size, status, last_service_date (shop-app/schema.sql:1 bikes).
- The customers table declares columns id, name, phone, email (shop-app/schema.sql:9 customers).
- The rentals table declares columns id, bike_id, customer_id, rented_at, due_at, returned_at, deposit_cents, late_fee_cents (shop-app/schema.sql:16 rentals).
- The maintenance_log table declares columns id, bike_id, note, logged_at (shop-app/schema.sql:27 maintenance_log).
- bikes.id is INTEGER PRIMARY KEY AUTOINCREMENT (shop-app/schema.sql:2 bikes.id); SQLite assigns it on the INSERT in add_bike (shop-app/rentals.py:10 add_bike); read by SELECT id in rent_bike (shop-app/rentals.py:34 rent_bike) and by bike["id"] in the rentals INSERT (shop-app/rentals.py:42 rent_bike).
- bikes.label is TEXT NOT NULL UNIQUE (shop-app/schema.sql:3 bikes.label); written by the INSERT in add_bike (shop-app/rentals.py:10 add_bike); read in WHERE label = ? by rent_bike (shop-app/rentals.py:34 rent_bike), return_bike (shop-app/rentals.py:53 return_bike) and the UPDATE in return_bike (shop-app/rentals.py:63 return_bike); read as b.label by list_open (shop-app/rentals.py:70 list_open) and row["label"] in the open command (shop-app/app.py:40 open).
- bikes.frame_size is TEXT NOT NULL (shop-app/schema.sql:4 bikes.frame_size); written by the INSERT in add_bike (shop-app/rentals.py:10 add_bike), fed from the frame_size argument (shop-app/app.py:30 main); no code reads it back (shop-app/rentals.py:34 rent_bike, shop-app/rentals.py:52 return_bike, shop-app/rentals.py:70 list_open).
- bikes.status is TEXT NOT NULL DEFAULT "available" (shop-app/schema.sql:5 bikes.status); written by the column default on the INSERT in add_bike (shop-app/rentals.py:10 add_bike), by UPDATE bikes SET status = "rented" in rent_bike (shop-app/rentals.py:44 rent_bike) and by UPDATE bikes SET status = "available" in return_bike (shop-app/rentals.py:63 return_bike); read by SELECT id, status in rent_bike (shop-app/rentals.py:34 rent_bike) and compared to "available" (shop-app/rentals.py:38 rent_bike).
- bikes.last_service_date is TEXT with no constraint (shop-app/schema.sql:6 bikes.last_service_date); no INSERT or UPDATE in shop-app/ sets it, and no code reads it (shop-app/rentals.py:10 add_bike, shop-app/rentals.py:44 rent_bike, shop-app/rentals.py:63 return_bike).
- customers.id is INTEGER PRIMARY KEY AUTOINCREMENT (shop-app/schema.sql:10 customers.id); SQLite assigns it on the INSERT in find_or_create_customer (shop-app/rentals.py:23 find_or_create_customer); read by SELECT id (shop-app/rentals.py:18 find_or_create_customer), row["id"] (shop-app/rentals.py:21 find_or_create_customer) and c.id in the join of list_open (shop-app/rentals.py:71 list_open).
- customers.name is TEXT NOT NULL (shop-app/schema.sql:11 customers.name); written by the INSERT in find_or_create_customer (shop-app/rentals.py:23 find_or_create_customer); read as c.name by list_open (shop-app/rentals.py:70 list_open) and row["name"] in the open command (shop-app/app.py:40 open).
- customers.phone is TEXT NOT NULL (shop-app/schema.sql:12 customers.phone); written by the INSERT in find_or_create_customer (shop-app/rentals.py:23 find_or_create_customer); read in WHERE phone = ? (shop-app/rentals.py:18 find_or_create_customer), as c.phone by list_open (shop-app/rentals.py:70 list_open) and row["phone"] in the open command (shop-app/app.py:40 open).
- customers.email is TEXT with no constraint (shop-app/schema.sql:13 customers.email); no INSERT or UPDATE in shop-app/ sets it (shop-app/rentals.py:23 find_or_create_customer), and no code reads it (shop-app/rentals.py:18 find_or_create_customer, shop-app/rentals.py:70 list_open).
- rentals.id is INTEGER PRIMARY KEY AUTOINCREMENT (shop-app/schema.sql:17 rentals.id); SQLite assigns it on the INSERT in rent_bike (shop-app/rentals.py:41 rent_bike); read by SELECT r.id in return_bike (shop-app/rentals.py:52 return_bike) and in WHERE id = ? of the UPDATE (shop-app/rentals.py:60 return_bike).
- rentals.bike_id is INTEGER NOT NULL REFERENCES bikes(id) (shop-app/schema.sql:18 rentals.bike_id); written by the INSERT in rent_bike (shop-app/rentals.py:41 rent_bike); read in the join of return_bike (shop-app/rentals.py:52 return_bike) and of list_open (shop-app/rentals.py:71 list_open).
- rentals.customer_id is INTEGER NOT NULL REFERENCES customers(id) (shop-app/schema.sql:19 rentals.customer_id); written by the INSERT in rent_bike (shop-app/rentals.py:41 rent_bike); read in the join of list_open (shop-app/rentals.py:71 list_open).
- rentals.rented_at is TEXT NOT NULL (shop-app/schema.sql:20 rentals.rented_at); written by the INSERT in rent_bike from today.isoformat() (shop-app/rentals.py:41 rent_bike); no code reads it (shop-app/rentals.py:52 return_bike, shop-app/rentals.py:70 list_open).
- rentals.due_at is TEXT NOT NULL (shop-app/schema.sql:21 rentals.due_at); written by the INSERT in rent_bike from due.isoformat() (shop-app/rentals.py:41 rent_bike); read by SELECT r.due_at in return_bike (shop-app/rentals.py:52 return_bike), by date.fromisoformat(row["due_at"]) in return_bike (shop-app/rentals.py:58 return_bike), by SELECT r.due_at and ORDER BY r.due_at in list_open (shop-app/rentals.py:70 list_open, shop-app/rentals.py:72 list_open) and by row["due_at"] in the open command (shop-app/app.py:40 open).
- rentals.returned_at is TEXT with no default (shop-app/schema.sql:22 rentals.returned_at); the INSERT in rent_bike omits it (shop-app/rentals.py:41 rent_bike), and it is written by UPDATE rentals SET returned_at = ? in return_bike (shop-app/rentals.py:60 return_bike); read by WHERE r.returned_at IS NULL in return_bike (shop-app/rentals.py:53 return_bike) and in list_open (shop-app/rentals.py:72 list_open).
- rentals.deposit_cents is INTEGER with no default or constraint (shop-app/schema.sql:23 rentals.deposit_cents); no INSERT or UPDATE in shop-app/ sets it (shop-app/rentals.py:41 rent_bike, shop-app/rentals.py:60 return_bike), and no code reads it (shop-app/rentals.py:52 return_bike, shop-app/rentals.py:70 list_open).
- rentals.late_fee_cents is INTEGER NOT NULL DEFAULT 0 (shop-app/schema.sql:24 rentals.late_fee_cents); written with the default 0 by the INSERT in rent_bike (shop-app/rentals.py:41 rent_bike) and by UPDATE rentals SET late_fee_cents = ? in return_bike (shop-app/rentals.py:60 return_bike), where the value comes from late_fee_cents (shop-app/rentals.py:58 return_bike, shop-app/fees.py:11 late_fee_cents); no code reads it back, because return_bike returns the Python fee value (shop-app/rentals.py:64 return_bike).
- The late fee is 400 cents per day late, capped at 4000 cents per rental (shop-app/fees.py:3 LATE_FEE_PER_DAY_CENTS, shop-app/fees.py:4 LATE_FEE_CAP_CENTS).
- maintenance_log.id is INTEGER PRIMARY KEY AUTOINCREMENT (shop-app/schema.sql:28 maintenance_log.id); no INSERT into maintenance_log exists in shop-app/, and no code reads the table (shop-app/schema.sql:27 maintenance_log).
- maintenance_log.bike_id is INTEGER NOT NULL REFERENCES bikes(id) (shop-app/schema.sql:29 maintenance_log.bike_id); no INSERT or UPDATE in shop-app/ sets it, and no code reads it (shop-app/schema.sql:27 maintenance_log).
- maintenance_log.note is TEXT NOT NULL (shop-app/schema.sql:30 maintenance_log.note); no INSERT or UPDATE in shop-app/ sets it, and no code reads it (shop-app/schema.sql:27 maintenance_log).
- maintenance_log.logged_at is TEXT NOT NULL (shop-app/schema.sql:31 maintenance_log.logged_at); no INSERT or UPDATE in shop-app/ sets it, and no code reads it (shop-app/schema.sql:27 maintenance_log).
- The table name maintenance_log appears in no code file under shop-app/; the only match is its CREATE TABLE statement (shop-app/schema.sql:27 maintenance_log).
- The test module drives add_bike in setUp, rent_bike in two tests and list_open in one, against a temporary database (shop-app/tests/test_rent.py:17 setUp, shop-app/tests/test_rent.py:23 test_rent_marks_bike_rented, shop-app/tests/test_rent.py:27 test_rent_twice_fails, shop-app/tests/test_rent.py:24 test_rent_marks_bike_rented); it reads no table column directly (shop-app/tests/test_rent.py:8-9 imports, shop-app/tests/test_rent.py:17 setUp, shop-app/tests/test_rent.py:23-29 test methods).
