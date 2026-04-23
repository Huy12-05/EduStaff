# Mô Tả Chức Năng Thực Tế Dự Án EduStaff

## 1. Mục đích tài liệu

Tài liệu này mô tả các chức năng thực tế đang có trong mã nguồn dự án `EduStaff`, dựa trên việc đối chiếu trực tiếp:

- `backend/`
- `frontend/`
- `database/edustaff_sample.sql`

Mục tiêu là ghi lại đúng những gì hệ thống hiện đang hỗ trợ ở mức backend API, giao diện desktop và dữ liệu mẫu, thay vì mô tả theo định hướng mong muốn hoặc theo README.

---

## 2. Tổng quan dự án

EduStaff là hệ thống quản lý giảng viên đại học theo mô hình tách hai phần:

- `backend/`: REST API dùng FastAPI + SQLAlchemy
- `frontend/`: ứng dụng desktop dùng PySide6 + qfluentwidgets

Các nhóm chức năng chính đang có trong mã nguồn:

- Đăng nhập và xác thực người dùng
- Phân quyền `admin` và `staff`
- Quản lý khoa/bộ môn
- Quản lý giảng viên
- Quản lý lịch giảng dạy
- Quản lý tài khoản người dùng
- Theo dõi nhật ký hệ thống
- Thống kê tổng quan trên dashboard
- Xuất dữ liệu giảng viên ra Excel/PDF
- Tạo và quản lý file backup dạng snapshot JSON

---

