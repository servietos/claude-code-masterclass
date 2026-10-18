# Current state: bike rental shop

Built from ledger.md in this folder. Inventory and How it is used lines cite the source path from the ledger. Limits and Gap list conclude from the observations they name.

## Inventory

- The shop app is a Python command-line tool with four subcommands: add-bike, rent, return, open (shop-app/app.py:7 main).
- add-bike takes a label and a frame_size (shop-app/app.py:11-13 main).
- rent takes a label, name and phone, plus an optional --days integer that defaults to 1 (shop-app/app.py:15-19 main).
- return takes a label (shop-app/app.py:21-22 main).
- open prints one tab-separated line per open rental: label, name, phone, due_at (shop-app/app.py:38-40 main).
- The late fee is 400 cents per day late, capped at 4000 cents per rental (shop-app/fees.py:3-4).
- days_late() returns max((returned_at - due_at).days, 0) (shop-app/fees.py:7-8 days_late).
- rent_bike() sets the due date to today plus the days argument, and raises an error when the bike is unknown or not available (shop-app/rentals.py:28-39 rent_bike).
- return_bike() writes returned_at and late_fee_cents to the open rental, sets the bike to available, and returns the fee (shop-app/rentals.py:51-64 return_bike).
- list_open() returns open rentals ordered by due_at (shop-app/rentals.py:67-73 list_open).
- The database has four tables: bikes, customers, rentals, maintenance_log (shop-app/schema.sql:1, 9, 16, 27).
- The test file has two tests, one for renting and one for a second rent of the same bike (shop-app/tests/test_rent.py:22-29).
- The workbook shop-sources/rentals-tracker.xlsx has a Rentals sheet with headers Bike, Customer, Phone, Out, Due, Returned, Days Late, Late Fee, Deposit (Rentals!A1:I1).
- The Rentals sheet holds four rentals: CITY-01, CITY-02, TREK-03, CITY-04 (Rentals!A2:A5).
- The Rentals Deposit values are 50, 50, 100, 50 (Rentals!I2:I5).
- Rentals!H2:H5 computes the late fee as MIN(days late * 5, 50) (Rentals!H2:H5).
- The workbook has a Service sheet with headers Bike, Last Service, Next Service, Overdue (Service!A1:D1).
- Service!C2:C5 sets Next Service to Last Service plus 90 days (Service!C2:C5).
- Service!D2:D5 shows "yes" when Next Service is before TODAY() (Service!D2:D5).
- The process notes are by Mara Huber, Shop Owner, and cover one week, 5 to 9 October 2026 (shop-sources/process-notes.md line 3).

## How it is used

- Monday: the owner writes the rental into the Rentals sheet, takes a 50 euro cash deposit, and types the rental into the shop app. The steps take 6 and 4 minutes (shop-sources/process-notes.md lines 7-8).
- Tuesday: the owner phones each customer whose bike is due the next day, read from the Due column. The step takes 25 minutes (shop-sources/process-notes.md line 9).
- Wednesday: the owner reads the Late Fee column in Excel, takes the fee with the deposit refund, and marks the bike returned in the shop app. The steps take 8 and 3 minutes (shop-sources/process-notes.md lines 10-11).
- Thursday: the owner checks the Service sheet for bikes past their next service date and pulls them off the floor by hand. The step takes 15 minutes (shop-sources/process-notes.md line 12).
- Friday: the owner counts the week's late fees from the Rentals sheet for the owner report. The step takes 20 minutes (shop-sources/process-notes.md line 13).
- The notes name the reminder calls as the costliest step, and state that only filtering the sheet shows who is due tomorrow (shop-sources/process-notes.md line 15).
- The notes state that deposits are not written into the shop app, and that the cash box and the Rentals sheet are the only deposit record (shop-sources/process-notes.md line 15).
- Rentals row 2 (CITY-01) has Out 2026-10-05, Due 2026-10-08, Returned 2026-10-09 (Rentals!D2:F2), so the bike came back one day late (shop-sources/process-notes.md line 10).
- Dates in Rentals!D2:F5 and Service!B2:B5 are stored as text, and the formulas convert them with DATEVALUE (shop-sources/rentals-tracker.xlsx Rentals!D2:F5, Service!B2:B5).

