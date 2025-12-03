|schema_id|schema_name|name|definition|
|---------|-----------|----|----------|
|1|dbo|v_ActiveMVMeters|CREATE VIEW dbo.v_ActiveMVMeters
AS
SELECT TOP (100) PERCENT dbo.OptionCMeter.UtilityMeterID, dbo.v_MERA.Customer_Name, dbo.v_MERA.Facility_Name, dbo.v_MERA.Utility_Type, dbo.v_MERA.Utility_Provider, dbo.v_MERA.Account_Number, dbo.v_MERA.Meter_Number, dbo.UtilityAccount.AccessType, dbo.UtilityAccess.Email, dbo.UtilityAccess.Username, dbo.UtilityAccess.Password
FROM  dbo.UtilityAccount LEFT OUTER JOIN
         dbo.UtilityAccess ON dbo.UtilityAccount.UtilityAccessID = dbo.UtilityAccess.UtilityAccessID INNER JOIN
         dbo.OptionCMeter INNER JOIN
         dbo.v_MERA ON dbo.OptionCMeter.UtilityMeterID = dbo.v_MERA.UtilityMeterID INNER JOIN
         dbo.MVContract ON dbo.OptionCMeter.MVContractID = dbo.MVContract.MVContractID ON dbo.UtilityAccount.UtilityAccountID = dbo.v_MERA.UtilityAccountID
WHERE (dbo.MVContract.MV_Active = 1)
ORDER BY dbo.v_MERA.Customer_Name
|
|1|dbo|v_cdexUtilityAccounts|CREATE VIEW dbo.v_cdexUtilityAccounts AS 

SELECT
	UtilityAccount.UtilityAccountID,
	UtilityProvider.UtilityProviderID,
	Customer.CustomerID,
	Account_Number,
	UtilityProvider.Utility_Provider,
	Customer.Customer_Name,
	Count(UtilityMeter.UtilityMeterID) AS TotalCount,
	Sum(CASE when UtilityTypeID = 1 then 1 else 0 end) as ElectricCount,
	Sum(CASE when UtilityTypeID = 2 then 1 else 0 end) as NatGasCount,
	Sum(CASE when UtilityTypeID = 10 then 1 else 0 end) as WaterCount
FROM
	UtilityAccount
LEFT OUTER JOIN UtilityMeter ON
	UtilityAccount.UtilityAccountID = UtilityMeter.UtilityAccountID
LEFT OUTER JOIN UtilityProvider on
	UtilityAccount.UtilityProviderID = UtilityProvider.UtilityProviderID
INNER JOIN Customer ON
	UtilityAccount.CustomerID = Customer.CustomerID
GROUP BY
	UtilityAccount.UtilityAccountID,
	Account_Number,
	Utility_Provider,
	UtilityProvider.UtilityProviderID,
	Customer.CustomerID,
	Customer.Customer_Name;|
|1|dbo|v_LeopardoConversion|CREATE VIEW dbo.v_LeopardoConversion
AS
SELECT dbo.Customer.CustomerID, dbo.Customer.Customer_Name, dbo.Project.ProjectID, dbo.Project.Project_Name_Full, dbo.ProjectFeasibility.ProjectFeasibilityID, dbo.ProjectFeasibility.Report_Delivered AS Feasibility_Report_Delivered, dbo.ProjectFeasibility.Report_Delivered_Date AS Feasibility_Report_Delivered_Date, dbo.ProjectRFPRFQ.ProjectRFPRFQID, 
         dbo.ProjectRFPRFQ.RFPRFQ_Delivered, dbo.RFPRFQStatus.RFPRFQ_Status, dbo.ProjectSelectedIGA.ProjectSelectedIGAID, dbo.ProjectSelectedIGA.IGA_Delivered, dbo.MVContract.MVContractID
FROM  dbo.Customer LEFT OUTER JOIN
         dbo.Project ON dbo.Customer.CustomerID = dbo.Project.CustomerID LEFT OUTER JOIN
         dbo.ProjectFeasibility ON dbo.Project.ProjectID = dbo.ProjectFeasibility.ProjectID LEFT OUTER JOIN
         dbo.ProjectRFPRFQ ON dbo.Project.ProjectID = dbo.ProjectRFPRFQ.ProjectID LEFT OUTER JOIN
         dbo.ProjectSelectedIGA ON dbo.Project.ProjectID = dbo.ProjectSelectedIGA.ProjectID LEFT OUTER JOIN
         dbo.MVContract ON dbo.Project.ProjectID = dbo.MVContract.ProjectID LEFT OUTER JOIN
         dbo.RFPRFQStatus ON dbo.ProjectRFPRFQ.RFPRFQStatusID = dbo.RFPRFQStatus.RFPRFQSTATUSID
