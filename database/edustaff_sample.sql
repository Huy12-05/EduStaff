-- ============================================================
--  EduStaff — Sample Database (MySQL 8.0+)
--  Mật khẩu mẫu:  admin / admin123  |  staff / staff123
--  Chạy: mysql -u root -p < edustaff_sample.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS edustaff
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE edustaff;

-- ------------------------------------------------------------
--  ACCOUNTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    full_name     VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'staff',
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
--  DEPARTMENTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(20)  NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    is_deleted   TINYINT(1)   NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
--  LECTURERS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lecturers (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(50)  NOT NULL UNIQUE,
    full_name     VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    phone         VARCHAR(30)  NOT NULL,
    gender        VARCHAR(20)  NOT NULL,
    date_of_birth DATE         NOT NULL,
    degree        VARCHAR(50)  NOT NULL,
    position      VARCHAR(100) NOT NULL,
    department_id INT          NOT NULL,
    hire_date     DATE         NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'active',
    is_deleted    TINYINT(1)   NOT NULL DEFAULT 0,
    FOREIGN KEY (department_id) REFERENCES departments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
--  SCHEDULES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schedules (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    lecturer_id   INT          NOT NULL,
    subject_name  VARCHAR(255) NOT NULL,
    subject_code  VARCHAR(50)  NOT NULL,
    room          VARCHAR(50)  NOT NULL,
    day_of_week   VARCHAR(10)  NOT NULL,
    start_time    TIME         NOT NULL,
    end_time      TIME         NOT NULL,
    semester      VARCHAR(20)  NOT NULL,
    academic_year VARCHAR(20)  NOT NULL,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
--  AUDIT LOGS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    action      VARCHAR(50)  NOT NULL,
    entity_type VARCHAR(50)  NOT NULL,
    entity_id   INT,
    details     TEXT,
    username    VARCHAR(100) NOT NULL,
    ip_address  VARCHAR(50),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  DATA: ACCOUNTS  (password: admin123 / staff123)
-- ============================================================
INSERT INTO accounts (username, full_name, role, is_active, password_hash, created_at) VALUES
('admin',    'Quản Trị Viên',      'admin', TRUE,  '$2b$12$RdqgNYrYpzcDar33nxM1KOIofy7bEJDQYpq6BfAc5tPxL6So1.5qS', '2024-08-01 08:00:00'),
('ngoclan',  'Trần Ngọc Lan',      'staff', TRUE,  '$2b$12$e.IkuttiUFAwfUbpg9H8Oe3StH/zQ/hWq73HbpNG.U8xX.tjsWO7.', '2024-08-02 09:00:00'),
('minhkhoa', 'Lê Minh Khoa',       'staff', TRUE,  '$2b$12$e.IkuttiUFAwfUbpg9H8Oe3StH/zQ/hWq73HbpNG.U8xX.tjsWO7.', '2024-08-03 09:30:00'),
('thuhuong', 'Phạm Thu Hương',     'staff', TRUE,  '$2b$12$e.IkuttiUFAwfUbpg9H8Oe3StH/zQ/hWq73HbpNG.U8xX.tjsWO7.', '2024-09-01 08:00:00'),
('vandat',   'Nguyễn Văn Đạt',     'staff', FALSE, '$2b$12$e.IkuttiUFAwfUbpg9H8Oe3StH/zQ/hWq73HbpNG.U8xX.tjsWO7.', '2024-09-15 10:00:00');

-- ============================================================
--  DATA: DEPARTMENTS  (8 khoa)
-- ============================================================
INSERT INTO departments (code, name, description) VALUES
('CNTT',   'Công nghệ Thông tin',         'Đào tạo kỹ sư phần mềm, mạng máy tính, trí tuệ nhân tạo và khoa học dữ liệu.'),
('KTDDT',  'Kỹ thuật Điện – Điện tử',    'Đào tạo kỹ sư điện, tự động hóa, hệ thống nhúng và điện tử viễn thông.'),
('COKHI',  'Cơ khí',                      'Đào tạo kỹ sư cơ khí chế tạo máy, cơ điện tử và kỹ thuật công nghiệp.'),
('XDCD',   'Xây dựng Dân dụng',          'Đào tạo kỹ sư xây dựng công trình dân dụng, cầu đường và kết cấu.'),
('KTTE',   'Kinh tế',                     'Đào tạo cử nhân quản trị kinh doanh, kế toán, tài chính và thương mại.'),
('NGOAINGU','Ngoại ngữ',                  'Đào tạo cử nhân tiếng Anh, tiếng Trung, tiếng Nhật và ngôn ngữ học.'),
('LLCT',   'Lý luận Chính trị',           'Giảng dạy các môn lý luận Mác–Lênin, tư tưởng Hồ Chí Minh và lịch sử Đảng.'),
('GDTC',   'Giáo dục Thể chất',           'Giảng dạy giáo dục thể chất, bơi lội, võ thuật và thể thao học đường.');

-- ============================================================
--  DATA: LECTURERS  (30 giảng viên)
-- ============================================================
INSERT INTO lecturers (employee_code, full_name, email, phone, gender, date_of_birth, degree, position, department_id, hire_date, status) VALUES
-- CNTT (dept 1) — 6 người
('GV001', 'Nguyễn Văn An',      'nvan.an@eaut.edu.vn',      '0901234501', 'Nam',  '1978-03-15', 'TS',  'Trưởng khoa',        1, '2005-08-01', 'active'),
('GV002', 'Trần Thị Bích',      'tthi.bich@eaut.edu.vn',    '0901234502', 'Nữ',   '1983-07-22', 'ThS', 'Giảng viên chính',   1, '2009-09-01', 'active'),
('GV003', 'Lê Minh Cường',      'lm.cuong@eaut.edu.vn',     '0901234503', 'Nam',  '1985-11-10', 'TS',  'Phó trưởng khoa',    1, '2011-08-01', 'active'),
('GV004', 'Phạm Thị Dung',      'pthi.dung@eaut.edu.vn',    '0901234504', 'Nữ',   '1990-04-05', 'ThS', 'Giảng viên',         1, '2015-09-01', 'active'),
('GV005', 'Võ Quốc Hùng',       'vq.hung@eaut.edu.vn',      '0901234505', 'Nam',  '1987-08-18', 'PGS', 'Giảng viên cao cấp', 1, '2013-08-01', 'active'),
('GV006', 'Đặng Thị Kim',       'dthi.kim@eaut.edu.vn',     '0901234506', 'Nữ',   '1993-01-29', 'ThS', 'Giảng viên',         1, '2019-09-01', 'on_leave'),

-- KTDDT (dept 2) — 4 người
('GV007', 'Hoàng Văn Long',     'hv.long@eaut.edu.vn',      '0901234507', 'Nam',  '1975-06-12', 'GS',  'Trưởng khoa',        2, '2001-08-01', 'active'),
('GV008', 'Nguyễn Thị Mai',     'nthi.mai@eaut.edu.vn',     '0901234508', 'Nữ',   '1984-09-30', 'TS',  'Giảng viên chính',   2, '2010-09-01', 'active'),
('GV009', 'Bùi Quang Nam',      'bq.nam@eaut.edu.vn',       '0901234509', 'Nam',  '1988-12-07', 'ThS', 'Giảng viên',         2, '2014-08-01', 'active'),
('GV010', 'Trịnh Thị Oanh',     'tthi.oanh@eaut.edu.vn',    '0901234510', 'Nữ',   '1992-03-14', 'ThS', 'Giảng viên',         2, '2018-09-01', 'inactive'),

-- COKHI (dept 3) — 3 người
('GV011', 'Phan Văn Phúc',      'pv.phuc@eaut.edu.vn',      '0901234511', 'Nam',  '1979-05-20', 'PGS', 'Trưởng khoa',        3, '2004-08-01', 'active'),
('GV012', 'Lý Thị Quỳnh',       'lthi.quynh@eaut.edu.vn',   '0901234512', 'Nữ',   '1986-10-08', 'TS',  'Giảng viên chính',   3, '2012-09-01', 'active'),
('GV013', 'Trần Văn Sơn',       'tv.son@eaut.edu.vn',       '0901234513', 'Nam',  '1991-02-25', 'ThS', 'Giảng viên',         3, '2016-08-01', 'active'),

-- XDCD (dept 4) — 3 người
('GV014', 'Ngô Thị Thanh',      'nthi.thanh@eaut.edu.vn',   '0901234514', 'Nữ',   '1980-07-17', 'TS',  'Trưởng khoa',        4, '2006-08-01', 'active'),
('GV015', 'Đinh Văn Toàn',      'dv.toan@eaut.edu.vn',      '0901234515', 'Nam',  '1985-04-03', 'ThS', 'Giảng viên chính',   4, '2011-09-01', 'active'),
('GV016', 'Cao Thị Uyên',       'cthi.uyen@eaut.edu.vn',    '0901234516', 'Nữ',   '1994-11-28', 'ThS', 'Giảng viên',         4, '2020-09-01', 'active'),

-- KTTE (dept 5) — 4 người
('GV017', 'Lê Văn Vinh',        'lv.vinh@eaut.edu.vn',      '0901234517', 'Nam',  '1977-08-09', 'PGS', 'Trưởng khoa',        5, '2003-08-01', 'active'),
('GV018', 'Phạm Thị Xuân',      'pthi.xuan@eaut.edu.vn',    '0901234518', 'Nữ',   '1982-01-16', 'TS',  'Phó trưởng khoa',    5, '2008-09-01', 'active'),
('GV019', 'Vũ Trọng Yên',       'vt.yen@eaut.edu.vn',       '0901234519', 'Nam',  '1989-06-24', 'ThS', 'Giảng viên chính',   5, '2015-08-01', 'active'),
('GV020', 'Đỗ Thị Yến',         'dthi.yen@eaut.edu.vn',     '0901234520', 'Nữ',   '1995-09-11', 'ThS', 'Giảng viên',         5, '2021-09-01', 'active'),

-- NGOAINGU (dept 6) — 3 người
('GV021', 'Hà Văn Bảo',         'hv.bao@eaut.edu.vn',       '0901234521', 'Nam',  '1981-03-06', 'TS',  'Trưởng khoa',        6, '2007-08-01', 'active'),
('GV022', 'Nguyễn Thị Cẩm',     'nthi.cam@eaut.edu.vn',     '0901234522', 'Nữ',   '1987-07-19', 'ThS', 'Giảng viên chính',   6, '2013-09-01', 'active'),
('GV023', 'Trần Quang Dũng',    'tq.dung@eaut.edu.vn',      '0901234523', 'Nam',  '1993-12-02', 'ThS', 'Giảng viên',         6, '2019-08-01', 'on_leave'),

-- LLCT (dept 7) — 4 người
('GV024', 'Bùi Thị Giang',      'bthi.giang@eaut.edu.vn',   '0901234524', 'Nữ',   '1976-05-28', 'TS',  'Trưởng khoa',        7, '2002-08-01', 'active'),
('GV025', 'Hoàng Văn Hải',      'hv.hai@eaut.edu.vn',       '0901234525', 'Nam',  '1983-10-15', 'ThS', 'Giảng viên chính',   7, '2009-09-01', 'active'),
('GV026', 'Lê Thị Hồng',        'lthi.hong@eaut.edu.vn',    '0901234526', 'Nữ',   '1988-02-22', 'ThS', 'Giảng viên',         7, '2014-08-01', 'active'),
('GV027', 'Võ Đình Khải',       'vd.khai@eaut.edu.vn',      '0901234527', 'Nam',  '1994-08-07', 'ThS', 'Giảng viên',         7, '2020-09-01', 'inactive'),

-- GDTC (dept 8) — 3 người
('GV028', 'Phan Thị Liên',      'pthi.lien@eaut.edu.vn',    '0901234528', 'Nữ',   '1979-11-04', 'TS',  'Trưởng khoa',        8, '2005-08-01', 'active'),
('GV029', 'Trương Văn Minh',    'tv.minh@eaut.edu.vn',      '0901234529', 'Nam',  '1986-04-13', 'ThS', 'Giảng viên chính',   8, '2012-09-01', 'active'),
('GV030', 'Đinh Thị Nga',       'dthi.nga@eaut.edu.vn',     '0901234530', 'Nữ',   '1992-07-26', 'ThS', 'Giảng viên',         8, '2018-08-01', 'active');

-- ============================================================
--  DATA: SCHEDULES  (40 lịch giảng dạy)
-- ============================================================
INSERT INTO schedules (lecturer_id, subject_name, subject_code, room, day_of_week, start_time, end_time, semester, academic_year) VALUES
-- GV001
(1,  'Lập trình Python',            'CS101', 'A101', 'Mon', '07:00', '09:30', 'HK1', '2025-2026'),
(1,  'Trí tuệ Nhân tạo',            'CS401', 'A201', 'Wed', '13:00', '15:30', 'HK1', '2025-2026'),
-- GV002
(2,  'Lập trình Web',               'CS201', 'B102', 'Tue', '07:00', '09:30', 'HK1', '2025-2026'),
(2,  'Cơ sở Dữ liệu',              'CS202', 'B203', 'Thu', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV003
(3,  'Mạng Máy tính',               'CS301', 'C101', 'Mon', '09:45', '12:15', 'HK1', '2025-2026'),
(3,  'Bảo mật Hệ thống',            'CS302', 'C202', 'Fri', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV004
(4,  'Giải thuật & Lập trình',      'CS102', 'A102', 'Tue', '09:45', '12:15', 'HK1', '2025-2026'),
(4,  'Kỹ thuật Phần mềm',          'CS203', 'B104', 'Wed', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV005
(5,  'Học máy',                     'CS501', 'A301', 'Thu', '13:00', '15:30', 'HK1', '2025-2026'),
(5,  'Khoa học Dữ liệu',           'CS502', 'A302', 'Sat', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV007
(7,  'Điện tử Cơ bản',              'EE101', 'D101', 'Mon', '13:00', '15:30', 'HK1', '2025-2026'),
(7,  'Kỹ thuật Vi xử lý',          'EE301', 'D201', 'Wed', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV008
(8,  'Mạch điện',                   'EE102', 'D102', 'Tue', '13:00', '15:30', 'HK1', '2025-2026'),
(8,  'Điều khiển Tự động',          'EE302', 'D202', 'Thu', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV009
(9,  'Điện tử Công suất',           'EE201', 'D103', 'Fri', '09:45', '12:15', 'HK1', '2025-2026'),
(9,  'Hệ thống Nhúng',              'EE401', 'D301', 'Sat', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV011
(11, 'Cơ học Vật liệu',            'ME101', 'E101', 'Mon', '07:00', '09:30', 'HK1', '2025-2026'),
(11, 'Công nghệ Chế tạo',          'ME301', 'E201', 'Wed', '13:00', '15:30', 'HK1', '2025-2026'),
-- GV012
(12, 'Thiết kế CAD/CAM',           'ME201', 'E102', 'Tue', '07:00', '09:30', 'HK1', '2025-2026'),
(12, 'Cơ điện tử',                 'ME401', 'E301', 'Thu', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV014
(14, 'Cơ học Kết cấu',             'CE101', 'F101', 'Mon', '09:45', '12:15', 'HK1', '2025-2026'),
(14, 'Bê tông Cốt thép',           'CE301', 'F201', 'Fri', '13:00', '15:30', 'HK1', '2025-2026'),
-- GV015
(15, 'Vật liệu Xây dựng',          'CE102', 'F102', 'Tue', '09:45', '12:15', 'HK1', '2025-2026'),
(15, 'Kỹ thuật Công trình',        'CE201', 'F203', 'Thu', '13:00', '15:30', 'HK1', '2025-2026'),
-- GV017
(17, 'Kinh tế Vi mô',               'EC101', 'G101', 'Mon', '13:00', '15:30', 'HK1', '2025-2026'),
(17, 'Quản trị Chiến lược',         'EC401', 'G201', 'Wed', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV018
(18, 'Kế toán Tài chính',           'EC201', 'G102', 'Tue', '13:00', '15:30', 'HK1', '2025-2026'),
(18, 'Phân tích Tài chính',         'EC301', 'G203', 'Fri', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV021
(21, 'Tiếng Anh Chuyên ngành',      'EL101', 'H101', 'Mon', '07:00', '09:30', 'HK1', '2025-2026'),
(21, 'Ngôn ngữ học Ứng dụng',      'EL301', 'H201', 'Wed', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV022
(22, 'Tiếng Trung Cơ bản',          'ZH101', 'H102', 'Tue', '07:00', '09:30', 'HK1', '2025-2026'),
(22, 'Phiên dịch Tiếng Anh',        'EL201', 'H103', 'Thu', '07:00', '09:30', 'HK1', '2025-2026'),
-- GV024
(24, 'Triết học Mác–Lênin',         'ML101', 'I101', 'Mon', '09:45', '12:15', 'HK1', '2025-2026'),
(24, 'Tư tưởng Hồ Chí Minh',       'ML201', 'I201', 'Thu', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV025
(25, 'Kinh tế Chính trị',           'ML102', 'I102', 'Tue', '09:45', '12:15', 'HK1', '2025-2026'),
(25, 'Lịch sử Đảng CSVN',          'ML202', 'I202', 'Fri', '09:45', '12:15', 'HK1', '2025-2026'),
-- GV028
(28, 'Giáo dục Thể chất 1',         'PE101', 'J101', 'Wed', '07:00', '09:30', 'HK1', '2025-2026'),
(28, 'Võ thuật Cơ bản',             'PE201', 'J201', 'Fri', '13:00', '15:30', 'HK1', '2025-2026'),
-- GV029
(29, 'Bơi lội',                     'PE102', 'J102', 'Tue', '13:00', '15:30', 'HK1', '2025-2026'),
(29, 'Thể thao Đồng đội',           'PE301', 'J301', 'Sat', '13:00', '15:30', 'HK1', '2025-2026');

-- ============================================================
--  DATA: AUDIT LOGS  (30 bản ghi)
-- ============================================================
INSERT INTO audit_logs (action, entity_type, entity_id, details, username, ip_address, created_at) VALUES
('login',  'account',    1,  'Đăng nhập thành công',                         'admin',    '192.168.1.10', '2025-01-10 07:58:00'),
('create', 'department', 1,  'Tạo khoa CNTT',                                'admin',    '192.168.1.10', '2025-01-10 08:05:00'),
('create', 'department', 2,  'Tạo khoa KTDDT',                               'admin',    '192.168.1.10', '2025-01-10 08:08:00'),
('create', 'department', 3,  'Tạo khoa COKHI',                               'admin',    '192.168.1.10', '2025-01-10 08:10:00'),
('create', 'department', 4,  'Tạo khoa XDCD',                                'admin',    '192.168.1.10', '2025-01-10 08:12:00'),
('create', 'department', 5,  'Tạo khoa KTTE',                                'admin',    '192.168.1.10', '2025-01-10 08:14:00'),
('create', 'department', 6,  'Tạo khoa NGOAINGU',                            'admin',    '192.168.1.10', '2025-01-10 08:16:00'),
('create', 'department', 7,  'Tạo khoa LLCT',                                'admin',    '192.168.1.10', '2025-01-10 08:18:00'),
('create', 'department', 8,  'Tạo khoa GDTC',                                'admin',    '192.168.1.10', '2025-01-10 08:20:00'),
('create', 'account',    2,  'Tạo tài khoản staff: ngoclan',                 'admin',    '192.168.1.10', '2025-01-10 08:30:00'),
('create', 'account',    3,  'Tạo tài khoản staff: minhkhoa',                'admin',    '192.168.1.10', '2025-01-10 08:32:00'),
('create', 'account',    4,  'Tạo tài khoản staff: thuhuong',                'admin',    '192.168.1.10', '2025-01-10 08:34:00'),
('login',  'account',    2,  'Đăng nhập thành công',                         'ngoclan',  '192.168.1.11', '2025-01-11 08:00:00'),
('create', 'lecturer',   1,  'Thêm giảng viên GV001 Nguyễn Văn An',         'ngoclan',  '192.168.1.11', '2025-01-11 08:15:00'),
('create', 'lecturer',   2,  'Thêm giảng viên GV002 Trần Thị Bích',         'ngoclan',  '192.168.1.11', '2025-01-11 08:30:00'),
('create', 'lecturer',   3,  'Thêm giảng viên GV003 Lê Minh Cường',         'ngoclan',  '192.168.1.11', '2025-01-11 08:45:00'),
('login',  'account',    3,  'Đăng nhập thành công',                         'minhkhoa', '192.168.1.12', '2025-01-12 08:00:00'),
('create', 'lecturer',   7,  'Thêm giảng viên GV007 Hoàng Văn Long',        'minhkhoa', '192.168.1.12', '2025-01-12 08:20:00'),
('create', 'lecturer',   11, 'Thêm giảng viên GV011 Phan Văn Phúc',        'minhkhoa', '192.168.1.12', '2025-01-12 08:40:00'),
('update', 'lecturer',   6,  'Cập nhật trạng thái GV006 → on_leave',        'admin',    '192.168.1.10', '2025-02-01 09:00:00'),
('update', 'lecturer',   10, 'Cập nhật trạng thái GV010 → inactive',        'admin',    '192.168.1.10', '2025-02-01 09:05:00'),
('update', 'lecturer',   27, 'Cập nhật trạng thái GV027 → inactive',        'admin',    '192.168.1.10', '2025-02-01 09:10:00'),
('create', 'schedule',   1,  'Thêm lịch CS101 — GV001 — Thứ 2',            'ngoclan',  '192.168.1.11', '2025-02-10 10:00:00'),
('create', 'schedule',   2,  'Thêm lịch CS401 — GV001 — Thứ 4',            'ngoclan',  '192.168.1.11', '2025-02-10 10:05:00'),
('create', 'account',    5,  'Tạo tài khoản staff: vandat',                  'admin',    '192.168.1.10', '2025-03-01 08:00:00'),
('login',  'account',    1,  'Đăng nhập thành công',                         'admin',    '192.168.1.10', '2025-03-15 07:55:00'),
('update', 'account',    5,  'Khóa tài khoản vandat (is_active → false)',    'admin',    '192.168.1.10', '2025-03-15 08:00:00'),
('delete', 'schedule',   NULL, 'Xóa lịch trùng — CS302 Thứ 6',             'admin',    '192.168.1.10', '2025-03-20 14:00:00'),
('login',  'account',    4,  'Đăng nhập thành công',                         'thuhuong', '192.168.1.13', '2025-04-01 08:00:00'),
('update', 'lecturer',   23, 'Cập nhật trạng thái GV023 → on_leave',        'thuhuong', '192.168.1.13', '2025-04-01 08:30:00');
