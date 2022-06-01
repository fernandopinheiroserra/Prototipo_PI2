DROP TABLE IF EXISTS funcionarios;
DROP TABLE IF EXISTS turmas;
DROP TABLE IF EXISTS alunos;
DROP TABLE IF EXISTS historicos;

CREATE TABLE funcionarios (
	func_id	INTEGER not null primary key autoincrement,
	func_nome	TEXT NOT NULL,
	func_cargo	TEXT NOT NULL,
	func_username text not NULL,
	func_password TEXT NOT NULL,
	func_obs TEXT
);

CREATE TABLE turmas (
	trm_id	INTEGER NOT NULL primary key autoincrement,
    trm_ativo Boolean,
	trm_cod_prof	INTEGER	NOT NULL,
	trm_horario TEXT,
	trm_obs	TEXT,
	FOREIGN KEY("trm_cod_prof") references funcionarios("func_id")
);

CREATE TABLE alunos (
	aln_id	INTEGER NOT NULL primary KEY,
    aln_matriculado Boolean,
	aln_nome	TEXT NOT NULL,
	aln_serie	INTEGER NOT NULL,
	aln_turma	INTEGER NOT NULL,
	aln_nivel	INTEGER NOT NULL,
	aln_email_resp TEXT,
	aln_obs	TEXT,
	FOREIGN KEY("aln_turma") references turmas("trm_id")
);

CREATE TABLE historicos (
	hst_id	INTEGER NOT NULL primary key autoincrement,
	hst_cod_aln INTEGER NOT NULL,
	hst_nv_ant INTEGER NOT null,
	hst_nv_atual INTEGER NOT NULL,
	hst_data_alt	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	hst_cod_alt INTEGER NOT null,
	hst_cod_aprov INTEGER NOT NULL,
	hst_trm_ant INTEGER NOT null,
	hst_trm_atual INTEGER NOT NULL,
	hst_obs TEXT,
	FOREIGN KEY("hst_cod_aln") references alunos("aln_id"),
	FOREIGN KEY("hst_trm_ant") references turmas("trm_id"),
	FOREIGN KEY("hst_trm_atual") references turmas("trm_id")
);