WHERE (dbo.Customer.TeamID = 2)
|
|1|dbo|v_MERA|CREATE VIEW dbo.v_MERA
AS
SELECT TOP (100) PERCENT dbo.Customer.Customer_Name, dbo.Facility.Facility_Name, dbo.UtilityType.Utility_Type, dbo.UtilityProvider.Utility_Provider, dbo.UtilityAccount.Account_Number, dbo.UtilityMeter.Meter_Number, dbo.UtilityMeter.Utility_Rate, dbo.Customer.CustomerID, dbo.Facility.FacilityID, dbo.UtilityMeter.UtilityMeterID, dbo.UtilityAccount.UtilityAccountID, 
         dbo.UtilityType.UtilityTypeID, dbo.UtilityAccount.UtilityProviderID, dbo.UtilityMeter.FuelCodeID, dbo.EnergyConversionFactor.BTU_per_Unit
FROM  dbo.Customer INNER JOIN
         dbo.Facility ON dbo.Customer.CustomerID = dbo.Facility.CustomerID INNER JOIN
         dbo.UtilityMeter ON dbo.Customer.CustomerID = dbo.UtilityMeter.CustomerID AND dbo.Facility.FacilityID = dbo.UtilityMeter.FacilityID AND dbo.Facility.FacilityID = dbo.UtilityMeter.FacilityID INNER JOIN
         dbo.UtilityAccount ON dbo.UtilityMeter.UtilityAccountID = dbo.UtilityAccount.UtilityAccountID INNER JOIN
         dbo.UtilityType ON dbo.UtilityMeter.UtilityTypeID = dbo.UtilityType.UtilityTypeID AND dbo.UtilityMeter.UtilityTypeID = dbo.UtilityType.UtilityTypeID INNER JOIN
         dbo.UtilityProvider ON dbo.UtilityAccount.UtilityProviderID = dbo.UtilityProvider.UtilityProviderID INNER JOIN
         dbo.EnergyConversionFactor ON dbo.UtilityMeter.FuelCodeID = dbo.EnergyConversionFactor.FuelCodeID
ORDER BY dbo.Customer.Customer_Name DESC, dbo.Facility.Facility_Name DESC|
|1|dbo|v_MVContractMapping|CREATE VIEW dbo.v_MVContractMapping
AS
SELECT dbo.Customer.Customer_Name, dbo.Project.Project_Name, dbo.Customer.CustomerID, dbo.Project.ProjectID, dbo.MVContract.MVContractID
FROM  dbo.MVContract INNER JOIN
         dbo.Project ON dbo.MVContract.ProjectID = dbo.Project.ProjectID INNER JOIN
         dbo.Customer ON dbo.Project.CustomerID = dbo.Customer.CustomerID
|
|1|dbo|v_MVSavings_Verified|CREATE VIEW dbo.v_MVSavings_Verified
AS
SELECT        t1.MVContract_GuaranteeID, t1.MVReportID, t1.Actual_Savings_Cost, t1.Adjusted_Guarantee_Cost, t1.Savings_Goal_kBTU, t1.Savings_kBTU, MVContract_AnnualGuarantee.MVContractID, 
                         MVContract_AnnualGuarantee.Contract_Guarantee, dbo.MVReport.Report_Year, dbo.MVContract_Category.MV_Option, dbo.MVContract_Category.ECM_Category
