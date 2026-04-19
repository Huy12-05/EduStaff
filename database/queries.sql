-- ============================================================
--  EduStaff — Bộ câu truy vấn bổ sung
--  Database: edustaff  |  MySQL 8.0+
-- ============================================================

USE edustaff;

-- ============================================================
--  1. TỔNG QUAN HỆ THỐNG
-- ============================================================

-- 1.1 Thống kê tổng số toàn hệ thống
SELECT
    (SELECT COUNT(*) FROM lecturers  WHERE is_deleted = 0)              AS tong_giang_vien,
    (SELECT COUNT(*) FROM departments WHERE is_deleted = 0)             AS tong_khoa,
    (SELECT COUNT(*) FROM schedules)                                     AS tong_lich_day,
    (SELECT COUNT(*) FROM accounts  WHERE is_active = 1)                AS tai_khoan_hoat_dong,
    (SELECT COUNT(*) FROM lecturers  WHERE status = 'active'
                                     AND is_deleted = 0)                AS giang_vien_dang_day,
    (SELECT COUNT(*) FROM lecturers  WHERE status = 'on_leave'
                                     AND is_deleted = 0)                AS dang_nghi_phep;


-- 1.2 Số giảng viên theo từng khoa (kèm % tổng)
SELECT
    d.code                                          AS ma_khoa,
    d.name                                          AS ten_khoa,
    COUNT(l.id)                                     AS so_giang_vien,
    ROUND(COUNT(l.id) * 100.0
        / NULLIF((SELECT COUNT(*) FROM lecturers WHERE is_deleted = 0), 0), 1) AS phan_tram
FROM departments d
LEFT JOIN lecturers l ON l.department_id = d.id AND l.is_deleted = 0
WHERE d.is_deleted = 0
GROUP BY d.id, d.code, d.name
ORDER BY so_giang_vien DESC;


-- 1.3 Số giảng viên theo học hàm / học vị
SELECT
    degree                  AS hoc_vi,
    COUNT(*)                AS so_luong,
    ROUND(COUNT(*) * 100.0
        / (SELECT COUNT(*) FROM lecturers WHERE is_deleted = 0), 1) AS phan_tram
FROM lecturers
WHERE is_deleted = 0
GROUP BY degree
ORDER BY FIELD(degree, 'GS', 'PGS', 'TS', 'ThS') DESC, so_luong DESC;


-- 1.4 Số giảng viên theo chức vụ
SELECT
    position                AS chuc_vu,
    COUNT(*)                AS so_luong
FROM lecturers
WHERE is_deleted = 0
GROUP BY position
ORDER BY so_luong DESC;


-- 1.5 Số giảng viên theo giới tính
SELECT
    CASE gender
        WHEN 'male'   THEN 'Nam'
        WHEN 'female' THEN 'Nữ'
        ELSE gender
    END                     AS gioi_tinh,
    COUNT(*)                AS so_luong
FROM lecturers
WHERE is_deleted = 0
GROUP BY gender;


-- ============================================================
--  2. GIẢNG VIÊN
-- ============================================================

-- 2.1 Danh sách đầy đủ giảng viên (có tên khoa)
SELECT
    l.employee_code         AS ma_gv,
    l.full_name             AS ho_ten,
    l.gender                AS gioi_tinh,
    l.degree                AS hoc_vi,
    l.position              AS chuc_vu,
    d.name                  AS khoa,
    l.email,
    l.phone,
    l.hire_date             AS ngay_vao_lam,
    TIMESTAMPDIFF(YEAR, l.hire_date, CURDATE()) AS nam_cong_tac,
    CASE l.status
        WHEN 'active'   THEN 'Đang dạy'
        WHEN 'inactive' THEN 'Nghỉ việc'
        WHEN 'on_leave' THEN 'Nghỉ phép'
        ELSE l.status
    END                     AS trang_thai
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0
ORDER BY d.name, l.full_name;


-- 2.2 Giảng viên đang nghỉ phép / nghỉ việc
SELECT
    l.employee_code, l.full_name, d.name AS khoa, l.status
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0 AND l.status <> 'active'
ORDER BY l.status, l.full_name;


-- 2.3 Giảng viên thâm niên cao nhất (top 10)
SELECT
    l.employee_code, l.full_name, d.name AS khoa,
    l.hire_date,
    TIMESTAMPDIFF(YEAR, l.hire_date, CURDATE()) AS nam_cong_tac
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0
ORDER BY l.hire_date ASC
LIMIT 10;


