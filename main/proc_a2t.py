from a2t.legacy.relation_classification import NLIRelationClassifierWithMappingHead
from a2t.legacy.relation_classification import REInputFeatures
from sklearn.model_selection import train_test_split
import sqlite3, time, sys
import numpy as np
from timeit import default_timer as timer 
import os

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = ""

import torch
print('-'*20)
print('CUDA device Name Available:')
print(torch.cuda.get_device_name())
print(torch.cuda.list_gpu_processes())
print('-'*20)

global cursor, banco, xserieid, n_th, xproc, mod_er, paramlista_verbalizacao, paramlista_len
xproc = '112'
xserieid = xproc+'.'
n_th = 0.8
xref = 'PROC='+str(xproc)+', NT='+str(n_th)+', '
adiciona_placebo_flag = False
#mod_er = "roberta-large-mnli"
mod_er = "microsoft/deberta-large-mnli"
#mod_er = "facebook/bart-large-mnli"

#mod_er = "Caesarcc/bertimbau-finetune-br-news"
#mod_er = 'neuralmind/bert-base-portuguese-cased'

#paramlista_verbalizacao = '(2,3)' # operacao
#paramlista_verbalizacao = '(8)' # traf de influ
#paramlista_verbalizacao = '(1,4)' # corrupcao
paramlista_verbalizacao= '(1,2,3,4,5,6,7,8)' # todos
#paramlista_verbalizacao = '(5)' # # lavagem de dinheiro
#paramlista_verbalizacao = '(6)' # sonegacao
#paramlista_verbalizacao = '(7)' # suborno
paramlista_len = len([c for c in paramlista_verbalizacao if c.isdigit()])
paramConjuntoMin = 152
paramConjuntoMax = 152
paramExtracao = 'TB_SENTENCA'


banco = sqlite3.connect('corpus.db')
cursor = banco.cursor()

def carrega_verbalizacoes(paramlista_verbalizacao):
    global cursor, banco, relation_verbalizations, relations, valid_conditions
    relations = ['no_relation',]
    cod_relacao = paramlista_verbalizacao
    valid_conditions = {}
    relation_verbalizations = {}
    sql = 'SELECT id, relation FROM TB_RELACAO WHERE id in '+cod_relacao
    cursor.execute(sql)
    resposta = cursor.fetchall()

    for n, relation in resposta:
        #print(n, relation)
        # relation
        relations.append(relation)

        # verbalizacao
        sql2 = 'SELECT verbalizacao FROM TB_VERBALIZACAO WHERE id_relation = '+str(n)+' AND verbalizacao IS NOT NULL'
        verba = cursor.execute(sql2)
        listaverbalizacao = []
        for v in verba:
            listaverbalizacao.append(v[0])
        relation_verbalizations[relation] = listaverbalizacao

        #validRelations
        sql3 = 'SELECT texto FROM TB_VALIDACAO WHERE id in (SELECT DISTINCT id_validCondition FROM TB_VERBALIZACAO WHERE id_relation = '+str(n)+' ORDER BY id_validCondition ASC)'
        cond = cursor.execute(sql3)
        listavalidRelations = []
        for c in cond:
            listavalidRelations.append(c[0])
        #print(listavalidRelations)
        valid_conditions[relation] = listavalidRelations

    print('-'*10)
    print(relations)
    print(len(relations),u' Relações carregadas.')
    print('-'*10)
    print(relation_verbalizations)
    print(' Verbalizações carregadas referentes a '+str(len(relation_verbalizations))+' relações.')
    print('-'*10)
    print(valid_conditions)
    print(len(valid_conditions), u' validConditions carregadas.')



#@jit(target_backend='cuda', nopython=False)
def carrega_configuracoes():
    global clf
    print(u'4-Iniciando carregamento de configurações...')
    tempo_inicial = time.time()
    global relation_verbalizations, relations, valid_conditions, n_th, mod_er
    clf = NLIRelationClassifierWithMappingHead(
        labels=relations,
        template_mapping=relation_verbalizations,
        valid_conditions=valid_conditions,
        pretrained_model = mod_er,
        use_cuda=True,
        negative_threshold=n_th
    )
    print(u'  Carregamento finalizado.')
    tempo_final = time.time()
    tempo_execucao = tempo_final - tempo_inicial
    print('Tempo total: ',str(tempo_execucao))
    return clf


