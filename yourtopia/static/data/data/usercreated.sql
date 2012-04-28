-- Table: usercreated
CREATE TABLE usercreated ( 
    id          INTEGER         PRIMARY KEY ASC AUTOINCREMENT,
    user_name   VARCHAR( 100 ),
    user_url    VARCHAR( 150 ),
    description TEXT( 300 ),
    weights     TEXT( 1000 ),
    created_at  DATETIME        NOT NULL,
    user_ip     VARCHAR( 15 ),
    country     VARCHAR( 3 ),
    version     INTEGER 
);