-- 2.4 Giảng viên có học vị Tiến sĩ trở lên (TS / PGS / GS)
SELECT
    l.employee_code, l.full_name, l.degree, l.position, d.name AS khoa
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0
  AND l.degree IN ('TS', 'PGS', 'GS')
ORDER BY FIELD(l.degree, 'GS', 'PGS', 'TS'), l.full_name;


-- 2.5 Tìm giảng viên theo tên (thay 'Nguyễn' bằng từ khóa cần tìm)
SELECT
    l.employee_code, l.full_name, l.email, l.phone, d.name AS khoa
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0
  AND l.full_name LIKE '%Nguyễn%'
ORDER BY l.full_name;


-- 2.6 Giảng viên chưa có lịch dạy học kỳ này
SELECT
    l.employee_code, l.full_name, d.name AS khoa
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0
  AND l.status = 'active'
  AND l.id NOT IN (
      SELECT DISTINCT lecturer_id FROM schedules
      WHERE semester = 'HK1' AND academic_year = '2025-2026'
  )
ORDER BY d.name, l.full_name;


-- ============================================================
--  3. LỊCH GIẢNG DẠY
-- ============================================================

-- 3.1 Toàn bộ lịch học kỳ 1 (có tên giảng viên và khoa)
SELECT
    s.day_of_week           AS thu,
    s.start_time            AS gio_bat_dau,
    s.end_time              AS gio_ket_thuc,
    s.subject_code          AS ma_mon,
    s.subject_name          AS ten_mon,
    s.room                  AS phong,
    l.full_name             AS giang_vien,
    d.name                  AS khoa,
    s.semester, s.academic_year
FROM schedules s
JOIN lecturers  l ON l.id = s.lecturer_id
JOIN departments d ON d.id = l.department_id
WHERE s.semester = 'HK1' AND s.academic_year = '2025-2026'
ORDER BY FIELD(s.day_of_week,'Mon','Tue','Wed','Thu','Fri','Sat','Sun'),
         s.start_time;


-- 3.2 Số tiết dạy mỗi giảng viên trong học kỳ
SELECT
    l.employee_code, l.full_name,
    COUNT(s.id)             AS so_mon_day,
    SEC_TO_TIME(
        SUM(TIME_TO_SEC(s.end_time) - TIME_TO_SEC(s.start_time))
    )                       AS tong_so_tiet
FROM lecturers l
LEFT JOIN schedules s ON s.lecturer_id = l.id
    AND s.semester = 'HK1' AND s.academic_year = '2025-2026'
WHERE l.is_deleted = 0
GROUP BY l.id, l.employee_code, l.full_name
ORDER BY so_mon_day DESC;


-- 3.3 Phòng học đang dùng nhiều nhất
SELECT
    room                    AS phong,
    COUNT(*)                AS so_slot
FROM schedules
WHERE semester = 'HK1' AND academic_year = '2025-2026'
GROUP BY room
ORDER BY so_slot DESC;


-- 3.4 Kiểm tra trùng lịch (cùng phòng, cùng giờ, cùng ngày)
SELECT
    s1.day_of_week, s1.room,
    s1.start_time, s1.end_time,
    l1.full_name AS giang_vien_1,
    l2.full_name AS giang_vien_2
FROM schedules s1
JOIN schedules s2 ON s1.id < s2.id
    AND s1.room       = s2.room
    AND s1.day_of_week = s2.day_of_week
    AND s1.semester   = s2.semester
    AND s1.academic_year = s2.academic_year
    AND s1.start_time < s2.end_time
    AND s2.start_time < s1.end_time
JOIN lecturers l1 ON l1.id = s1.lecturer_id
JOIN lecturers l2 ON l2.id = s2.lecturer_id;


-- 3.5 Lịch của một giảng viên cụ thể (thay mã GV)
SELECT
    s.day_of_week, s.start_time, s.end_time,
    s.subject_code, s.subject_name, s.room,
    s.semester, s.academic_year
FROM schedules s
JOIN lecturers l ON l.id = s.lecturer_id
WHERE l.employee_code = 'GV001'
ORDER BY s.academic_year, s.semester,
         FIELD(s.day_of_week,'Mon','Tue','Wed','Thu','Fri','Sat','Sun');


