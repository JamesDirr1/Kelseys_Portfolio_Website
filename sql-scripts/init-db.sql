-- Create category table
CREATE TABLE IF NOT EXISTS category (
    category_id TINYINT AUTO_INCREMENT PRIMARY KEY,
    category_title VARCHAR(100),
    category_order TINYINT UNIQUE
);

-- Create project table
CREATE TABLE IF NOT EXISTS project (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    project_title VARCHAR(255) NOT NULL,
    project_date DATE NOT NULL,
    project_desc VARCHAR(255),
    category_id TINYINT,
    project_image_id INT,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE CASCADE
);

-- Create image table
CREATE TABLE IF NOT EXISTS image (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    image_title VARCHAR(255),
    image_desc VARCHAR(255),
    image_URL VARCHAR(2083) NOT NULL,
    image_weight TINYINT,
    project_id INT,
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE
);

-- Create user table
CREATE TABLE IF NOT EXISTS users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
	user_name VARCHAR(50) NOT NULL UNIQUE,
	user_password VARCHAR(255) NOT NULL,
	user_creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create_meta_table
CREATE TABLE IF NOT EXISTS site_meta (
	meta_id INT PRIMARY KEY AUTO_INCREMENT,
	meta_key VARCHAR(255) UNIQUE NOT NULL,
	meta_data JSON NOT NULL,
	last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE or Replace view `VV.category` AS
    SELECT category_id, category_title, category_order
    FROM category;

CREATE or Replace view `VV.project` AS
    SELECT project_id, project_title, project_date, project_desc, project.category_id, project_image_id
    FROM project;

CREATE or Replace view `VV.image` AS
    SELECT image_id, image_title, image_desc, image_URL, image_weight, image.project_id
    FROM image;

CREATE or Replace view `VV.users` AS
	SELECT user_id, user_name, user_password, user_creation_time
	FROM users;

CREATE OR REPLACE VIEW `VV.site_meta` AS
	SELECT meta_id, meta_key, meta_data, last_updated
	FROM site_meta;

DELETE from category;
DELETE from project;
DELETE from image;
DELETE from users;
ALTER TABLE image AUTO_INCREMENT = 1;
ALTER TABLE project AUTO_INCREMENT = 1;
ALTER TABLE category AUTO_INCREMENT = 1;
ALTER TABLE users AUTO_INCREMENT = 1;

DELIMITER $$

CREATE PROCEDURE test_data()
BEGIN
	INSERT INTO category (category_title, category_order) VALUES
	('Illustration', 1),
	('Design', 2),
	('Comics', 3);

	INSERT INTO project (project_title, project_date, project_desc, category_id, project_image_id) VALUES
	('A to Z', '2025-01-05', 'Illustrations of objects from A to Z.', 1, NULL),
	('Witch\'s Tea Party', '2024-12-07', 'Commission for Twitch streamer profile picture.', 1, NULL),
	('Mushroom Forest', '2024-03-10', 'Landscapes drawing of a mystical mushroom forest.', 1, NULL),
	('1928 Reese\'s Ad', '2025-01-17', 'Reese\'s Cup ad designed to be from 1928.', 2, NULL),
	('Cryptid Cookies', '2024-09-20', 'Cookie box design for a cookie shop named \'Cryptid Cookies\'.', 2, NULL),
	('Great Lakes bottle redesign', '2024-09-20', 'Redesign of a bottle for Great Lakes Brewing Company.', 2, NULL),
	('The Hat Guy', '2025-01-20', 'Story of a guy on his quest to find the perfect hat for to impress his date.', 3, NULL),
	('The Half-Goose of Ohio', '2024-09-17', 'Story of adventure vlogs on the hunt for the mysterious creature in the woods.', 3, NULL),
	('The Medium Ghost', '2024-01-17', 'A silent comic about a medium ghost and its visions', 3, NULL);

	INSERT INTO image (image_title, image_desc, image_URL, image_weight, project_id) VALUES
	('Dreamy Apothecary', null, 'https://static.wixstatic.com/media/0fee66_66b717693fc445f6a81ed9cb6be1df90~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_66b717693fc445f6a81ed9cb6be1df90~mv2.webp', 1, 1),
	('Twitch Commission', 'Witch sitting on a mushroom drinking tea with her cat', 'https://static.wixstatic.com/media/0fee66_0e33a20771a34816b0cc496f13fd139f~mv2.jpeg/v1/fit/w_1544,h_1420,q_90/0fee66_0e33a20771a34816b0cc496f13fd139f~mv2.webp', 2, 2),
	('Mushroom Forest', 'A Mushroom village in dark forest', 'https://static.wixstatic.com/media/0fee66_712108752e9c4813a75d378c02e59e74~mv2.jpg/v1/fit/w_2250,h_1278,q_90/0fee66_712108752e9c4813a75d378c02e59e74~mv2.webp', 1, 3),
	('Reese\'s ad', null, 'https://static.wixstatic.com/media/0fee66_f30654123c914ab9909e1e93fc0dbbac~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_f30654123c914ab9909e1e93fc0dbbac~mv2.webp', 1, 4),
	('Cryptid Cookies Full Box 1', 'Full box render for Cryptid Cookies', 'https://static.wixstatic.com/media/0fee66_86d3cc90528c453abd289b93367ef42c~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_86d3cc90528c453abd289b93367ef42c~mv2.webp', 1, 5),
	('Cryptid Cookies Full Box 2', 'Full box render for Cryptid Cookies', 'https://static.wixstatic.com/media/0fee66_60e0a4fdd92b4b9bb9431bcc9d7a454d~mv2.jpg/v1/fit/w_1126,h_1035,q_90/0fee66_60e0a4fdd92b4b9bb9431bcc9d7a454d~mv2.webp', 3, 5),
	('Cryptid Cookies flat View 1', 'unfolded view for Cryptid Cookies', 'https://static.wixstatic.com/media/0fee66_3424482a5d814fde9a77678b43d1308f~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_3424482a5d814fde9a77678b43d1308f~mv2.webp', 2, 5),
	('Cryptid Cookies flat View 2', 'unfolded view for Cryptid Cookies', 'https://static.wixstatic.com/media/0fee66_ad1d13042a564730b0e2e1f12f8dd66e~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_ad1d13042a564730b0e2e1f12f8dd66e~mv2.webp', 4, 5),
	('Great Lakes Bottle Render', 'Full bottle render for Great Lakes', 'https://static.wixstatic.com/media/0fee66_e2a1b0b1e47b483eb5b3cf1ec4a6f523~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_e2a1b0b1e47b483eb5b3cf1ec4a6f523~mv2.webp', 1, 6),
	('Great Lakes Bottle template', 'template for Great Lakes', 'https://static.wixstatic.com/media/0fee66_642b37d6e48844d9a1f8fcbd30c9dbad~mv2.jpg/v1/fit/w_1544,h_1420,q_90/0fee66_642b37d6e48844d9a1f8fcbd30c9dbad~mv2.webp', 1, 6),
	('The Hat Guy page 1', 'title page', 'https://static.wixstatic.com/media/0fee66_a60203f7cb46437a919948da2563e0e3~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_a60203f7cb46437a919948da2563e0e3~mv2.jpg', 1, 7),
	('The Hat Guy page 2', null, 'https://static.wixstatic.com/media/0fee66_0f41243433e1449597d4e4babc2e7a3b~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_0f41243433e1449597d4e4babc2e7a3b~mv2.jpg', 2, 7),
	('The Hat Guy page 3', null, 'https://static.wixstatic.com/media/0fee66_bf5ba101cda24193bd5ffb0e84f25c5f~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_bf5ba101cda24193bd5ffb0e84f25c5f~mv2.jpg', 3, 7),
	('The Hat Guy page 4', null, 'https://static.wixstatic.com/media/0fee66_8df18995daf941f6b4cfbdb246ecef46~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_8df18995daf941f6b4cfbdb246ecef46~mv2.jpg', 4, 7),
	('The Hat Guy page 5', null, 'https://static.wixstatic.com/media/0fee66_6dd04a46583d4aa985c9841c2d6da187~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_6dd04a46583d4aa985c9841c2d6da187~mv2.jpg', 5, 7),
	('Half-Goose page 1', 'title page', 'https://static.wixstatic.com/media/0fee66_dfda82ec2c6a47c9b654f6ddb9b5bc39~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_dfda82ec2c6a47c9b654f6ddb9b5bc39~mv2.jpg', 1, 8),
	('Half-Goose page 2', null, 'https://static.wixstatic.com/media/0fee66_8af1776a914f46ccafe7f95d27ddaf7c~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_8af1776a914f46ccafe7f95d27ddaf7c~mv2.jpg', 2, 8),
	('Half-Goose page 3', null, 'https://static.wixstatic.com/media/0fee66_549af2c08b964279a9bb8aa059501abc~mv2.jpg/v1/fill/w_736,h_1105,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_549af2c08b964279a9bb8aa059501abc~mv2.jpg', 3, 8),
	('Medium Ghost page 1', 'title page', 'https://static.wixstatic.com/media/0fee66_5ab377615998471e97c51eaa3b49acf5~mv2.jpg/v1/fill/w_746,h_1043,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_5ab377615998471e97c51eaa3b49acf5~mv2.jpg', 1, 9),
	('Medium Ghost page 2', null, 'https://static.wixstatic.com/media/0fee66_b166cfb214a14ef4ac6d754ff041eb45~mv2.jpg/v1/fill/w_746,h_1043,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_b166cfb214a14ef4ac6d754ff041eb45~mv2.jpg', 2, 9),
	('Medium Ghost page 3', null, 'https://static.wixstatic.com/media/0fee66_c73c9e842eec44d699ff0e892a62661a~mv2.jpg/v1/fill/w_746,h_1043,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/0fee66_c73c9e842eec44d699ff0e892a62661a~mv2.jpg', 3, 9);

	UPDATE project
	SET project_image_id = 1
	WHERE project_id = 1;

	UPDATE project
	SET project_image_id = 2
	WHERE project_id = 2;

	UPDATE project
	SET project_image_id = 3
	WHERE project_id = 3;

	UPDATE project
	SET project_image_id = 4
	WHERE project_id = 4;

	UPDATE project
	SET project_image_id = 5
	WHERE project_id = 5;

	UPDATE project
	SET project_image_id = 9
	WHERE project_id = 6;

	UPDATE project
	SET project_image_id = 11
	WHERE project_id = 7;

	UPDATE project
	SET project_image_id = 16
	WHERE project_id = 8;


	UPDATE project
	SET project_image_id = 19
	WHERE project_id = 9;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE clear_data()
BEGIN
    DELETE from category; DELETE from project;
    DELETE FROM image;
    ALTER TABLE image AUTO_INCREMENT = 1;
    ALTER TABLE project AUTO_INCREMENT = 1;
    ALTER TABLE category AUTO_INCREMENT = 1;
END$$

DELIMITER ;


    