# função utilizada para carregar parte do corpus
def carrega_corpus(lista_id):
    global cursor, banco
    string_lista_id = ', '.join(map(str, lista_id))
    print(string_lista_id)
    print(type(string_lista_id))
    sql = 'SELECT id, sentenca, entity1, entity2, entity_type1, entity_type2, referencia FROM '+paramExtracao+' WHERE id_corpus in ('+str(string_lista_id)+")"
    cursor.execute(sql)
    resultado2 = cursor.fetchall()
    corpus = []

    for id, sentenca, entity1, entity2, entity_type1, entity_type2, referencia in resultado2:
        sentenca = sentenca.replace("'","")
        if entity_type1 == 'B-PER' or entity_type1 == 'B-PESSOA':
            tipo1 = 'PERSON'
        elif entity_type1 == 'B-LOC' or entity_type1 == 'B-LOCAL':
            tipo1 = 'LOCAL'
        elif entity_type1 == 'B-ORG' or entity_type1 == 'B-ORGANIZACAO':
            tipo1 = 'ORGANIZATION'
        elif entity_type1 == 'B-TIM' or entity_type1 == 'B-TIME' or entity_type1 == 'B-TEMPO':
            tipo1 = 'TIME'
        else:
            continue
        if entity_type2 == 'B-PER' or entity_type2 == 'B-PESSOA':
            tipo2 = 'PERSON'
        elif entity_type2 == 'B-LOC' or entity_type2 == 'B-LOCAL':
            tipo2 = 'LOCAL'
        elif entity_type2 == 'B-ORG' or entity_type2 == 'B-ORGANIZACAO':
            tipo2 = 'ORGANIZATION'
        elif entity_type2 == 'B-TIM' or entity_type2 == 'B-TIME' or entity_type2 == 'B-TEMPO':
            tipo2 = 'TIME'
        else:
            continue
        corpus.append(REInputFeatures(subj=entity1, obj=entity2, pair_type=tipo1+':'+tipo2, context=sentenca, label=str(id)))

    print(len(corpus), u' de corpus.')
    return(corpus)


# function optimized to run on gpu 
# nopython = True , modo objeto
#@jit(target_backend='cuda', nopython=False)
def processa(corp, vTrue, vtopk) -> 'list':
    global clf
    resultado = clf.predict(corp, return_confidences=vTrue, topk=vtopk)
    return(resultado)