-- ============================================================
--  4. TÀI KHOẢN HỆ THỐNG
-- ============================================================

-- 4.1 Danh sách tài khoản (ẩn password_hash)
SELECT
    id, username, full_name,
    CASE role WHEN 'admin' THEN 'Quản trị viên' ELSE 'Nhân viên' END AS vai_tro,
    IF(is_active, 'Hoạt động', 'Bị khóa')   AS trang_thai,
    created_at                               AS ngay_tao
FROM accounts
ORDER BY role DESC, username;


-- 4.2 Tài khoản bị khóa
SELECT username, full_name, created_at
FROM accounts
WHERE is_active = 0;


-- ============================================================
--  5. NHẬT KÝ HỆ THỐNG
-- ============================================================

-- 5.1 Hoạt động gần nhất (50 dòng)
SELECT
    created_at, username,
    CASE action
        WHEN 'login'  THEN 'Đăng nhập'
        WHEN 'create' THEN 'Tạo mới'
        WHEN 'update' THEN 'Cập nhật'
        WHEN 'delete' THEN 'Xóa'
        ELSE action
    END         AS hanh_dong,
    entity_type AS doi_tuong,
    details
FROM audit_logs
ORDER BY created_at DESC
LIMIT 50;


-- 5.2 Thống kê hành động theo người dùng
SELECT
    username,
    SUM(action = 'login')  AS dang_nhap,
    SUM(action = 'create') AS tao_moi,
    SUM(action = 'update') AS cap_nhat,
    SUM(action = 'delete') AS xoa,
    COUNT(*)               AS tong
FROM audit_logs
GROUP BY username
ORDER BY tong DESC;


-- 5.3 Hoạt động theo ngày (7 ngày gần nhất)
SELECT
    DATE(created_at)    AS ngay,
    COUNT(*)            AS so_thao_tac
FROM audit_logs
WHERE created_at >= CURDATE() - INTERVAL 7 DAY
GROUP BY DATE(created_at)
ORDER BY ngay DESC;


-- ============================================================
--  6. BÁO CÁO TỔNG HỢP
-- ============================================================

-- 6.1 Báo cáo chi tiết từng khoa
SELECT
    d.code                                          AS ma_khoa,
    d.name                                          AS ten_khoa,
    COUNT(l.id)                                     AS tong_giang_vien,
    SUM(l.status = 'active')                        AS dang_day,
    SUM(l.status = 'on_leave')                      AS nghi_phep,
    SUM(l.status = 'inactive')                      AS nghi_viec,
    SUM(l.degree IN ('TS','PGS','GS'))              AS tien_si_tro_len,
    SUM(l.gender = 'female')                        AS giang_vien_nu,
    ROUND(AVG(TIMESTAMPDIFF(YEAR, l.hire_date, CURDATE())), 1) AS tham_nien_tb
FROM departments d
LEFT JOIN lecturers l ON l.department_id = d.id AND l.is_deleted = 0
WHERE d.is_deleted = 0
GROUP BY d.id, d.code, d.name
ORDER BY tong_giang_vien DESC;


-- 6.2 Giảng viên nhiều tiết dạy nhất (top 5)
SELECT
    l.full_name, d.name AS khoa,
    COUNT(s.id)         AS so_mon,
    GROUP_CONCAT(s.subject_name ORDER BY s.subject_name SEPARATOR ', ') AS cac_mon_day
FROM lecturers l
JOIN departments d  ON d.id = l.department_id
JOIN schedules  s   ON s.lecturer_id = l.id
WHERE l.is_deleted = 0
GROUP BY l.id, l.full_name, d.name
ORDER BY so_mon DESC
LIMIT 5;


-- 6.3 Độ tuổi trung bình giảng viên theo khoa
SELECT
    d.name                                                          AS khoa,
    ROUND(AVG(TIMESTAMPDIFF(YEAR, l.date_of_birth, CURDATE())), 1) AS tuoi_trung_binh,
    MIN(TIMESTAMPDIFF(YEAR, l.date_of_birth, CURDATE()))           AS tuoi_tre_nhat,
    MAX(TIMESTAMPDIFF(YEAR, l.date_of_birth, CURDATE()))           AS tuoi_lon_nhat
FROM lecturers l
JOIN departments d ON d.id = l.department_id
WHERE l.is_deleted = 0
GROUP BY d.id, d.name
ORDER BY tuoi_trung_binh;
