CREATE TABLE pages (
    url text PRIMARY KEY,
    date_accessed timestamp,
    page_title text,
    page_content text,
    meta_tags json,
    parent_url text,
    new_url bool NOT NULL,
    date_added timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO pages (url, new_url) VALUES
('http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/discover', true),
('http://liberalhf5hjefibussfn2mvqauks7pkfrmsaaymnamx7rrcstsrdpyd.onion/', true),
('http://donionsixbjtiohce24abfgsffo2l4tk26qx464zylumgejukfq2vead.onion/', true),
('http://wiki47qqn6tey4id7xeqb6l7uj6jueacxlqtk3adshox3zdohvo35vad.onion/', true);
