Database Structure – Potential Issues

Missing or Incomplete Keys
- No primary key defined: dbo.EmployeeHistory, dev.emp.
- Verify all foreign key columns are indexed on child tables to avoid scan-heavy joins and to support efficient deletes/updates.

Duplicate/Redundant Foreign Keys
- Duplicate FKs on the same column pair:
  - dbo.UtilityMeter.FacilityID → dbo.Facility.FacilityID (2 constraints)
  - dbo.UtilityMeter.UtilityTypeID → dbo.UtilityType.UtilityTypeID (2 constraints)

Naming / Spelling Inconsistencies
- Columns
  - ECM.Project_Invesetment (probable: Project_Investment)
  - ECM.Commisioning_and_Training_Cost (probable: Commissioning_and_Training_Cost)
  - System_Exhaust primary key column appears as System_ExhuastID in index metadata
- Views
  - dbo.v_MVVerfiedSavings (probable: v_MVVerifiedSavings)
- Constraints
  - FacilitySystem_HVACSystemConfiguration FK name references “SystemConfiguration” but points to HVACSystemMode (could be misnamed; confirm target).

View Implementation Concerns
- Ordering in views
  - dbo.v_MERA and dbo.v_ActiveMVMeters use TOP (100) PERCENT … ORDER BY.
  - ORDER BY is ignored in views; TOP 100 PERCENT does not guarantee ordering. Move ORDER BY to consuming queries or apply ordering in a final SELECT.
- Sensitive data exposure
  - dbo.v_ActiveMVMeters exposes UtilityAccess.Email/Username/Password. Consider removing or masking credentials, or moving to a secured proc.
- References to non-existent tables
  - dbo.v_MVVerfiedSavings references MVSavings_OptionA, MVSavings_NonMeasured, MVSavings_Custom which are not present in ListofTables.md. Validate object existence or update the view.
- Recursive CTE in view
  - dbo.v_MVSchedule uses a recursive Numbers CTE. Ensure performance is acceptable and recursion depth remains bounded (MAXRECURSION default is 100; logic bounds at 50).

Data Types / Modeling
- Many DECIMAL columns lack explicit precision/scale in TableColumns.md (defaults to DECIMAL(18,0) in SQL Server). Review monetary/energy fields (e.g., savings, costs, rates) for appropriate scale to avoid rounding.
- ZIP code stored as VARCHAR(5) in Customer.Zip; may not accommodate ZIP+4 or non-US postal codes.

Consistency / Conventions
- Mixed naming styles across objects (PK_*, *_PK, varying casing/underscores). Consider standardizing for clarity.
- Verify all FK columns follow consistent singular/plural and ID suffix conventions.

Weather/Reference Tables
- WeatherDataDailyNormals_2006-2020 has a hyphen and numbers in the name; unconventional but valid. Consider a consistent naming scheme (e.g., WeatherDataDailyNormals_2006_2020).

Suggested Remediations (targeted)
- Keys: Add PKs for dbo.EmployeeHistory and dev.emp if appropriate; otherwise document why they are heap/staging.
- FKs: Remove redundant FK duplicates on dbo.UtilityMeter columns after confirming no dependent objects rely on both.
- Columns: Correct typos (Project_Invesetment, Commisioning_and_Training_Cost, System_ExhuastID) with careful migration scripts.
- Views: Remove ORDER BY from views; move sorting downstream. Remove credentials from v_ActiveMVMeters. Update v_MVVerfiedSavings to reference real tables and correct spelling.
- Types: Specify DECIMAL precision/scale for financial/energy metrics; review VARCHAR lengths for addresses/IDs.

