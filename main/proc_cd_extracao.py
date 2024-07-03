import sqlite3, time, sys
from itertools import permutations
# to measure exec time
from timeit import default_timer as timer 

tempo_inicial = time.time()

# Configurações de documentos do corpus (1 a 150, p.ex.)
vMin = 1
vMax = 150
modelo_ren = 'Luciano/bertimbau-base-lener_br'
refer = 'Estudo de caso'
paramExtracao = 'TB_SENTENCA_CASO' # 'TB_SENTENCA'
paramCorpus = 'TB_CORPUS_CASO'    # 'TB_CORPUS'

def combine_entities_permutacao(sentences_with_entities):
    combined_entities = []

    for sentence_data in sentences_with_entities:
        entities = sentence_data['entities']

        # Gerar todas as combinações possíveis de entidades
        entity_permutations = list(permutations(entities, 2))

        for entity_pair in entity_permutations:
            entity1, entity2 = entity_pair

            # Adiciona o par de entidades à lista
            combined_entities.append({
                'sentence': sentence_data['text'],
                'entity1': entity1,
                'entity2': entity2
            })

    return combined_entities

def combine_entities(sentences_with_entities):
    combined_entities = []

    for sentence_data in sentences_with_entities:
        entities = sentence_data['entities']

        # Combinação 2 a 2 das entidades
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity1 = entities[i]
                entity2 = entities[j]

                # Adiciona o par de entidades à lista
                combined_entities.append({
                    'sentence': sentence_data['text'],
                    'entity1': entity1,
                    'entity2': entity2
                })

    return combined_entities

def extract_entities(data):
    sentences = []
    current_sentence = []

    for token in data:
        #print(current_sentence)
        if token[1] == '[SEP]':
            if current_sentence:
                sentences.append(current_sentence[1:])  # Remove [CLS] from the beginning
            current_sentence = []
        elif token[1].startswith('##'):
            # Junta com o token anterior sem espaços
            current_sentence[-1] = (current_sentence[-1][0] + token[1][2:], current_sentence[-1][1])
        elif token[1] in [',', '.']:
            # Junta com o token anterior sem espaços
            current_sentence[-1] = (current_sentence[-1][0] + token[1], current_sentence[-1][1])
        elif token[1].startswith('I-'):
            # Junta com o token anterior com espaços
            current_sentence[-1] = (current_sentence[-1][0] + ' ' + token[1][2:], current_sentence[-1][1])
        else:
            current_sentence.append((token[1], token[2] if len(token) > 2 else 'O'))

    # Adiciona a última sentença se não terminou com [SEP]
    if current_sentence:
        sentences.append(current_sentence[1:])  # Remove [CLS] from the beginning

    result = []
    for sentence in sentences:
        #print(sentence)
        text = ' '.join([token[0] for token in sentence])
        entities = []
        prev_entity_type = None
        for token in sentence:
            if token[1] == 'O':
                prev_entity_type = None
                continue

            if token[1].startswith('I-'):
                # Agrupa a entidade ao anterior mantendo apenas a classificação anterior
                #print('entities[-1][0] - ',entities[-1][0])
                #print('token - ',token[0])
                #print('entities[-1][1] - ',entities[-1][1])
                try:
                    entities[-1] = (entities[-1][0] + ' ' + token[0], entities[-1][1])
                except:
                    # desabilitado erro de iniciar com I-
                    #print(sentence)
                    #print(token)
                    #sys.exit()
                    pass
            else:
                entities.append((token[0], token[1]))

        result.append({'text': text, 'entities': entities})
    
    return result


banco_origem = sqlite3.connect('corpus.db')
cursor_origem = banco_origem.cursor()

# neste range deve-se colocar o primeiro e último+1 documentos
# original é range(1, 51) que trabalha com documentos de 1 a 50
vMax += 1 # incrementa o vMax para a utilização no range.
for id_documento in range(vMin, vMax+1):

    sql = 'SELECT id, token, classificacao FROM '+paramCorpus+' WHERE id_documento = '+str(id_documento)
    cursor_origem.execute(sql)
    resultado = cursor_origem.fetchall()
    #print(resultado)
    #print(len(resultado))

    #print(resultado)

    sentences_with_entities = extract_entities(resultado)
    combined_entities = combine_entities_permutacao(sentences_with_entities)

    # Exibindo os pares de entidades
    for pair in combined_entities:
        ventity1 = str(pair['entity1'][0]).replace(',','').replace('.','')
        ventity2 = str(pair['entity2'][0]).replace(',','').replace('.','')
        ventity_type1 = pair['entity1'][1]
        ventity_type2 = pair['entity2'][1]
        sql = "INSERT INTO "+paramExtracao+" (sentenca, mod_ren, entity1, entity2, entity_type1, entity_type2, referencia, id_corpus) VALUES ('"+pair['sentence']+"','"+modelo_ren+"','"+ventity1+"','"+ventity2+"','"+ventity_type1+"','"+ventity_type2+"','"+refer+"',"+str(id_documento)+")"
        #print(sql)
        cursor_origem.execute(sql)
        banco_origem.commit()

        # print("Sentença:", pair['sentence'])
        # print("Entidade 1:", pair['entity1'])
        # print("Entidade 2:", pair['entity2'])
        # print("\n")
    print(id_documento)

banco_origem.close()

tempo_final = time.time()
tempo_execucao = tempo_final - tempo_inicial
print('Tempo total: ',str(tempo_execucao))
