# Tài Liệu Phân Tích Dự Án Hiện Tại EduStaff

## 1. Mục đích tài liệu

- Kiến trúc backend và frontend đang được triển khai.
- Các class, module, router và màn hình hiện có.
- Thiết kế database đang dùng trong code.
- Các chức năng đã làm xong, đang làm dở, hoặc mới ở mức placeholder.

---

## 2. Tổng quan cấu trúc dự án

Dự án hiện tại được tách thành 2 phần chính:

- `backend/`: REST API dùng FastAPI.
- `frontend/`: ứng dụng desktop dùng PySide6 và `qfluentwidgets`.

Ngoài ra còn có:

- `database/`: chứa script SQL mẫu.
- `doc/`: tài liệu yêu cầu và tài liệu phân tích.
- `assets/`: ảnh giao diện minh họa.
- `docker-compose.yml`: cấu hình chạy backend + MySQL.

## 2.1. Cấu trúc thư mục chính

```text
EduStaff/
├─ backend/
│  ├─ app/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ models/
│  │  ├─ routers/
│  │  ├─ schemas/
│  │  └─ services/
│  ├─ tests/
│  └─ main.py
├─ frontend/
│  ├─ api/
│  ├─ components/
│  ├─ screens/
│  ├─ styles/
│  ├─ ui/
│  ├─ widgets/
│  └─ main.py
├─ database/
├─ doc/
└─ assets/
```

---

## 3. Kiến trúc backend thực tế

Backend hiện được tổ chức theo mô hình:

- `routers`: định nghĩa endpoint HTTP.
- `schemas`: khai báo dữ liệu vào/ra bằng Pydantic.
- `models`: entity SQLAlchemy.
- `services/store.py`: lớp truy cập dữ liệu và xử lý CRUD chính.
- `core`: bảo mật JWT, dependency phân quyền, cấu hình.
- `db`: tạo `engine`, `SessionLocal`, khởi tạo bảng.

Điểm cần lưu ý:

- Dự án có thư mục `services`, nhưng phần nghiệp vụ hiện tập trung chủ yếu trong một lớp lớn là `DatabaseStore`.
- Tức là dự án chưa tách service theo từng domain nhỏ như `LecturerService`, `ScheduleService`, `AccountService`; thay vào đó đang gom vào `STORE`.

## 3.1. Entry point backend

File chính:

- `backend/app/main.py`

Chức năng:

- Tạo `FastAPI app`.
- Cấu hình CORS.
- Nạp toàn bộ `api_router`.
- Chạy `init_db()` khi startup.
- Gọi `STORE.seed_initial_data()` để sinh dữ liệu mặc định nếu database chưa có tài khoản.

## 3.2. Cấu hình hệ thống

File:

- `backend/app/core/config.py`

Thông tin thực tế:

- `database_url` mặc định là MySQL:
  - `mysql+pymysql://edustaff:edustaff_password@localhost:3306/edustaff`
- Dùng JWT:
  - `jwt_secret_key`
  - `jwt_algorithm`
  - `jwt_expire_minutes`
- `backup_dir` mặc định:
  - `./backups`

Kết luận:

- Code hiện tại đang hướng tới chạy thật với MySQL, không phải mock database.

## 3.3. Kết nối database

File:

- `backend/app/db/session.py`

Triển khai thực tế:

- Sử dụng `create_engine()` của SQLAlchemy.
- Tạo `SessionLocal`.
- `init_db()` gọi `Base.metadata.create_all(bind=engine)`.

Điều này cho thấy:

- Bảng được tạo tự động từ model SQLAlchemy.
- Không thấy migration tool như Alembic trong dự án hiện tại.

---

## 4. Các class model hiện có

Các entity được định nghĩa trong:

- `backend/app/models/entities.py`

## 4.1. `Account`

Tên bảng:

- `accounts`

Thuộc tính:

- `id`
- `username`
- `full_name`
- `role`
- `is_active`
- `password_hash`
- `created_at`

Vai trò:

- Lưu tài khoản đăng nhập.
- Phân quyền theo `role` gồm `admin` và `staff`.

## 4.2. `Department`

Tên bảng:

- `departments`

Thuộc tính:

- `id`
- `code`
- `name`
- `description`
- `is_deleted`

Quan hệ:

- Một khoa có nhiều giảng viên qua `lecturers`.

Ghi chú:

- Có soft delete bằng `is_deleted`.

## 4.3. `Lecturer`

Tên bảng:

- `lecturers`