## 3. Cấu trúc dự án

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
├─ assets/
└─ docker-compose.yml
```

Ý nghĩa chính:

- `backend/app/routers/`: định nghĩa endpoint API
- `backend/app/services/store.py`: lớp xử lý dữ liệu trung tâm
- `backend/app/models/entities.py`: model SQLAlchemy
- `frontend/screens/`: các màn hình nghiệp vụ
- `frontend/api/`: lớp gọi HTTP API
- `database/edustaff_sample.sql`: schema và dữ liệu mẫu tương đối đầy đủ

---

## 4. Kiến trúc hoạt động thực tế

### 4.1. Backend

Backend khởi tạo trong `backend/app/main.py`.

Luồng khởi động thực tế:

1. Tạo `FastAPI app`
2. Cấu hình CORS
3. Nạp toàn bộ router
4. Khi startup:
   - gọi `init_db()`
   - gọi `STORE.seed_initial_data()`

Điều này cho thấy hệ thống có thể tự tạo bảng và seed dữ liệu cơ bản nếu database đang trống.

### 4.2. Frontend

Frontend khởi động từ `frontend/main.py`.

Luồng chạy thực tế:

1. Tạo `QApplication`
2. Nạp theme toàn cục
3. Mở `LoginScreen`
4. Sau khi đăng nhập thành công thì mở `MainWindow`
5. `MainWindow` tải các màn hình theo role của người dùng

### 4.3. Mô hình truy cập dữ liệu

Hệ thống hiện chưa tách service theo domain rõ ràng. Phần lớn thao tác dữ liệu được dồn vào:

- `backend/app/services/store.py`

Lớp `DatabaseStore` hiện đảm nhiệm:

- map dữ liệu ORM sang JSON
- CRUD cho nhiều bảng
- thống kê
- audit log
- seed dữ liệu

Đây là kiến trúc phù hợp cho đồ án hoặc prototype, nhưng chưa phải tổ chức theo service tách nhỏ.

---

## 5. Database thực tế đang dùng

Theo `database/edustaff_sample.sql`, hệ thống có 5 bảng chính:

1. `accounts`
2. `departments`
3. `lecturers`
4. `schedules`
5. `audit_logs`

### 5.1. Quan hệ dữ liệu

- `departments.id` 1 - n `lecturers.department_id`
- `lecturers.id` 1 - n `schedules.lecturer_id`
- `audit_logs.username` là liên kết logic tới người thao tác, không phải foreign key tới `accounts`

### 5.2. Đặc điểm đáng chú ý

- `departments` và `lecturers` dùng soft delete qua `is_deleted`
- `accounts` dùng trạng thái khóa/mở qua `is_active`
- `schedules` đang xóa cứng
- `accounts.username`, `departments.code`, `lecturers.employee_code`, `lecturers.email` có unique

### 5.3. Dữ liệu mẫu

Hệ thống có hai mức dữ liệu mẫu:

- `STORE.seed_initial_data()`: dữ liệu tối thiểu để chạy nhanh
- `database/edustaff_sample.sql`: bộ dữ liệu mẫu lớn hơn, đủ cho demo nghiệp vụ

---

## 6. Chức năng xác thực và phân quyền

### 6.1. Đăng nhập

API:

- `POST /auth/token`

Thực tế đang làm:

- nhận `username/password`
- kiểm tra tài khoản qua `STORE.find_account_by_username()`
- so khớp mật khẩu bằng hàm hash/verify
- từ chối nếu tài khoản bị khóa
- tạo JWT token nếu hợp lệ
- ghi audit log cho thao tác đăng nhập

### 6.2. Lấy thông tin người dùng hiện tại

API:

- `GET /auth/me`

Trả về:

- `id`
- `username`
- `full_name`
- `role`
- `is_active`

### 6.3. Đổi mật khẩu

API:

- `POST /auth/change-password`

Điều kiện:

- phải đăng nhập
- phải nhập đúng mật khẩu cũ

### 6.4. Phân quyền

Hai role hiện có:

- `admin`
- `staff`

Phân quyền thực tế:

- `staff`: xem dữ liệu chung, thống kê, giảng viên, khoa, lịch dạy
- `admin`: thêm/sửa/xóa dữ liệu quản trị, xem audit log, thao tác backup, quản lý tài khoản

Trên giao diện:

- sidebar của `staff` không hiển thị các màn hình quản trị
- sidebar của `admin` có thêm tài khoản, nhật ký hệ thống, sao lưu

---

## 7. Chức năng backend thực tế theo module

## 7.1. Quản lý khoa/bộ môn

Router:

- `backend/app/routers/department_router.py`

API hiện có:

- `GET /departments`
- `GET /departments/{department_id}`
- `POST /departments`
- `PUT /departments/{department_id}`
- `DELETE /departments/{department_id}`

Chức năng thực tế:

- liệt kê khoa còn hoạt động
- tìm kiếm theo mã khoa hoặc tên khoa
- tạo khoa mới
- cập nhật thông tin khoa
- xóa mềm khoa bằng `is_deleted`

Ràng buộc nghiệp vụ đang có:

- không cho xóa khoa nếu vẫn còn giảng viên chưa bị soft delete trong khoa đó

Lưu ý:

- router có đoạn tương thích cho trường hợp frontend cũ truyền sai tham số `search` vào `page`

## 7.2. Quản lý giảng viên

Router:

- `backend/app/routers/lecturer_router.py`

API hiện có:

- `GET /lecturers`
- `GET /lecturers/{lecturer_id}`
- `POST /lecturers`
- `PUT /lecturers/{lecturer_id}`
- `DELETE /lecturers/{lecturer_id}`
- `POST /lecturers/{lecturer_id}/avatar`
- `GET /lecturers/export`
- `GET /lecturers/export/pdf`

Chức năng thực tế:

- danh sách giảng viên có phân trang
- lọc theo:
  - từ khóa
  - khoa
  - học vị
  - chức vụ
  - giới tính
  - trạng thái
- xem chi tiết giảng viên
- thêm giảng viên mới
- cập nhật giảng viên
- xóa mềm giảng viên

Ràng buộc đang có:

- bắt trùng `employee_code`
- bắt trùng `email`

Chức năng export:

- export Excel đã làm thật bằng `openpyxl`
- export PDF đã làm thật bằng `reportlab`

Trạng thái upload avatar:

- endpoint có tồn tại
- hiện mới là placeholder giữ hợp đồng API
- chưa thấy logic lưu file thật

## 7.3. Quản lý lịch giảng dạy

Router:

- `backend/app/routers/schedule_router.py`

API hiện có:

- `GET /schedules`
- `GET /schedules/{schedule_id}`
- `POST /schedules`
- `PUT /schedules/{schedule_id}`
- `DELETE /schedules/{schedule_id}`
- `GET /schedules/week/detail`

Chức năng thực tế ở backend:

- liệt kê lịch có phân trang
- lọc theo:
  - giảng viên
  - thứ
  - học kỳ
  - năm học
- lấy chi tiết một lịch
- tạo lịch
- cập nhật lịch
- xóa lịch
- lấy toàn bộ lịch theo một khung giờ cụ thể để phục vụ giao diện lịch tuần

Lưu ý quan trọng:

- backend hiện chưa tự chặn xung đột lịch/phòng học khi lưu
- việc kiểm tra trùng lịch hiện được làm chủ yếu ở frontend trước khi gửi lệnh lưu

## 7.4. Quản lý tài khoản

Router:

- `backend/app/routers/account_router.py`

API hiện có:

- `GET /accounts`
- `GET /accounts/{account_id}`
- `POST /accounts`
- `PUT /accounts/{account_id}`
- `PATCH /accounts/{account_id}/toggle-active`
- `POST /accounts/{account_id}/reset-password`
- `DELETE /accounts/{account_id}`

Chức năng thực tế:

- danh sách tài khoản
- tìm kiếm theo username hoặc họ tên
- lọc theo role
- lọc theo trạng thái khóa/mở
- tạo tài khoản mới
- cập nhật họ tên, role, mật khẩu
- khóa/mở tài khoản
- đặt lại mật khẩu
- xóa tài khoản

Ràng buộc đang có:

- không cho xóa chính tài khoản đang đăng nhập

## 7.5. Nhật ký hệ thống

Router:

- `backend/app/routers/audit_router.py`

API hiện có:

- `GET /audit-logs`

Chức năng thực tế:

- liệt kê log theo phân trang
- lọc theo:
  - action
  - entity_type
  - username
  - date_from
  - date_to

Nguồn log:

- đăng nhập
- tạo/cập nhật/xóa nhiều đối tượng chính

Quyền truy cập:

- chỉ `admin`

## 7.6. Thống kê

Router:

- `backend/app/routers/stats_router.py`

API hiện có:

- `GET /stats/overview`
- `GET /stats/by-department`
- `GET /stats/by-degree`
- `GET /stats/by-position`
- `GET /stats/lecturer-status`

Chức năng thực tế:

- tổng số giảng viên
- tổng số khoa
- tổng số lịch
- tổng số tài khoản
- thống kê giảng viên theo khoa
- thống kê theo học vị
- thống kê theo chức vụ
- thống kê trạng thái giảng viên

## 7.7. Sao lưu và phục hồi

Router:

- `backend/app/routers/backup_router.py`

API hiện có:

- `GET /backup/create`
- `GET /backup/list`
- `POST /backup/upload`
- `POST /backup/restore`
- `DELETE /backup/{filename}`

Chức năng thực tế:

- tạo snapshot dữ liệu dưới dạng file JSON
- tự lưu file snapshot vào thư mục backup của server
- tải file backup về client
- liệt kê các file backup hiện có
- tải file backup từ máy local lên server
- xóa file backup trên server

Giới hạn hiện tại:

- restore mới ở mức nhận lệnh và trả thông báo
- chưa có logic phục hồi dữ liệu thật vào database
- backup hiện là snapshot JSON, không phải dump MySQL đầy đủ

---

## 8. Chức năng frontend thực tế theo màn hình

## 8.1. LoginScreen

File:

- `frontend/screens/login_screen.py`

Chức năng:

- nhập username/password
- gọi API đăng nhập bằng worker thread
- lấy thông tin người dùng sau đăng nhập
- thông báo lỗi nếu API lỗi hoặc mất kết nối
- giao diện dark theme, cửa sổ kéo thả được

## 8.2. MainWindow

File:

- `frontend/screens/main_window.py`

Chức năng:

- khởi tạo toàn bộ các màn hình chính
- tạo sidebar navigation
- ẩn/hiện module theo role
- hỗ trợ đăng xuất và quay lại màn hình login

Các màn hình được nạp:

- `DashboardScreen`
- `LecturerScreen`
- `DepartmentScreen`
- `ScheduleScreen`
- `AccountScreen`
- `AuditLogScreen`
- `BackupScreen`

## 8.3. DashboardScreen

File:

- `frontend/screens/dashboard_screen.py`

Chức năng thực tế:

- hiển thị số liệu tổng quan:
  - tổng giảng viên
  - tổng khoa
  - tổng lịch
  - tổng tài khoản
- bảng số giảng viên theo khoa
- biểu đồ theo trình độ và chức vụ
- donut chart trạng thái giảng viên
- hiển thị lịch hôm nay
- với `admin`: hiển thị hoạt động gần đây từ audit log
- với `admin`: có thao tác nhanh để chuyển sang thêm giảng viên/lịch
- xuất báo cáo dashboard ra:
  - `.xlsx`
  - `.csv`

## 8.4. LecturerScreen

Màn hình này là module quản lý giảng viên ở phía UI.

Chức năng thực tế theo backend và cấu trúc frontend:

- hiển thị danh sách giảng viên
- phân trang
- tìm kiếm và lọc
- xem chi tiết
- thêm giảng viên
- sửa giảng viên
- xóa giảng viên
- export danh sách

Các thao tác gọi backend thông qua worker thread để tránh khóa giao diện.

## 8.5. DepartmentScreen

Chức năng thực tế:

- hiển thị danh sách khoa
- tìm kiếm theo tên hoặc mã
- thêm khoa
- cập nhật khoa
- xóa khoa

## 8.6. ScheduleScreen

File:

- `frontend/screens/schedule_screen.py`

Chức năng thực tế:

- hiển thị lịch ở 2 chế độ:
  - bảng
  - lịch tuần
- lọc theo:
  - giảng viên
  - học kỳ
  - năm học
  - thứ
- thêm lịch
- sửa lịch
- xóa lịch
- xem chi tiết một slot giờ trong lịch tuần

Điểm đáng chú ý:

- frontend có `ConflictCheckWorker`
- khi thêm/sửa lịch, giao diện sẽ tải các lịch cùng thứ/học kỳ/năm học để kiểm tra trùng phòng theo khung giờ
- nếu có xung đột, người dùng vẫn có thể chọn tiếp tục lưu
- nghĩa là đây là cảnh báo phía client, chưa phải ràng buộc cứng ở backend

## 8.7. AccountScreen

File:

- `frontend/screens/account_screen.py`

Chức năng thực tế:

- hiển thị danh sách tài khoản
- tìm kiếm
- lọc role
- lọc trạng thái hoạt động
- tạo tài khoản
- cập nhật tài khoản
- khóa/mở khóa tài khoản
- xóa tài khoản

Quyền sử dụng:

- chỉ dành cho `admin`

## 8.8. AuditLogScreen

File:

- `frontend/screens/audit_log_screen.py`

Chức năng thực tế:

- xem nhật ký hệ thống dạng bảng
- lọc theo hành động
- lọc theo đối tượng
- lọc theo khoảng ngày
- phân trang

Quyền sử dụng:

- chỉ dành cho `admin`

## 8.9. BackupScreen

File:

- `frontend/screens/backup_screen.py`

Chức năng thực tế:

- tạo backup mới qua API
- chọn nơi lưu file backup ở máy local
- tải file backup từ máy local lên server
- hiển thị danh sách file backup trên server
- gửi lệnh restore
- xóa file backup

Giới hạn:

- UI đã khá đầy đủ
- nhưng hiệu quả restore thật vẫn phụ thuộc backend, hiện mới dừng ở mức placeholder

---