FROM            (SELECT        MVContract_GuaranteeID, MVReportID, SUM(CASE WHEN Actual_or_SimActual = 'Actual' THEN Savings_Cost_Actual ELSE Savings_Cost_SimActual END) AS Actual_Savings_Cost, SUM(Savings_Goal_Cost) 
                                                    AS Adjusted_Guarantee_Cost, SUM(Savings_Goal_kBTU) AS Savings_Goal_kBTU, SUM(Baseline_kBTU) - SUM(Actual_kBTU) AS Savings_kBTU
                          FROM            dbo.MVSavings_OptionC
                          GROUP BY MVContract_GuaranteeID, MVReportID
                          UNION
                          SELECT        MVContract_GuaranteeID, MVReportID, SUM(Actual_Savings_Cost) AS Actual_Savings_Cost, SUM(Adjusted_Guarantee_Cost) AS Adjusted_Guarantee_Cost, SUM(Savings_Goal_kBTU) AS Savings_Goal_kBTU, 
                                                   SUM(Savings_Goal_kBTU) AS Savings_kBTU
                          FROM            dbo.MVSavings_ECMLevel
                          GROUP BY MVContract_GuaranteeID, MVReportID
                          UNION
                          SELECT        MVContract_GuaranteeID, MVReportID, SUM(Actual_Savings_Cost) AS Actual_Savings_Cost, SUM(Adjusted_Guarantee_Cost) AS Adjusted_Guarantee_Cost, NULL AS Savings_Goal_kBTU, NULL 
                                                   AS Savings_kBTU
                          FROM            dbo.MVSavings_Operational
                          GROUP BY MVContract_GuaranteeID, MVReportID) AS t1 INNER JOIN
                         dbo.MVContract_AnnualGuarantee ON t1.MVContract_GuaranteeID = MVContract_AnnualGuarantee.MVContract_GuaranteeID INNER JOIN
                         dbo.MVReport ON t1.MVReportID = dbo.MVReport.MVReportID INNER JOIN
                         dbo.MVContract_Category ON dbo.MVContract_AnnualGuarantee.MVContract_CategoryID = dbo.MVContract_Category.MVContract_CategoryID
|
|1|dbo|v_MVSavingsSummary|-- dbo.v_MVSavingsSummary source

CREATE VIEW dbo.v_MVSavingsSummary
AS
SELECT
  * 
