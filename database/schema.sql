PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Organization (
    organization_id   INTEGER PRIMARY KEY,
    organization_name TEXT NOT NULL,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    hq_location       TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'Draft' CHECK (status IN('Draft', 'Active','Deactive')),
    website_url       TEXT,
    contact_email     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "User" (
    user_id             INTEGER PRIMARY KEY,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    email               TEXT NOT NULL UNIQUE,
    dob                 TEXT NOT NULL,                       -- YYYY-MM-DD
    password_hash       TEXT NOT NULL,
    address             TEXT NOT NULL,
    date_joined         TEXT NOT NULL  DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),    -- ISO date/time
    is_active           INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    phone_number        TEXT NOT NULL UNIQUE,
    role                TEXT,
    profile_picture_url TEXT,
    bio                 TEXT,
    last_login          TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),               -- ISO date/time
    office_location     TEXT,
    availability_status TEXT CHECK (availability_status IN ('Available','Busy','On Leave','Remote'))
    team_id             INTEGER NOT NULL,

    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Department (
    department_id    INTEGER PRIMARY KEY,
    department_name  TEXT NOT NULL,
    description      TEXT,
    status           TEXT NOT NULL DEFAULT 'Draft' CHECK (status IN('Draft', 'Active','Deactive')),
    created_at       TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    department_email TEXT NOT NULL,

    -- Department belongs to exactly one Organization (NOT NULL)
    organization_id  INTEGER NOT NULL,

    -- department head is a user
    deptHead_id      INTEGER NOT NULL,

    FOREIGN KEY (organization_id) REFERENCES Organization(organization_id) ON DELETE RESTRICT,
    FOREIGN KEY (deptHead_id)     REFERENCES  "User"(user_id)              ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS JiraBoard (
    jiraBoard_id INTEGER PRIMARY KEY,
    board_name   TEXT NOT NULL,
    board_type   TEXT NOT NULL DEFAULT 'Scrum' CHECK (board_type IN ('Scrum','Kanban','Backlog','Bug Tracking')),
    is_active    INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at   TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at   TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS JiraProject (
    jira_project_id INTEGER PRIMARY KEY,
    project_name    TEXT NOT NULL,
    description     TEXT,
    project_type    TEXT NOT NULL DEFAULT 'Software' CHECK (project_type IN ('Software','Service','Infrastructure','Research','Maintenance','Support')),
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    status          TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active','On Hold','Completed','Archived')),

    -- each project belongs to one board
    jiraBoard_id    INTEGER NOT NULL,
    FOREIGN KEY (jiraBoard_id) REFERENCES JiraBoard(jiraBoard_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Team (
    team_id                 INTEGER PRIMARY KEY,
    team_name               TEXT NOT NULL,

    purpose                 TEXT NOT NULL,
    responsibility          TEXT,
    description             TEXT,
    status                  TEXT NOT NULL DEFAULT 'Draft' CHECK(status in('Draft','Active','Deactive', 'On Hold', 'Archived')),

    created_at              TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at              TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    team_email              TEXT NOT NULL,
    on_call_contact         TEXT NOT NULL, --Emergency Situation
    location                TEXT,
    last_reviewed_at        TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    development_focus_area  TEXT,
    key_skills_technology   TEXT,
    software_owned          TEXT,
    agile_practice          TEXT DEFAULT 'Scrum' CHECK (agile_practice IN ('Scrum','Kanban','Hybrid','Others','None')),
    daily_standup_time      TEXT,
    concurrent_working_range TEXT,
    team_wiki_url           TEXT,

          
    jira_project_id         INTEGER NOT NULL,
    department_id           INTEGER NOT NULL,

    FOREIGN KEY (jira_project_id) REFERENCES JiraProject(jira_project_id) ON DELETE RESTRICT,
    FOREIGN KEY (department_id)   REFERENCES Department(department_id)   ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Dependency (
    dependency_id    INTEGER PRIMARY KEY,
    dependency_name  TEXT NOT NULL,
    description      TEXT,
    created_at       TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    criticality      TEXT NOT NULL DEFAULT 'Medium' CHECK (criticality IN ('Low','Medium','High','Critical')),
    impact_note      TEXT DEFAULT 'No impact recorded',

    owner_contact_id INTEGER NOT NULL, -- Team Leader or Department head number for emergency
);

CREATE TABLE IF NOT EXISTS TeamDependency (
    team_id         INTEGER NOT NULL,
    dependency_id   INTEGER NOT NULL,
    date            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    dependency_type ENUM('Upstream', 'Downstream') NOT NULL
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    impact_note     TEXT NOT NULL,

    PRIMARY KEY (team_id,dependency_id,date),
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE,
    FOREIGN KEY (dependency_id) REFERENCES Dependency(dependency_id) ON DELETE CASCADE


);
CREATE TABLE IF NOT EXISTS Meeting_Participant (
    user_id     INTEGER NOT NULL,
    meeting_id  INTEGER NOT NULL,

    date        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    join_status TEXT NOT NULL  DEFAULT 'Invited' CHECK (join_status IN ('Invited','Accepted','Declined','Joined','No Show')), 
    joined_at   TEXT ,

    PRIMARY KEY (user_id, meeting_id, date),
    FOREIGN KEY (user_id)    REFERENCES "User"(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (meeting_id) REFERENCES Meeting(meeting_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Admin (
    user_id              INTEGER PRIMARY KEY,
    can_manage_users     INTEGER NOT NULL DEFAULT 0 CHECK (can_manage_users IN (0,1)),
    can_manage_teams     INTEGER NOT NULL DEFAULT 0 CHECK (can_manage_teams IN (0,1)),
    can_generate_reports INTEGER NOT NULL DEFAULT 0 CHECK (can_generate_reports IN (0,1)),
    admin_since          TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS DepartmentHead (
    user_id              INTEGER PRIMARY KEY,
    can_manage_users     INTEGER NOT NULL DEFAULT 0 CHECK (can_manage_users IN (0,1)),
    can_manage_teams     INTEGER NOT NULL DEFAULT 0 CHECK (can_manage_teams IN (0,1)),
    can_generate_reports INTEGER NOT NULL DEFAULT 0 CHECK (can_generate_reports IN (0,1)),
    deptHead_since       TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Developer (
    user_id         INTEGER PRIMARY KEY,
    primary_skill   TEXT,
    grade_level     TEXT DEFAULT 'Junior' CHECK (grade_level IN('Junior','Mid', 'Senior','Lead')),
    github_username TEXT,

    leader_id       INTEGER, 
    leader_since    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    FOREIGN KEY (user_id)   REFERENCES "User"(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (leader_id) REFERENCES Developer(user_id) ON DELETE RESTRICT
);



CREATE TABLE IF NOT EXISTS ContactChannel (
    contact_channel_id INTEGER PRIMARY KEY,
    channel_type       TEXT NOT NULL,
    is_primary         INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0,1)),
    created_at         TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    -- each ContactChannel belongs to one Team
    team_id            INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ResourceLink (
    resource_id     INTEGER PRIMARY KEY,
    resource_type   TEXT NOT NULL DEFAULT 'Team Wiki' CHECK(resource_type IN ('Team Wiki','Documentation','report','Search Term')),
    documentation   TEXT,
    description     TEXT,
    resource_value  TEXT,
    report_url      TEXT,
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    -- belongs to Team 
    team_id         INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CodeRepository (
    repo_id         INTEGER PRIMARY KEY,
    repo_name       TEXT NOT NULL,
    repo_url        TEXT NOT NULL,
    platform        TEXT NOT NULL DEFAULT 'GitHub' CHECK(platform IN('GitHub','GitLab','Bitbucket')),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    main_language   TEXT,
    default_branch  TEXT,
    last_commit_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    access_level    TEXT NOT NULL DEFAULT 'Internal' CHECK(access_level IN('Public','Internal','Private')),

    -- belongs to Team
    team_id         INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE
);




CREATE TABLE IF NOT EXISTS Notification (
    notification_id   INTEGER PRIMARY KEY,
    user_id           INTEGER NOT NULL, 
    title             TEXT NOT NULL,
    message           TEXT NOT NULL,
    created_at        TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    notification_type TEXT,
    link_url          TEXT,
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS USER_NOTIFICATION (
    notification_id INTEGER NOT NULL,
    user_id         INTEGER NOT NULL,
    date            TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    delivered_at    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    delivery_status TEXT DEFAULT 'Queued' CHECK (delivery_status IN('Queued','Sent','Delivered','Read','Failed')),
    read_at         TEXT ,

    PRIMARY KEY (notification_id, user_id, date),
    FOREIGN KEY (notification_id) REFERENCES Notification(notification_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)         REFERENCES "User"(user_id)             ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Message (
    message_id      INTEGER PRIMARY KEY,
    recipient_type  TEXT NOT NULL CHECK (recipient_type IN ('Individual','Team')),
    recipient_id    INTEGER,
    recipient_team_id INTEGER,
    subject         TEXT NOT NULL,
    body            TEXT NOT NULL,
    sent_at         TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    status          TEXT DEFAULT 'Queued' CHECK (status IN('Queued','Sent','Delivered','Read','Failed')),
    attachment_url  TEXT,
    read_at         TEXT ,

    sended_user_id         INTEGER NOT NULL,
    FOREIGN KEY (sended_user_id) REFERENCES "User"(user_id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id)  REFERENCES "User"(user_id) ON DELETE CASCADE,

    FOREIGN KEY (recipient_team_id) REFERENCES Team(team_id) ON DELETE SET NULL,

    CHECK (
      (recipient_type = 'Individual' AND recipient_id IS NOT NULL AND recipient_team_id IS NULL)
      OR
      (recipient_type = 'Team' AND recipient_team_id IS NOT NULL AND recipient_id IS NULL)
    )
);


CREATE TABLE IF NOT EXISTS Meeting (
    meeting_id          INTEGER PRIMARY KEY,

    organiser_user_id   INTEGER NOT NULL,
    meeting_type TEXT NOT NULL CHECK (meeting_type IN ('Individual','Team')),
    receiver_user_id    INTEGER,
    team_id             INTEGER,

    title               TEXT NOT NULL,
    start_datetime      TEXT NOT NULL,
    end_datetime        TEXT NOT NULL,
    location            TEXT,
    agenda              TEXT NOT NULL,
    meeting_link        TEXT NOT NULL,
    created_at          TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    FOREIGN KEY (organiser_user_id) REFERENCES "User"(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (receiver_user_id)  REFERENCES "User"(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (team_id)           REFERENCES Team(team_id)   ON DELETE SET NULL,

    CHECK (meeting_type = 'Team' OR organiser_user_id <> receiver_user_id),

    CHECK ((meeting_type = 'Individual' AND receiver_user_id IS NOT NULL AND team_id IS NULL)
            OR
            (meeting_type = 'Team' AND team_id IS NOT NULL AND receiver_user_id IS NULL)),

    CHECK (end_datetime > start_datetime)
);

CREATE TABLE IF NOT EXISTS Meeting_Participant (
    user_id     INTEGER NOT NULL,
    meeting_id  INTEGER NOT NULL,

    date        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

    join_status TEXT NOT NULL  DEFAULT 'Invited' CHECK (join_status IN ('Invited','Accepted','Declined','Joined','No Show')), 
    joined_at   TEXT ,

    PRIMARY KEY (user_id, meeting_id, date),
    FOREIGN KEY (user_id)    REFERENCES "User"(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (meeting_id) REFERENCES Meeting(meeting_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS auditLog (
    audit_id         INTEGER PRIMARY KEY,
    entity_name      TEXT,
    action           TEXT,
    changed_by_name  TEXT NOT NULL,
    changed_at       TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    change_summary   TEXT,

    user_id          INTEGER,
    FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE SET NULL
);


CREATE INDEX IF NOT EXISTS idx_team_department      ON Team(department_id);
CREATE INDEX IF NOT EXISTS idx_team_jira_project    ON Team(jira_project_id);
CREATE INDEX IF NOT EXISTS idx_teammember_user      ON TeamMember(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_user    ON Notification(user_id);
CREATE INDEX IF NOT EXISTS idx_meeting_team         ON Meeting(team_id);
