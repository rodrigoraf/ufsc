BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "ValidCondition" (
	"id"	INTEGER,
	"texto"	TEXT,
	PRIMARY KEY("id")
);
INSERT INTO "ValidCondition" ("id","texto") VALUES (1,'PERSON:PERSON');
INSERT INTO "ValidCondition" ("id","texto") VALUES (2,'ORGANIZATION:ORGANIZATION');
INSERT INTO "ValidCondition" ("id","texto") VALUES (3,'ORGANIZATION:PERSON');
INSERT INTO "ValidCondition" ("id","texto") VALUES (4,'PERSON:ORGANIZATION');
INSERT INTO "ValidCondition" ("id","texto") VALUES (5,'ORGANIZATION:LOCATION');
INSERT INTO "ValidCondition" ("id","texto") VALUES (6,'PERSON:LOCATION');
INSERT INTO "ValidCondition" ("id","texto") VALUES (7,'ORGANIZATION:TIME');
INSERT INTO "ValidCondition" ("id","texto") VALUES (8,'PERSON:TIME');
INSERT INTO "ValidCondition" ("id","texto") VALUES (9,'LOCATION:TIME');
CREATE INDEX IF NOT EXISTS "id_tb_validCondition" ON "ValidCondition" (
	"id"	ASC
);
CREATE VIEW "vw_corpus_corrupcao" AS SELECT DISTINCT id_corpus FROM verbalizacao WHERE id_relation in (1,4);
CREATE VIEW "vw_corpus_operacao" AS SELECT DISTINCT id_corpus FROM verbalizacao WHERE id_relation in (2,3);
CREATE VIEW "vw_corpus_lavagem" AS SELECT DISTINCT id_corpus FROM verbalizacao WHERE id_relation = 5;
CREATE VIEW "vw_corpus_sonegacao" AS SELECT DISTINCT id_corpus FROM verbalizacao WHERE id_relation = 6;
CREATE VIEW "vw_corpus_suborno" AS SELECT DISTINCT id_corpus FROM verbalizacao WHERE id_relation = 7;
CREATE VIEW "vw_corpus_traficoinfluencia" AS SELECT DISTINCT id_corpus FROM verbalizacao WHERE id_relation = 8;
COMMIT;