FROM 
  (
    SELECT 
      t1.MVContract_GuaranteeID, 
      t1.MVReportID, 
      t1.MVReport_StipulatedID, 
      t1.Type, 
      t1.Actual_Savings_Cost, 
      t1.Adjusted_Guarantee_Cost, 
      t1.Savings_Goal_kBTU, 
      t1.Savings_kBTU, 
      MVContract_AnnualGuarantee.MVContractID, 
      MVContract_AnnualGuarantee.Contract_Guarantee, 
      COALESCE (dbo.MVReport.Report_Year, '') + COALESCE (
        dbo.MVReport_Stipulated.Report_Year, 
        ''
      ) AS Report_Year, 
      (
        Select 
          Max(v) 
        FROM 
          (
            VALUES 
              (
                dbo.MVReport_Stipulated.Period_End
              ), 
              (dbo.MVReport.Period_End)
          ) as value(v)
      ) AS Period_End, 
      dbo.MVContract_Category.MV_Option, 
      dbo.MVContract_Category.ECM_Category 
    FROM 
      (
        SELECT 
          'Verified - Option C' AS Type, 
          MVContract_GuaranteeID, 
          MVReportID, 
          NULL AS MVReport_StipulatedID, 
          SUM(
            CASE WHEN Actual_or_SimActual = 'Actual' THEN Savings_Cost_Actual ELSE Savings_Cost_SimActual END
          ) AS Actual_Savings_Cost, 
          SUM(Savings_Goal_Cost) AS Adjusted_Guarantee_Cost, 
          SUM(Savings_Goal_kBTU) AS Savings_Goal_kBTU, 
          SUM(Baseline_kBTU) - SUM(Actual_kBTU) AS Savings_kBTU 
        FROM 
          dbo.MVSavings_OptionC 
        GROUP BY 
          MVContract_GuaranteeID, 
          MVReportID 
        UNION ALL 
        SELECT 
          'Verified - ECMLevel' AS Type, 
          MVContract_GuaranteeID, 
          MVReportID, 
          NULL AS MVReport_StipulatedID, 
          SUM(Actual_Savings_Cost) AS Actual_Savings_Cost, 
          SUM(Adjusted_Guarantee_Cost) AS Adjusted_Guarantee_Cost, 
          SUM(Savings_Goal_kBTU) AS Savings_Goal_KBTU, 
          SUM(Savings_kBTU) AS Savings_kBTU 
        FROM 
          dbo.MVSavings_ECMLevel 
        GROUP BY 
          MVContract_GuaranteeID, 
          MVReportID 
        UNION ALL 
        SELECT 
          'Verified - Operational' AS Type, 
          MVContract_GuaranteeID, 
          MVReportID, 
          NULL AS MVReport_StipulatedID, 
          SUM(Actual_Savings_Cost) AS Actual_Savings_Cost, 
          SUM(Adjusted_Guarantee_Cost) AS Adjusted_Guarantee_Cost, 
          NULL AS Savings_Goal_kBTU, 
          NULL AS Savings_kBTU 
        FROM 
          dbo.MVSavings_Operational 
        GROUP BY 
          MVContract_GuaranteeID, 
          MVReportID 
        UNION ALL 
        SELECT 
          'Stipulated - Energy' AS Type, 
          MVContract_AnnualGuaranteeID AS MVContract_GuaranteeID, 
          NULL AS MVReportID, 
          MVReport_StipulatedID, 
          SUM(Savings_Cost) AS Actual_Savings_Cost, 
          SUM(Savings_Goal_Cost) AS Adjusted_Guarantee_Cost, 
          SUM(Savings_Goal_kBTU) AS Savings_Goal_kBTU, 
          SUM(Savings_kBTU) AS Savings_kBTU 
        FROM 
          dbo.MVSavings_StipulatedEnergy 
        GROUP BY 
          MVContract_AnnualGuaranteeID, 
          MVReport_StipulatedID 
        UNION ALL 
        SELECT 
          'Stipulated - Operational' AS Type, 
          MVContract_AnnualGuaranteeID AS MVContract_GuaranteeID, 
          NULL AS MVReportID, 
          MVReport_StipulatedID, 
          SUM(Realized_Savings) AS Actual_Savings_Cost, 
          SUM(Adjusted_Guarantee_Cost) AS Adjusted_Guarantee_Cost, 
          NULL AS Savings_Goal_kbTU, 
          NULL AS Savings_kBTU 
        FROM 
          dbo.MVSavings_StipulatedOperational 
        GROUP BY 
          MVContract_AnnualGuaranteeID, 
          MVReport_StipulatedID
      ) AS t1 
      INNER JOIN dbo.MVContract_AnnualGuarantee ON t1.MVContract_GuaranteeID = MVContract_AnnualGuarantee.MVContract_GuaranteeID 
      INNER JOIN dbo.MVContract_Category ON dbo.MVContract_AnnualGuarantee.MVContract_CategoryID = dbo.MVContract_Category.MVContract_CategoryID 
      LEFT OUTER JOIN dbo.MVReport ON t1.MVReportID = dbo.MVReport.MVReportID 
      LEFT OUTER JOIN dbo.MVReport_Stipulated ON t1.MVReport_StipulatedID = dbo.MVReport_Stipulated.MVReport_StipulatedID
  ) AS Temp 
WHERE 
  Temp.Period_End < (
    SELECT 
      CONVERT(
        date, 
        GETDATE()
      ) AS 'Current Date'
  )|
|1|dbo|v_MVSchedule|CREATE VIEW dbo.v_MVSchedule
AS
WITH Numbers AS (
    -- Generate numbers from 0 up to the max guarantee years you expect
    SELECT 0 AS n
    UNION ALL
    SELECT n + 1
    FROM Numbers
    WHERE n + 1 <= 50  -- adjust this number to a safe upper bound for Guarantee_Years
)
SELECT
    ROW_NUMBER() OVER (ORDER BY c.MVContractID, n.n) AS MVScheduleID,
    c.MVContractID,
    c.ProjectID,
    n.n AS [Report Year],
    CASE 
        WHEN (c.Included_MV_Years + c.Additional_MV_Years) = 0 THEN 'Stipulated'
        WHEN n.n <= (c.Included_MV_Years + c.Additional_MV_Years) THEN 'Verified'
        ELSE 'Stipulated'
    END AS [Verification Type],
    CASE 
        WHEN n.n = 0 THEN NULL
        ELSE DATEADD(YEAR, n.n - 1, c.Substantial_Completion_Date)
    END AS Period_Start,
    CASE 
        WHEN n.n = 0 THEN c.Substantial_Completion_Date
        ELSE DATEADD(DAY, -1, DATEADD(YEAR, n.n, c.Substantial_Completion_Date))
    END AS Period_End,
    ISNULL(
        CASE 
            WHEN (c.Included_MV_Years + c.Additional_MV_Years) <> 0 AND n.n <= (c.Included_MV_Years + c.Additional_MV_Years)
            THEN DATEADD(DAY, 90, DATEADD(DAY, -1, DATEADD(YEAR, n.n, c.Substantial_Completion_Date)))
        END,
        CASE 
            WHEN n.n <= (c.Included_MV_Years + c.Additional_MV_Years) THEN DATEADD(DAY, 60, DATEADD(YEAR, n.n, CAST(GETDATE() AS DATE)))
        END
    ) AS [Target Report Date],
    r.MVReportID,
    r.Report_Delivery_Date