Thuộc tính:

- `id`
- `employee_code`
- `full_name`
- `email`
- `phone`
- `gender`
- `date_of_birth`
- `degree`
- `position`
- `department_id`
- `hire_date`
- `status`
- `is_deleted`

Quan hệ:

- Thuộc về một `Department`.
- Có nhiều `Schedule`.

Ghi chú:

- Giảng viên cũng đang dùng soft delete.

## 4.4. `Schedule`

Tên bảng:

- `schedules`

Thuộc tính:

- `id`
- `lecturer_id`
- `subject_name`
- `subject_code`
- `room`
- `day_of_week`
- `start_time`
- `end_time`
- `semester`
- `academic_year`

Quan hệ:

- Thuộc về một `Lecturer`.

## 4.5. `AuditLog`

Tên bảng:

- `audit_logs`

Thuộc tính:

- `id`
- `action`
- `entity_type`
- `entity_id`
- `details`
- `username`
- `ip_address`
- `created_at`

Mục đích:

- Ghi nhận thao tác hệ thống như đăng nhập, tạo, sửa, xóa.

---

## 5. Thiết kế database thực tế

Thiết kế database hiện tại được phản ánh bởi hai nguồn:

- SQLAlchemy models trong `backend/app/models/entities.py`
- Script mẫu `database/edustaff_sample.sql`

## 5.1. Các bảng chính

Hệ thống hiện có 5 bảng nghiệp vụ chính:

1. `accounts`
2. `departments`
3. `lecturers`
4. `schedules`
5. `audit_logs`

## 5.2. Quan hệ dữ liệu

```text
departments 1 --- n lecturers
lecturers   1 --- n schedules
accounts    1 --- n audit_logs   (quan hệ logic theo username/user thao tác)
```

Lưu ý:

- `audit_logs` trong code không dùng khóa ngoại trực tiếp tới `accounts`.
- Log hiện lưu `username` và `entity_id` thay vì ràng buộc chặt bằng `account_id`.

## 5.3. Đặc điểm thiết kế hiện tại

- `Department` và `Lecturer` dùng soft delete qua cột `is_deleted`.
- `Schedule` đang xóa cứng khỏi database.
- `Account` đang xóa cứng khỏi database.
- Có unique cho:
  - `accounts.username`
  - `departments.code`
  - `lecturers.employee_code`
  - `lecturers.email`

## 5.4. Dữ liệu mẫu

Có 2 nguồn dữ liệu mẫu:

- `STORE.seed_initial_data()` sinh dữ liệu tối thiểu khi chạy backend lần đầu.
- `database/edustaff_sample.sql` cung cấp dữ liệu mẫu lớn hơn, gồm:
  - nhiều khoa
  - nhiều giảng viên
  - nhiều lịch giảng dạy
  - nhiều log hệ thống

Nhận xét:

- `seed_initial_data()` hiện chỉ sinh tập dữ liệu nhỏ để frontend có thể chạy ngay.
- File SQL mẫu đầy đủ hơn, phù hợp cho demo hoặc khởi tạo thủ công.

---

## 6. Lớp xử lý dữ liệu trung tâm

File:

- `backend/app/services/store.py`

Class chính:

- `DatabaseStore`

Biến dùng toàn cục:

- `STORE = DatabaseStore()`

## 6.1. Vai trò của `DatabaseStore`

Đây là lớp xử lý dữ liệu trung tâm của toàn bộ backend hiện tại. Nó đang gánh cả:

- ánh xạ model sang dict JSON,
- CRUD cho account,
- CRUD cho department,
- CRUD cho lecturer,
- CRUD cho schedule,
- truy vấn thống kê,
- truy vấn audit logs,
- seed dữ liệu ban đầu.

## 6.2. Các nhóm hàm chính

### Tài khoản

- `find_account_by_username`
- `list_accounts`
- `get_account`
- `create_account`
- `update_account`
- `delete_account`
- `toggle_account`
- `reset_password`
- `change_password`

### Khoa

- `list_departments`
- `get_department`
- `create_department`
- `update_department`
- `delete_department`

### Giảng viên

- `list_lecturers`
- `get_lecturer`
- `create_lecturer`
- `update_lecturer`
- `delete_lecturer`

### Lịch giảng dạy

- `list_schedules`
- `get_schedule`
- `create_schedule`
- `update_schedule`
- `delete_schedule`
- `get_slot_detail`

### Nhật ký và thống kê

