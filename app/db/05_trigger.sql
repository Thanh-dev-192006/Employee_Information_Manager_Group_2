DELIMITER $$

-- 1. Trigger khi INSERT (Thêm mới thưởng/phạt)
DROP TRIGGER IF EXISTS trg_after_bonus_insert $$
CREATE TRIGGER trg_after_bonus_insert
AFTER INSERT ON bonus_deductions
FOR EACH ROW
BEGIN
    INSERT INTO bonus_deduction_log(
        bd_id, employee_id, description, bd_type, 
        action, amount, effective_date, log_time
    )
    VALUES(
        NEW.bd_id, NEW.employee_id, NEW.description, NEW.bd_type, 
        'INSERT', NEW.amount, NEW.effective_date, NOW()
    );
END $$

-- 2. Trigger khi UPDATE (Cập nhật thưởng/phạt)
DROP TRIGGER IF EXISTS trg_after_bonus_update $$
CREATE TRIGGER trg_after_bonus_update
AFTER UPDATE ON bonus_deductions
FOR EACH ROW
BEGIN
    INSERT INTO bonus_deduction_log(
        bd_id, employee_id, description, bd_type, 
        action, amount, old_amount, effective_date, log_time
    )
    VALUES(
        NEW.bd_id, NEW.employee_id, NEW.description, NEW.bd_type, 
        'UPDATE', NEW.amount, OLD.amount, NEW.effective_date, NOW()
    );
END $$

-- 3. Trigger khi DELETE (Xóa thưởng/phạt)
DROP TRIGGER IF EXISTS trg_after_bonus_delete $$
CREATE TRIGGER trg_after_bonus_delete
AFTER DELETE ON bonus_deductions
FOR EACH ROW
BEGIN
    INSERT INTO bonus_deduction_log(
        bd_id, employee_id, description, bd_type, 
        action, amount, effective_date, log_time
    )
    VALUES(
        OLD.bd_id, OLD.employee_id, OLD.description, OLD.bd_type, 
        'DELETE', OLD.amount, OLD.effective_date, NOW()
    );
END $$

DELIMITER ;