BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "TB_RELACAO" (
	"id"	INTEGER,
	"relation"	TEXT
);
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (1,'per:corrupcao');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (2,'per:operacao');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (3,'org:operacao');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (4,'org:corrupcao');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (5,'per:lavagemdinheiro');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (6,'per:sonegacao');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (7,'per:suborno');
INSERT INTO "TB_RELACAO" ("id","relation") VALUES (8,'per:traficodeinfluencia');
CREATE INDEX IF NOT EXISTS "id_tb_relation" ON "TB_RELACAO" (
	"id"	ASC
);
CREATE VIEW "vw_corpus_corrupcao" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation in (1,4);
CREATE VIEW "vw_corpus_operacao" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation in (2,3);
CREATE VIEW "vw_corpus_lavagem" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 5;
CREATE VIEW "vw_corpus_sonegacao" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 6;
CREATE VIEW "vw_corpus_suborno" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 7;
CREATE VIEW "vw_corpus_traficoinfluencia" AS SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation = 8;
COMMIT;