def executa(corpus, clf):
    tempo_inicial = time.time()
    global cursor, banco, xref, xserieid, xproc, mod_er, paramlista_len, paramExtracao
    if paramlista_len > 1:
        vtopk = 3
    else:
        vtopk = 2
    n = 0
    while True:
        if n >=len(corpus):break
        y = int(corpus[n].label)
        print('-'*20)
        #print(u'id extração nº ',str(y))
        corp = [corpus[n],]

        # essa segunda leitura é necessária porque o corpus preparado para extração não contém todos os elementos necessários para o registro do resultado
        sql = 'SELECT id, sentenca, entity1, entity2, entity_type1, entity_type2, referencia, id_corpus FROM '+paramExtracao+' WHERE id = '+str(y)
        cursor.execute(sql)
        result = cursor.fetchone()
        #print(result)
        xid = result[0]
        xsentenca = result[1]
        xentity1 = result[2]
        xentity2 = result[3]
        xentity_type1 = result[4]
        xentity_type2 = result[5]
        xreferencia = xref+result[6]
        xid_corpus = result[7]



        # id_extracao = [ano][proc][id]
        xid_extracao = str(xserieid)+str(xid)
        print('xid_extracao: ',xid_extracao)
        print('xid_corpus: ',xid_corpus)
        sql4 = "SELECT id FROM TB_RESULTADO WHERE id_extracao ="+str(xid_extracao)
        cursor.execute(sql4)
        r = cursor.fetchone()
        if r is None:
            sql2= "INSERT INTO TB_RESULTADO (sentenca, entity1, entity2, entity_type1, entity_type2, referencia, id_corpus, id_extracao) VALUES ('"+str(xsentenca)+"', '"+str(xentity1)+"', '"+str(xentity2)+"', '"+str(xentity_type1)+"', '"+str(xentity_type2)+"', '"+str(xreferencia)+"', "+str(xid_corpus)+", "+str(xid_extracao)+")"
            #print(sql2)
            cursor.execute(sql2)

            #print('INSERT executado')
            #print(corp)
            #print(type(corp))
            #resultado = clf.predict(corp, return_confidences=True, topk=vtopk)
            resultado = processa(corp, True, vtopk)
            #print('Tipo de resultado: ',type(resultado))

            res_relation1 = resultado[0][0]
            res_relation1_desc = res_relation1[0]
            res_relation1_score = res_relation1[1]
            print(' ',res_relation1_score, res_relation1_desc)
            res_relation2 = resultado[0][1]
            res_relation2_desc = res_relation2[0]
            res_relation2_score = res_relation2[1]
            print(' ',res_relation2_score, res_relation2_desc)
            if vtopk == 3:
                res_relation3 = resultado[0][2]
                res_relation3_desc = res_relation3[0]
                res_relation3_score = res_relation3[1]
                print(' ',res_relation3_score, res_relation3_desc)
            
            if paramlista_len > 1:
                # mínimo de 3 verbalizações
                sql3 = "UPDATE TB_RESULTADO SET proc = '"+xproc+"', mod_er = '"+mod_er+"',relation1 = '"+res_relation1_desc+"',score1 = '"+str(res_relation1_score)+"',relation2 = '"+res_relation2_desc+"',score2 = '"+str(res_relation2_score)+"',relation3 = '"+res_relation3_desc+"',score3 = '"+str(res_relation3_score)+"' WHERE id_extracao="+str(xid_extracao)
            else:
                # mínimo de 2 verbalizações
                sql3 = "UPDATE TB_RESULTADO SET proc = '"+xproc+"', mod_er = '"+mod_er+"',relation1 = '"+res_relation1_desc+"',score1 = '"+str(res_relation1_score)+"',relation2 = '"+res_relation2_desc+"',score2 = '"+str(res_relation2_score)+"' WHERE id_extracao="+str(xid_extracao)

            cursor.execute(sql3)
            banco.commit()
            #print('Concluído '+str(xid_extracao))
            print('-'*20)
        n += 1
    banco.close()
    tempo_final = time.time()
    tempo_execucao = tempo_final - tempo_inicial
    print('Tempo total: ',str(tempo_execucao))



def cria_conjunto_MinMax(idmin, idmax):
    sql = 'SELECT id FROM TB_CORPUS WHERE id >= '+str(idmin)+' AND id <= '+str(idmax)
    cursor.execute(sql)
    docpre = cursor.fetchall()
    docs = []
    for d in docpre:
        docs.append(d[0])
    return(docs)


def cria_conjunto_verbalizacao(paramlista):
    cod_relacao = paramlista
    sql = 'SELECT DISTINCT id_corpus FROM TB_VERBALIZACAO WHERE id_relation in '+cod_relacao
    cursor.execute(sql)
    docpre = cursor.fetchall()
    docs = []
    for d in docpre:
        docs.append(d[0])
    return(docs)


def adiciona_placebo(conjuntopre):
    for x in range(101,151):
        conjuntopre.append(x)
    return(conjuntopre)


def main():
    global paramlista
    print('-'*20)
    print(u'1-Carregando relações,verbalizações e relações válidas...')

    carrega_verbalizacoes(paramlista_verbalizacao)
    #sys.exit()
    print('-'*20)
    clf = carrega_configuracoes()
    print('-'*20)
    # cria conjunto
    print(u'5-Criando conjunto...')
    #conjuntopre = cria_conjunto_verbalizacao(paramlista)
    conjuntopre = cria_conjunto_MinMax(paramConjuntoMin,paramConjuntoMax)

    if adiciona_placebo_flag == True:
        conjunto = adiciona_placebo(conjuntopre)
    else:
        conjunto = conjuntopre
    print('-'*20)
    print(u'6-Criando corpus...')
    print(len(conjunto))
    print('-'*20)
    #x = cria_corpus()
    print('-'*20)
    x = carrega_corpus(conjunto)
    print('-'*20)
    print(u'7-Executando...')
    executa(x, clf)
    print('-'*20)
    try:
    	banco.close()
    except:
    	pass
    print(u'8-Finalizado.')


if __name__ == '__main__':
	main()