- `add_audit_log`
- `list_audit_logs`
- `overview_stats`
- `stats_by_department`
- `stats_by_degree`
- `stats_by_position`

## 6.3. Nhận xét thiết kế

Ưu điểm:

- Dễ chạy nhanh và dễ theo dõi cho đồ án hoặc prototype.
- Toàn bộ luồng CRUD tập trung một chỗ.

Hạn chế:

- `DatabaseStore` đang quá lớn.
- Logic dữ liệu và logic nghiệp vụ chưa tách rõ.
- Khi hệ thống mở rộng, file này sẽ khó bảo trì và khó test hơn.

---

## 7. Bảo mật và phân quyền

Các file chính:

- `backend/app/core/security.py`
- `backend/app/core/deps.py`
- `backend/app/routers/auth_router.py`

## 7.1. Cơ chế xác thực

Backend hiện dùng:

- OAuth2 password flow cho endpoint lấy token.
- JWT bearer token cho các request sau đăng nhập.

Luồng thực tế:

1. Frontend gửi username/password tới `/auth/token`.
2. Backend kiểm tra tài khoản bằng `STORE.find_account_by_username()`.
3. So khớp mật khẩu qua `verify_password`.
4. Nếu hợp lệ thì trả `access_token`.
5. Frontend lưu token vào header `Authorization: Bearer ...`.

## 7.2. Phân quyền

Code hiện có 2 mức quyền:

- `get_current_user`: yêu cầu đã đăng nhập.
- `require_admin`: yêu cầu role là `admin`.

Áp dụng thực tế:

- `staff` xem được dữ liệu chung, thống kê, lịch, giảng viên, khoa.
- `admin` mới được tạo/sửa/xóa các dữ liệu quản trị, xem audit log, backup, quản lý tài khoản.

---

## 8. API backend đang có

Các router được gom trong `backend/app/routers/`.

## 8.1. Authentication

File:

- `auth_router.py`

Endpoint hiện có:

- `POST /auth/token`
- `GET /auth/me`
- `POST /auth/change-password`

## 8.2. Departments

File:

- `department_router.py`

Endpoint hiện có:

- `GET /departments`
- `GET /departments/{department_id}`
- `POST /departments`
- `PUT /departments/{department_id}`
- `DELETE /departments/{department_id}`

Ghi chú thực tế:

- Router này có một đoạn tương thích đặc biệt vì frontend hiện có lúc truyền sai tham số `search` vào `page`.

## 8.3. Lecturers

File:

- `lecturer_router.py`

Endpoint hiện có:

- `GET /lecturers`
- `GET /lecturers/{lecturer_id}`
- `POST /lecturers`
- `PUT /lecturers/{lecturer_id}`
- `DELETE /lecturers/{lecturer_id}`
- `POST /lecturers/{lecturer_id}/avatar`
- `GET /lecturers/export`
- `GET /lecturers/export/pdf`

Ghi chú:

- Export Excel đã làm thật bằng `openpyxl`.
- Export PDF đã làm thật bằng `reportlab`.
- Upload avatar mới là placeholder, chưa thấy lưu file thật.

## 8.4. Schedules

File:

- `schedule_router.py`

Endpoint hiện có:

- `GET /schedules`
- `GET /schedules/{schedule_id}`
- `POST /schedules`
- `PUT /schedules/{schedule_id}`
- `DELETE /schedules/{schedule_id}`
- `GET /schedules/week/detail`

Ghi chú:

- Có API hỗ trợ xem chi tiết slot theo khung giờ để phục vụ giao diện lịch tuần.
- Chưa thấy kiểm tra trùng lịch trong `create_schedule` và `update_schedule`.

## 8.5. Accounts

File:

- `account_router.py`

Endpoint hiện có:

- `GET /accounts`
- `GET /accounts/{account_id}`
- `POST /accounts`
- `PUT /accounts/{account_id}`
- `PATCH /accounts/{account_id}/toggle-active`
- `POST /accounts/{account_id}/reset-password`
- `DELETE /accounts/{account_id}`

## 8.6. Audit logs

File:

- `audit_router.py`

Endpoint hiện có:

- `GET /audit-logs`

Quyền:

- Chỉ `admin`.

## 8.7. Stats

File:

- `stats_router.py`

Endpoint hiện có:

- `GET /stats/overview`
- `GET /stats/by-department`
- `GET /stats/by-degree`
- `GET /stats/by-position`

## 8.8. Backup

File:

- `backup_router.py`

Endpoint hiện có:

- `GET /backup/create`
- `GET /backup/list`
- `POST /backup/restore`
- `DELETE /backup/{filename}`

Nhận xét thực tế:

- `create` hiện chỉ trả về file JSON snapshot đơn giản, chưa phải backup database thật.
- `restore` hiện trả về thông báo thành công kiểu placeholder, chưa thấy logic phục hồi dữ liệu thật.
- `list` và `delete` thao tác trên thư mục backup thật.

---

## 9. Kiến trúc frontend thực tế

Frontend được tổ chức theo các nhóm:

- `screens/`: mỗi màn hình chính của hệ thống.
- `api/`: HTTP client gọi backend.
- `components/`: component tái sử dụng như dialog, toast, loading, pagination.
- `widgets/`: widget đặc thù, ví dụ lịch tuần.
- `ui/` và `styles/`: theme, icon, stylesheet.

## 9.1. Điểm vào ứng dụng

File:

- `frontend/main.py`

Luồng:

1. Tạo `QApplication`.
2. Nạp stylesheet toàn cục.
3. Mở `LoginScreen`.
4. Khi đăng nhập thành công, mở `MainWindow`.

## 9.2. Màn hình đăng nhập

File:

- `frontend/screens/login_screen.py`

Đặc điểm:

- Giao diện dark theme theo Fluent Design.
- Dùng `LoginWorker` chạy đăng nhập ở thread riêng.
- Sau khi login, gọi thêm `auth_api.get_me()` để lấy user info.

## 9.3. Cửa sổ chính

File:

- `frontend/screens/main_window.py`

Thành phần thực tế:

- `DashboardScreen`
- `LecturerScreen`
- `DepartmentScreen`
- `ScheduleScreen`
- `AccountScreen`
- `AuditLogScreen`
- `BackupScreen`

Phân quyền giao diện:

- Nếu user là `staff`, sidebar không hiện các màn hình quản trị.
- Nếu user là `admin`, có thêm tài khoản, nhật ký hệ thống, sao lưu.

---

## 10. Các màn hình frontend hiện có

## 10.1. `DashboardScreen`

Chức năng:

- Hiển thị tổng số giảng viên, khoa, lịch, tài khoản.
- Bảng thống kê giảng viên theo khoa.
- Biểu đồ thanh theo học vị và chức vụ.
- Với `admin`, hiển thị thêm hoạt động gần đây từ audit log.

Nguồn dữ liệu:

- `stats_api`
- `audit_api`

## 10.2. `LecturerScreen`

Chức năng thực tế:

- Danh sách giảng viên có phân trang.
- Tìm kiếm và lọc.
- Thêm, sửa, xóa.
- Xem chi tiết.
- Export dữ liệu.

Điểm đáng chú ý:

- Có `LecturerDetailDialog` và `LecturerFormDialog`.
- Các thao tác backend đều được bọc trong worker `QThread`.

## 10.3. `DepartmentScreen`

Chức năng thực tế:

- Danh sách khoa.
- Tìm kiếm theo tên hoặc mã khoa.
- Thêm, sửa, xóa khoa.

Đặc điểm:

- Có timer debounce cho ô tìm kiếm.

## 10.4. `ScheduleScreen`

Chức năng thực tế:

- Hiển thị lịch giảng dạy ở 2 chế độ:
  - bảng
  - lịch tuần
- Lọc theo giảng viên, học kỳ, năm học, thứ.
- Thêm, sửa, xóa lịch.
- Nhấn vào slot trong lịch tuần để xem chi tiết ca học.

Đây là màn hình có mức tích hợp UI cao nhất trong dự án hiện tại.

## 10.5. `AccountScreen`

Chức năng thực tế:

- Danh sách tài khoản.
- Tìm kiếm, lọc role, lọc trạng thái.
- Tạo tài khoản mới.
- Cập nhật tài khoản.
- Khóa/mở tài khoản.

## 10.6. `AuditLogScreen`

Chức năng theo cấu trúc dự án:

- Hiển thị log hệ thống cho admin.
- Lọc theo action, entity, username, khoảng ngày.

## 10.7. `BackupScreen`

Chức năng thực tế:

- Tạo file backup từ endpoint `/backup/create`.
- Tải danh sách backup từ `/backup/list`.
- Gửi restore theo tên file.
- Xóa file backup.

Nhận xét:

- Giao diện backup đã khá đầy đủ.
- Nhưng backend backup/restore hiện mới ở mức bán mô phỏng.

---

## 11. Lớp API frontend

Thư mục:

- `frontend/api/`

File trung tâm:

- `frontend/api/client.py`

Chức năng:

- Quản lý `requests.Session`.
- Lưu và gỡ token.
- Chuẩn hóa lỗi HTTP thành `APIError`.
- Hỗ trợ `get`, `post`, `put`, `patch`, `delete`, `get_file`, `post_file`.

Nhận xét:

- Frontend không truy cập database trực tiếp.
- Toàn bộ dữ liệu đều đi qua HTTP API.

Đây là điểm thiết kế đúng và nhất quán trong dự án hiện tại.

---

## 12. Chức năng đã triển khai theo trạng thái thực tế

## 12.1. Đã làm tương đối đầy đủ

- Đăng nhập JWT.
- Lấy thông tin user hiện tại.
- Phân quyền `admin` và `staff`.
- CRUD khoa.
- CRUD giảng viên.
- CRUD lịch giảng dạy.
- CRUD tài khoản.
- Audit log cơ bản.
- Dashboard thống kê.
- Export Excel giảng viên.
- Export PDF giảng viên.
- Frontend tích hợp cho hầu hết module chính.

## 12.2. Đã có nhưng còn hạn chế

- Backup/restore:
  - UI khá đầy đủ.
  - Backend mới chỉ tạo snapshot JSON đơn giản và restore placeholder.

- Upload avatar giảng viên:
  - Endpoint tồn tại.
  - Chưa thấy lưu file thật.

- Kiểm tra trùng lịch:
  - README và yêu cầu có nhắc.
  - Trong code hiện tại chưa thấy validate xung đột thời gian khi tạo/sửa lịch.

## 12.3. Có dấu hiệu chênh giữa README và code

- README mô tả hệ thống khá đầy đủ theo hướng production.
- Nhưng code thực tế hiện đang ở mức đồ án chạy tốt hoặc prototype hoàn chỉnh một phần.
- Một số tính năng trong README mạnh hơn trạng thái code hiện tại, đặc biệt:
  - backup/restore thật
  - upload avatar thật
  - kiểm tra trùng lịch chặt chẽ
  - tách service rõ hơn

---

## 13. Kiểm thử hiện có

Thư mục:

- `backend/tests/`

Các file test:

- `test_auth.py`
- `test_departments.py`
- `test_lecturers.py`

Nhận xét:

- Dự án đã có bước đầu kiểm thử backend.
- Chưa thấy test cho:
  - schedules
  - accounts
  - stats
  - audit logs
  - backup

---

## 14. Đánh giá thiết kế hiện tại

## 14.1. Điểm mạnh

- Tách frontend và backend rõ ràng.
- Luồng đăng nhập và phân quyền hợp lý.
- Frontend dùng worker để tránh khóa giao diện.
- Mô hình dữ liệu đủ cho bài toán quản lý giảng viên.
- Schedule screen và dashboard được làm khá tốt về trải nghiệm.
- Có seed data và script SQL mẫu hỗ trợ demo.

## 14.2. Điểm cần cải thiện

- `DatabaseStore` đang ôm quá nhiều trách nhiệm.
- Backup/restore chưa đúng nghĩa backup database thật.
- Chưa thấy validate trùng lịch giảng dạy.
- Chưa có migration database.
- Một số API còn mang tính tương thích tạm thời với frontend.
- Tài liệu README mô tả rộng hơn trạng thái triển khai thực tế.

---

## 15. Kết luận

Từ mã nguồn hiện tại, EduStaff là một hệ thống quản lý giảng viên đại học theo mô hình:

- Backend FastAPI + SQLAlchemy + MySQL
- Frontend desktop PySide6 + qfluentwidgets

Hệ thống hiện đã có nền tảng vận hành tương đối rõ:

- đăng nhập,
- phân quyền,
- quản lý khoa,
- quản lý giảng viên,
- quản lý lịch giảng dạy,
- quản lý tài khoản,
- thống kê,
- nhật ký hệ thống.

Tuy nhiên, một số phần vẫn đang ở mức chưa hoàn thiện hoàn toàn trong code thực tế, đặc biệt là:

- backup/restore thật,
- upload avatar thật,
- kiểm tra trùng lịch,
- tách lớp service để dễ bảo trì.

Nếu cần bước tiếp theo, có thể viết tiếp một tài liệu ngắn hơn theo dạng:

- sơ đồ class của dự án hiện tại,
- sơ đồ database ERD,
- bảng đối chiếu "README mô tả gì" và "code hiện có gì".
