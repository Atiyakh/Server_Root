-- The following table names are forbidden [archive, record]
-- Use the same structure following the pattern of the comments below
-- MySql DBMS are strongly recommended

/*START*/
CREATE TABLE accounts(
	id INT AUTO_INCREMENT,
	username VARCHAR(50) UNIQUE,
	password VARCHAR(128) NOT NULL,
	PRIMARY KEY (id)
);
/*END*/