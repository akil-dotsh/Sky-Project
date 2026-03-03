-- ============================================================
-- triggers.sql - Business Rules (Minimum Cardinalities)
-- Enforced at "activation" time (Draft -> Active)
--
-- Rule 1: Organization Active => >= 2 Active Departments
-- Rule 2: Department Active   => >= 3 Active Teams
-- Rule 3: Team Active         => >= 5 members (distinct users)
-- ============================================================

PRAGMA foreign_keys = ON;

-- Rule 1: Organization must have at least 2 ACTIVE Departments to become Active
CREATE TRIGGER IF NOT EXISTS trg_org_activate_requires_2_active_departments
BEFORE UPDATE OF status ON Organization
FOR EACH ROW
WHEN NEW.status = 'Active'
BEGIN
  SELECT CASE
    WHEN (
      SELECT COUNT(*)
      FROM Department
      WHERE organization_id = NEW.organization_id
        AND status = 'Active'
    ) < 2
    THEN RAISE(ABORT, 'Cannot activate Organization: must have at least 2 Active Departments')
  END;
END;

-- Rule 2: Department must have at least 3 ACTIVE Teams to become Active
CREATE TRIGGER IF NOT EXISTS trg_department_activate_requires_3_active_teams
BEFORE UPDATE OF status ON Department
FOR EACH ROW
WHEN NEW.status = 'Active'
BEGIN
  SELECT CASE
    WHEN (
      SELECT COUNT(*)
      FROM Team
      WHERE department_id = NEW.department_id
        AND status = 'Active'
    ) < 3
    THEN RAISE(ABORT, 'Cannot activate Department: must have at least 3 Active Teams')
  END;
END;

-- Rule 3: Team must have at least 5 MEMBERS to become Active
-- (A user can belong to 0 teams if he/she isn't assign to any team yet.)
CREATE TRIGGER IF NOT EXISTS trg_team_activate_requires_5_members
BEFORE UPDATE OF status ON Team
FOR EACH ROW
WHEN NEW.status = 'Active'
BEGIN
  SELECT CASE
    WHEN (
      SELECT COUNT(DISTINCT user_id)
      FROM TeamMember
      WHERE team_id = NEW.team_id
    ) < 5
    THEN RAISE(ABORT, 'Cannot activate Team: must have at least 5 Members')
  END;
END;
