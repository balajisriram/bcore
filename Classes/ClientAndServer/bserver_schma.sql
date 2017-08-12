CREATE TABLE stations (
	id integer PRIMARY KEY AUTOINCREMENT,
	type varchar,
	version integer,
	obj blob
);

CREATE TABLE subjects (
	id integer PRIMARY KEY AUTOINCREMENT,
	alt_id varchar,
	species varchar,
	gender text,
	strain varchar,
	gene_bkgd varchar,
	obj blob
);
