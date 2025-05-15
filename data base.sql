-- إنشاء قاعدة البيانات
CREATE DATABASE IF NOT EXISTS face_recognition_system
CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- استخدام القاعدة
USE face_recognition_system;

-- جدول المستخدمين (users)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,               -- معرف المستخدم
    username VARCHAR(100) NOT NULL,                   -- اسم المستخدم
    email VARCHAR(100) UNIQUE NOT NULL,               -- البريد الإلكتروني
    password VARCHAR(255),                            -- كلمة المرور (تخزين مؤمن)
    face_encoding LONGTEXT NOT NULL,                  -- تمثيل بصمة الوجه (face encoding)
    image_path VARCHAR(255),                          -- مسار الصورة
    video_path VARCHAR(255),                          -- مسار الفيديو (اختياري)
    role ENUM('user', 'admin') DEFAULT 'user',        -- الدور (مستخدم أو مدير)
    status ENUM('active', 'inactive') DEFAULT 'active', -- الحالة (نشط أو غير نشط)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- تاريخ الإنشاء
);

-- جدول سجل المحاولات (login_logs)
CREATE TABLE IF NOT EXISTS login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,               -- معرف المحاولة
    user_id INT,                                     -- معرف المستخدم المرتبط
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- وقت المحاولة
    result ENUM('success', 'fail') NOT NULL,          -- النتيجة (نجاح أو فشل)
    confidence FLOAT,                                -- نسبة الثقة
    image_used VARCHAR(255),                          -- الصورة المستخدمة للمقارنة
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL -- الربط مع جدول المستخدمين
);

-- ملاحظة: لا يتم إضافة بيانات أولية هنا، ويمكن إضافة البيانات عبر التطبيق أو يدويًا عبر واجهة SQL