FROM dbo.MVContract c
INNER JOIN Numbers n
    ON n.n <= c.Guarantee_Years
LEFT JOIN dbo.MVReport r
    ON c.MVContractID = r.MVContractID
   AND n.n = r.Report_Year
WHERE c.Guarantee_Years <> 0

|
|1|dbo|v_MVVerfiedSavings|CREATE VIEW dbo.v_MVVerfiedSavings AS 
SELECT t1.*, MVContract_AnnualGuarantee.MVContractID, MVContract_AnnualGuarantee.Contract_Guarantee
	FROM(	SELECT MVContract_GuaranteeID, MVReportID, Sum(CASE WHEN Actual_or_SimActual = 'Actual' THEN Savings_Cost_Actual ELSE Savings_Cost_SimActual END) AS Actual_Savings_Cost, Sum(Savings_Goal_Cost) AS Adjusted_Guarantee_Cost, SUM(Savings_Goal_kBTU) as Savings_Goal_KBTU, SUM(Baseline_KBTU) - SUM(Actual_kBTU) AS Savings_kBTU, 'Option C' as MVOption
			FROM MVSavings_OptionC
			GROUP BY MVContract_GuaranteeID, MVReportID
UNION
			Select MVContract_GuaranteeID, MVReportID, Sum(Actual_Savings_Cost) AS Actual_Savings_Cost, Sum(Adjusted_Guarantee_Cost) AS Adjusted_Guarantee_Cost, SUM(Savings_Goal_kBTU) as Savings_Goal_KBTU, SUM(Savings_kBTU) AS Savings_kBTU, 'Option A' as MVOption
			FROM MVSavings_OptionA
			GROUP BY MVCONTract_GuaranteeID, MVReportID
UNION
			Select MVContract_GuaranteeID, MVReportID, Sum(Actual_Savings) AS Actual_Savings_Cost, Sum(Adjusted_Guarantee) AS Adjusted_Guarantee_Cost, NULL as Savings_Goal_kBTU, NULL as Savings_kBTU, 'Non-Measured' as MVOption
			FROM MVSavings_NonMeasured
			GROUP BY MVCONTract_GuaranteeID, MVReportID
UNION
			Select MVContract_GuaranteeID, MVReportID, Sum(Actual_Savings) AS Actual_Savings_Cost, Sum(Adjusted_Guarantee) AS Adjusted_Guarantee_Cost, NULL as Savings_Goal_kBTU, NULL as Savings_kBTU, 'Custom' as MVOption
			FROM MVSavings_Custom
			GROUP BY MVCONTract_GuaranteeID, MVReportID) as t1	
INNER JOIN MVContract_AnnualGuarantee on t1.MVContract_GuaranteeID = MVContract_AnnualGuarantee.MVContract_GuaranteeID|
|1|dbo|v_PowerAppCustomer|CREATE VIEW dbo.v_PowerAppCustomer
AS
SELECT        dbo.Customer.Customer_Name, dbo.Customer.Primary_Address, dbo.Customer.City, dbo.Customer.County, dbo.Customer.Zip, dbo.Customer.Federal_Tax_ID, dbo.Customer.Federal_Tax_ID2, dbo.Customer.Logo_URL, 
                         dbo.Customer.Latitude, dbo.Customer.Longitude, dbo.Customer.StateID, dbo.Customer.CustomerTypeID, dbo.Customer.WeatherStationID, dbo.CustomerType.CustomerType, dbo.State.stateCode, dbo.Customer.CustomerID, 
                         dbo.Team.Project_Team, dbo.Team.ProjectTeamID
FROM            dbo.Customer INNER JOIN
                         dbo.CustomerType ON dbo.Customer.CustomerTypeID = dbo.CustomerType.CustomerTypeID INNER JOIN
                         dbo.State ON dbo.Customer.StateID = dbo.State.stateID INNER JOIN
                         dbo.Team ON dbo.Customer.TeamID = dbo.Team.ProjectTeamID
