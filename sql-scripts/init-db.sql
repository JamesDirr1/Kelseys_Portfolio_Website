CREATE TABLE IF NOT EXISTS category (
    category_id TINYINT AUTO_INCREMENT PRIMARY KEY,
    category_title VARCHAR(100),
    category_order TINYINT UNIQUE
);

-- Create the project table
CREATE TABLE IF NOT EXISTS project (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    project_title VARCHAR(255) NOT NULL,
    project_date DATE NOT NULL,
    project_desc VARCHAR(255),
    category_id TINYINT,
    project_image_id INT,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE CASCADE
);

-- Create the image table
CREATE TABLE IF NOT EXISTS image (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    image_title VARCHAR(255),
    image_desc VARCHAR(255),
    image_URL VARCHAR(2083) NOT NULL,
    image_weight TINYINT,
    project_id INT,
    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE
);

CREATE or Replace view `VV.category` AS
    SELECT category_id, category_title, category_order
    FROM category;

CREATE or Replace view `VV.project` AS
    SELECT project_id, project_date, project_desc, project.category_id, project_image_id
    FROM project;

CREATE or Replace view `VV.image` AS
    SELECT image_id, image_title, image_desc, image_URL, image_weight, image.project_id
    FROM image;


    
