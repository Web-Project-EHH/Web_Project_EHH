USE `forum`;

-- -----------------------------------------------------
-- INSERTING USERS
-- -----------------------------------------------------
INSERT INTO users(username, password, email, is_admin) 
VALUES ('admin', 'dummy_password1', 'admin@carforum.com', true);
INSERT INTO users(username, password, email, is_admin) 
VALUES ('john_doe', 'dummy_password2', 'john_doe@gmail.com', false);
INSERT INTO users(username, password, email, is_admin) 
VALUES ('carlover', 'dummy_password3', 'carlover@gmail.com', false);
INSERT INTO users(username, password, email, is_admin) 
VALUES ('speedy', 'dummy_password4', 'speedy@gmail.com', false);
INSERT INTO users(username, password, email, is_admin) 
VALUES ('mechanic_guru', 'dummy_password5', 'mechanic_guru@gmail.com', false);

-- -----------------------------------------------------
-- INSERTING CATEGORIES
-- -----------------------------------------------------
INSERT INTO categories(name) VALUES ('Uncategorized'); -- 1
INSERT INTO categories(name) VALUES ('General Discussion'); -- 2
INSERT INTO categories(name) VALUES ('Car Reviews'); -- 3
INSERT INTO categories(name) VALUES ('Maintenance and Repairs'); -- 4q
INSERT INTO categories(name) VALUES ('Performance Upgrades'); -- 5
INSERT INTO categories(name, is_private) VALUES ('Club Meetings', 1); -- 6 private

-- -----------------------------------------------------
-- INSERTING TOPICS
-- -----------------------------------------------------
INSERT INTO topics(title, user_id, category_id) 
VALUES ('Best cars of 2024', 2, 3); -- 1
INSERT INTO topics(title, user_id, category_id) 
VALUES ('How to change oil?', 4, 4); -- 2
INSERT INTO topics(title, user_id, category_id) 
VALUES ('Turbocharging a Honda Civic', 3, 5); -- 3
INSERT INTO topics(title, user_id, category_id) 
VALUES ('New tires recommendations', 5, 4); -- 4
INSERT INTO topics(title, user_id, category_id) 
VALUES ('Upcoming club events', 2, 6); -- 5 private

-- -----------------------------------------------------
-- INSERTING PERMISSIONS
-- -----------------------------------------------------
INSERT INTO users_categories_permissions(user_id, category_id) 
VALUES (3, 6); -- read-only
INSERT INTO users_categories_permissions(user_id, category_id, write_access) 
VALUES (4, 6, 1); -- write access

-- -----------------------------------------------------
-- INSERTING REPLIES
-- -----------------------------------------------------
INSERT INTO replies(text, user_id, topic_id) 
VALUES ('I think the Tesla Model S is the best!', 3, 1); -- 1
INSERT INTO replies(text, user_id, topic_id) 
VALUES ('Don\'t forget to use the correct oil type.', 4, 2); -- 2
INSERT INTO replies(text, user_id, topic_id) 
VALUES ('I turbocharged mine last year, big difference!', 5, 3); -- 3
INSERT INTO replies(text, user_id, topic_id) 
VALUES ('Michelin tires are a great choice.', 2, 4); -- 4
INSERT INTO replies(text, user_id, topic_id) 
VALUES ('Can\'t wait for the next meeting!', 3, 5); -- 5

-- -----------------------------------------------------
-- OPTIONAL: INSERTING PRIVATE MESSAGES
-- -----------------------------------------------------
-- INSERT INTO messages(text, sender_id, receiver_id) 
-- VALUES ('Hi, are you coming to the meeting?', 2, 3);

-- -----------------------------------------------------
-- END OF SCRIPT
-- -----------------------------------------------------