|
|1|dbo|v_PowerAppProjects|CREATE VIEW dbo.v_PowerAppProjects
AS
SELECT dbo.Project.ProjectID, dbo.Project.CustomerID, dbo.Project.ProjectStatusID, dbo.ProjectStatus.Status_Type AS Project_Status_Level, dbo.Customer.TeamID, dbo.Customer.Customer_Name, dbo.Project.Project_Name_Full, dbo.ProjectStatus.Project_Status, dbo.Team.Project_Team, dbo.Project.Project_Name, dbo.ProjectSelectedIGA.IGA_Delivered, 
         dbo.ProjectFeasibility.Report_Delivered AS Feasibility_Report_Delivere, dbo.RFPRFQStatus.RFPRFQ_Status, dbo.ProjectRFPRFQ.RFPRFQStatusID
FROM  dbo.ProjectStatus RIGHT OUTER JOIN
         dbo.Project LEFT OUTER JOIN
         dbo.ProjectRFPRFQ ON dbo.Project.ProjectID = dbo.ProjectRFPRFQ.ProjectID LEFT OUTER JOIN
         dbo.RFPRFQStatus ON dbo.ProjectRFPRFQ.RFPRFQStatusID = dbo.RFPRFQStatus.RFPRFQSTATUSID ON dbo.ProjectStatus.ProjectStatusID = dbo.Project.ProjectStatusID LEFT OUTER JOIN
         dbo.Customer ON dbo.Project.CustomerID = dbo.Customer.CustomerID LEFT OUTER JOIN
         dbo.Team ON dbo.Customer.TeamID = dbo.Team.ProjectTeamID LEFT OUTER JOIN
         dbo.ProjectFeasibility ON dbo.Project.ProjectID = dbo.ProjectFeasibility.ProjectID LEFT OUTER JOIN
         dbo.ProjectSelectedIGA ON dbo.Project.ProjectID = dbo.ProjectSelectedIGA.ProjectID
|
|1|dbo|v_Utilities|CREATE VIEW dbo.v_Utilities
AS
SELECT        dbo.UtilityMeter.UtilityMeterID, dbo.UtilityMeter.CustomerID, dbo.UtilityMeter.UtilityAccountID, dbo.UtilityMeter.FacilityID, dbo.UtilityMeter.FuelCodeID, dbo.UtilityMeter.UtilityTypeID, dbo.UtilityProvider.Utility_Provider, 
                         dbo.UtilityAccount.Account_Number, dbo.Facility.Facility_Name, dbo.EnergyConversionFactor.Fuel_Type, dbo.Customer.Customer_Name, dbo.UtilityType.Utility_Type, dbo.UtilityMeter.Meter_Number, 
                         dbo.UtilityMeter.Service_Address, dbo.UtilityMeter.Utility_Rate, dbo.UtilityMeter.Cost_Calculation_Method, dbo.UtilityMeter.Notes
FROM            dbo.UtilityMeter INNER JOIN
                         dbo.UtilityAccount ON dbo.UtilityMeter.UtilityAccountID = dbo.UtilityAccount.UtilityAccountID INNER JOIN
                         dbo.UtilityProvider ON dbo.UtilityAccount.UtilityProviderID = dbo.UtilityProvider.UtilityProviderID INNER JOIN
                         dbo.Facility ON dbo.UtilityMeter.FacilityID = dbo.Facility.FacilityID AND dbo.UtilityMeter.FacilityID = dbo.Facility.FacilityID INNER JOIN
                         dbo.Customer ON dbo.UtilityMeter.CustomerID = dbo.Customer.CustomerID AND dbo.Facility.CustomerID = dbo.Customer.CustomerID INNER JOIN
                         dbo.EnergyConversionFactor ON dbo.UtilityMeter.FuelCodeID = dbo.EnergyConversionFactor.FuelCodeID INNER JOIN
                         dbo.UtilityType ON dbo.UtilityMeter.UtilityTypeID = dbo.UtilityType.UtilityTypeID AND dbo.UtilityMeter.UtilityTypeID = dbo.UtilityType.UtilityTypeID
|
|4|sys|database_firewall_rules|CREATE VIEW sys.database_firewall_rules AS SELECT id, name, start_ip_address, end_ip_address, create_date, modify_date FROM sys.database_firewall_rules_table|
