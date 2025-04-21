-- Active: 1741465596609@@127.0.0.1@3306@fastapi_db
INSERT INTO users (username, email, password, firstname, lastname, idnumber, address, created_at, is_admin, is_banned) VALUES
('john_doe', 'john.doe@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'John', 'Doe', '12345678', '123 Main St', NOW(), 0, 0),
('jane_smith', 'jane.smith@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Jane', 'Smith', '23456789', '456 Oak Ave', NOW(), 0, 0),
('admin_user', 'admin@company.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Admin', 'User', '34567890', '789 Admin Rd', NOW(), 1, 0),
('mary_jones', 'mary.jones@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Mary', 'Jones', '45678901', '321 Pine Ln', NOW(), 0, 0),
('bob_wilson', 'bob.wilson@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Bob', 'Wilson', '56789012', '654 Elm St', NOW(), 0, 0),
('sarah_lee', 'sarah.lee@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Sarah', 'Lee', '67890123', '987 Maple Dr', NOW(), 0, 0),
('mike_brown', 'mike.brown@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Mike', 'Brown', '78901234', '147 Cedar Rd', NOW(), 0, 0),
('lisa_white', 'lisa.white@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Lisa', 'White', '89012345', '258 Birch Ave', NOW(), 0, 0),
('david_green', 'david.green@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'David', 'Green', '90123456', '369 Spruce St', NOW(), 0, 0),
('emma_black', 'emma.black@email.com', 'f42fe47e2f9794a4aedd5e52f42fe47e2f9794a4aedd5e52', 'Emma', 'Black', '01234567', '741 Willow Ln', NOW(), 0, 0); 