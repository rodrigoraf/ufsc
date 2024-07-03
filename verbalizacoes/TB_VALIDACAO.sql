BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "TB_VALIDACAO" (
	"id"	INTEGER,
	"texto"	TEXT,
	PRIMARY KEY("id")
);
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (1,'PERSON:PERSON');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (2,'ORGANIZATION:ORGANIZATION');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (3,'ORGANIZATION:PERSON');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (4,'PERSON:ORGANIZATION');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (5,'ORGANIZATION:LOCATION');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (6,'PERSON:LOCATION');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (7,'ORGANIZATION:TIME');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (8,'PERSON:TIME');
INSERT INTO "TB_VALIDACAO" ("id","texto") VALUES (9,'LOCATION:TIME');
CREATE INDEX IF NOT EXISTS "id_tb_validCondition" ON "TB_VALIDACAO" (
	"id"	ASC
);
CREATE VIEW "vw_corpus_corrupcao" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation in (1,4);
CREATE VIEW "vw_corpus_operacao" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation in (2,3);
CREATE VIEW "vw_corpus_lavagem" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 5;
CREATE VIEW "vw_corpus_sonegacao" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 6;
CREATE VIEW "vw_corpus_suborno" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 7;
CREATE VIEW "vw_corpus_traficoinfluencia" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 8;
COMMIT;