## Limits

- Late fee rate differs. The app charges 400 cents per day with a 4000 cent cap (shop-app/fees.py:3-4). The workbook charges 5 per day with a cap of 50 (Rentals!H2:H5). Both values are kept. For the one late return (Rentals!G2 = 1 day), the app gives 400 cents and the workbook gives 5. The workbook states no currency unit, and the app states cents only.
- Deposit differs. The app's deposit_cents column is never written by any code (shop-app/rentals.py:41 rent_bike, shop-app/rentals.py:60 return_bike). The workbook records 50, 50, 100, 50 (Rentals!I2:I5). Both values are kept: the app has none, the workbook has those four amounts.
- Service dates differ in presence. The app's last_service_date column is never written or read (shop-app/schema.sql:6, shop-app/rentals.py:10 add_bike). The workbook has Last Service values 2026-07-02, 2026-09-15, 2026-06-20, 2026-08-30 (Service!B2:B5). Both kept.
- Overdue status exists only in the workbook. Computed by hand from the Service!C2:C5 formula on 2026-10-17, Next Service is 2026-09-30, 2026-12-14, 2026-09-18, 2026-11-28, so Overdue would read yes, no, yes, no. The workbook's cached value is not in the ledger, so this is my calculation.
- The app's maintenance_log table is never written or read (shop-app/schema.sql:27), so the app has no service history.
- The app keeps bike frame_size and customer email, and no code reads either (shop-app/rentals.py:34, 52, 70; shop-app/schema.sql:13). The workbook has neither column.
- Each rental is entered twice, once in the workbook and once in the app (shop-sources/process-notes.md lines 7-8, 11).
- Tests cover renting and the double-rent error only. No test calls return_bike(), late_fee_cents() or days_late() (shop-app/tests/test_rent.py:22-29, and ledger notes on test_rent.py).
- The workbook's date values are text, so DATEVALUE depends on the locale of the machine that opens the file (shop-sources/rentals-tracker.xlsx Rentals!D2:F5).

## Gap list

| # | Capability | Mark | Sources | Basis |
|---|---|---|---|---|
| 1 | Remind a customer the day before a bike is due | partly exists | shop-app/rentals.py:67-73 list_open; shop-app/app.py:38-40 open; shop-sources/process-notes.md lines 9, 15 | open shows due dates and phone numbers but has no date filter and sends nothing; the owner calls by hand from the Due column |
| 2 | Record the deposit at rental and refund it at return | partly exists | shop-sources/rentals-tracker.xlsx Rentals!I2:I5; shop-app/schema.sql:23; shop-sources/process-notes.md lines 10, 15 | the workbook records deposit amounts but has no refund field; the app column deposit_cents is never written; refunds come from the cash box |
| 3 | Flag bikes whose service is overdue | exists | shop-sources/rentals-tracker.xlsx Service!C2:D5; shop-sources/process-notes.md line 12 | the workbook computes the overdue flag; the app has no flag and never uses last_service_date |
| 4 | Report the late fees collected in a week | partly exists | shop-sources/rentals-tracker.xlsx Rentals!H2:H5; shop-app/fees.py:3-4; shop-app/rentals.py:58-64; shop-sources/process-notes.md line 13 | fees are calculated per rental in both, but neither totals a week or records payment; the owner counts by hand, and the two rates differ |
| 5 | Let customers book a bike online | missing | shop-app/app.py:7 main (command-line only); shop-app/schema.sql:1, 9, 16, 27 | the observed files contain no web interface, no booking code and no booking table |
</content>
