from sklearn.metrics import confusion_matrix
import sqlite3
import numpy as np

from datetime import datetime
now = datetime.now()

# Defina o número do processamento
vproc = '106'
# Defina o código da relação analisada para busca do universo positivo
cod_relacao = '(1,2,3,4,5,6,7,8)'   #cod_relacao = '(1,2,3,4,5,6,7,8)'
cod_relacao2 = {1,2,3,4,5,6,7,8}
# Defina o conjunto Universo
global universo
universo = set(range(1, 151))

banco = sqlite3.connect('corpus.db')
cursor = banco.cursor()


print(u'AVALIAÇÃO DO PROCESSAMENTO')
print('-'*20)
print('Avaliação do proc = ',vproc)
print(u'Relações: ', cod_relacao)
print('Data de Processamento: ', now)
print('-'*20)

# Cálculo do gabarito positivo (relação verdadeira)
sql2 = """
    SELECT DISTINCT id_corpus, id_relation
    FROM verbalizacao
    LEFT JOIN relation ON verbalizacao.id_relation = relation.id
    WHERE id_corpus <= ?
    ORDER BY id_corpus
"""
cursor.execute(sql2, (max(universo),))
resposta2 = cursor.fetchall()

positivo = set((id_corpus, id_relation) for id_corpus, id_relation in resposta2 if id_relation in cod_relacao2)
positivo3 = set((id_corpus) for id_corpus, id_relation in resposta2 if id_relation in cod_relacao2)
print()
print('id_corpus positivos: ', len(positivo3))
print(sorted(positivo3))
print()
print('gabarito positivo: ', len(positivo))
print(sorted(positivo))

# Cálculo do resultado
sql1 = """
SELECT
        id_corpus,
        id_relation
    FROM (
        SELECT
            id_corpus,
            relation1, Relation.id as id_relation,
            MAX(score1) AS max_score
        FROM Processados
        LEFT JOIN Relation ON Processados.relation1 = Relation.relation
        WHERE proc = """+vproc+""" AND relation1 <> 'no_relation' AND id_corpus <= ?
        GROUP BY id_corpus
    ) AS max_scores
    WHERE max_scores.max_score IS NOT NULL

"""

cursor.execute(sql1, (max(universo),))
resposta1 = cursor.fetchall()

resultado = set((id_corpus, id_relation) for id_corpus, id_relation in resposta1)
resultado3 = set((id_corpus) for id_corpus, id_relation in resposta1)
print()
print('id_corpus resultado: ', len(resultado3))
print(resultado3)
print()
print('resultado: ', len(resultado))
print(sorted(resultado))

global VP, FP, VN, FN, gVP, gFP, gVN, gFN
VP = 0
FP = 0
VN = 0
FN = 0

gVP = []
gFP = []
gVN = []
gFN = []

def proc_positivo(xres, xpositivo):

    for pos in xpositivo:
        if pos == xres:
            return True
    return False 

def avalia_resultado(vresultado, vpositivo):
    global VP, FP, gVP, gFP
    for res in vresultado:
        if proc_positivo(res,vpositivo) == True:
            VP += 1
            gVP.append(res)
        else:
            FP += 1
            gFP.append(res)
    return

def avalia_negativos(xresultado3, xpositivo3, xuniverso):
    global VN, FN, gVN, gFN
    for uni in xuniverso:
        if uni not in xresultado3:
            if uni not in xpositivo3:
                VN += 1
                gVN.append(uni)
            else:
                FN += 1
                gFN.append(uni)
    return

avalia_resultado(sorted(resultado), sorted(positivo))
avalia_negativos(resultado3, positivo3, universo)


if VP < 10:
    vlVP = '0'+str(VP)
else:
    vlVP = str(VP)

if FP < 10:
    vlFP = '0'+str(FP)
else:
    vlFP = str(FP)


if VN < 10:
    vlVN = '0'+str(VN)
else:
    vlVN = str(VN)

if FN < 10:
    vlFN = '0'+str(FN)
else:
    vlFN = str(FN)

print('Avaliação do proc = ',vproc)
print(u'Relações: ', cod_relacao)
print()
print()
print()
print(u'          MATRIZ DE CONFUSÃO           ')
print()
print('            V           F')
print('      _________________________')
print('      |           |           |')
print('  P   |    '+vlVP+'     |     '+vlFP+'    |')
print('  N   |    '+vlVN+'     |     '+vlFN+'    |')
print('      |           |           |')
#print('      _________________________')
print()
print()
print()
print('gVP: ')
print(gVP)
print()
print('gVN: ')
print(gVN)
print()
print('gFP: ')
print(gFP)
print()
print('gFN: ')
print(gFN)
print()
print()
vPrecision = VP / (VP + FP)
print('vPrecision: ', vPrecision)
print()
vRecall = VP / (VP + FN)
print('vRecall/vSensitivity: ', vRecall)
print()
vF1Score = 2*(vPrecision*vRecall) / (vPrecision + vRecall)
print('vF1Score: ', vF1Score)
print()
vAccuracy = (VP + VN) / (VN + VP + FP + FN)
print('vAccuracy: ', vAccuracy)
print()