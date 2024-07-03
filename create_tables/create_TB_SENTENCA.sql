CREATE TABLE "TB_SENTENCA" (
	"id"	INTEGER,
	"sentenca"	TEXT NOT NULL,
	"mod_ren"	TEXT,
	"entity1"	TEXT NOT NULL,
	"entity2"	TEXT NOT NULL,
	"entity_type1"	TEXT NOT NULL,
	"entity_type2"	TEXT NOT NULL,
	"referencia"	TEXT,
	"id_corpus"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
	)
