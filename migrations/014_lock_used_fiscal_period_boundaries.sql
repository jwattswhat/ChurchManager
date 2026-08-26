-- Protect historical posting and adopted-budget period boundaries from later edits.
DELIMITER $$
CREATE TRIGGER trg_acct_period_lock_used_boundaries
BEFORE UPDATE ON tblAccountingFiscalPeriod
FOR EACH ROW
BEGIN
    IF (
        NOT (NEW.FiscalYearID <=> OLD.FiscalYearID)
        OR NOT (NEW.PeriodNumber <=> OLD.PeriodNumber)
        OR NOT (NEW.StartDate <=> OLD.StartDate)
        OR NOT (NEW.EndDate <=> OLD.EndDate)
    ) AND (
        EXISTS (
            SELECT 1 FROM tblAccountingTransaction t
            WHERE t.FiscalPeriodID=OLD.ID AND t.Status IN ('POSTED','REVERSED')
        )
        OR EXISTS (
            SELECT 1 FROM tblAccountingBudgetLine l
            JOIN tblAccountingBudget b ON b.ID=l.BudgetID
            WHERE l.FiscalPeriodID=OLD.ID AND b.Status='ADOPTED'
        )
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='This fiscal period is locked by posted transactions or an adopted budget.';
    END IF;
END$$
DELIMITER ;
