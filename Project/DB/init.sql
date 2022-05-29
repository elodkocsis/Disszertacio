CREATE TABLE Pages (
    url text PRIMARY KEY,
    date_accessed timestamp,
    page_content text,
    meta_tags json,
    parent_url text,
    new_url bool NOT NULL,
    date_added timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO Pages (url, new_url) VALUES
('http://www.example1.com', true),
('http://www.example2.com', true),
('http://www.example2.com/some_page', true);
