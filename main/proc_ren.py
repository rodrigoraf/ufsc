# proc_ren2.py
# Script para sentenciar, tokenizar e classificar documentos

import sqlite3, spacy
from transformers import BertTokenizer, BertForTokenClassification
import torch

modelo1 = 'Luciano/bertimbau-base-lener_br'
modelo2 = 'spacy/pt_core_news_lg'
modelo3 = 'arubenruben/PT-BERT-CRF'
modelo4 = 'monilouise/ner_news_portuguese' 
modelo5 = 'marcosgg/bert-large-pt-ner-enamex'
modelo6 = 'marquesafonso/bertimbau-large-ner-selective'
modelo7 = 'neuralmind/bert-base-portuguese-cased'
modelo8 = 'neuralmind/bert-large-portuguese-cased'
modelo = modelo1
global paramCorpus
# Atenção: Antes de alterar o paramCorpus, certifique que a tabela foi criada.
paramCorpus = 'Corpus_caso1'    # tabela de dados do Corpus. Padrão: 'Corpus'

banco_origem = sqlite3.connect('corpus.db')
cursor_origem = banco_origem.cursor()

sql = "SELECT DOC.id, DOC.texto FROM Corpus DOC WHERE DOC.id = 151"
#AND Doc.id <= 100"
cursor_origem.execute(sql)
result_origem = cursor_origem.fetchall()

# Carregue o modelo BERT pré-treinado
model = BertForTokenClassification.from_pretrained(modelo)

# Carregue o tokenizer correspondente
tokenizer = BertTokenizer.from_pretrained(modelo)

# Carregue o tokenizer do spacy
nlp = spacy.load("pt_core_news_sm")

# Módulo para extrair entidades
def extrai_entidades(arg):
	# Tokenize o texto de entrada
	tokens = tokenizer.tokenize(arg)

	# Adicione tokens especiais de início e fim de sequência
	tokens = ['[CLS]'] + tokens + ['[SEP]']

	# Converta os tokens em IDs de token
	input_ids = tokenizer.convert_tokens_to_ids(tokens)

	# Crie um tensor de entrada
	input_tensor = torch.tensor([input_ids])

	# Obtenha as previsões do modelo
	outputs = model(input_tensor)
	predictions = torch.argmax(outputs.logits, dim=2)

	# Converta as previsões de volta para rótulos de entidades
	predicted_label_ids = predictions[0].tolist()
	predicted_labels = [model.config.id2label[label_id] for label_id in predicted_label_ids]

	# Mapeie os tokens e os rótulos de entidades resultantes
	entities = []
	for token, label in zip(tokens, predicted_labels):
		#if label != 'O':  # Ignorar rótulos 'O' (outras)
		entities.append({'word': token, 'entity': label})

	# Imprima os resultados
	return(entities)

# Código para tratar o resultado da REN juntando tokens da mesma entidade
def extract_named_entities(tokens):
	named_entities = []
	entity_tags = {}

	i = 0
	while i < len(tokens):
		if tokens[i]['entity'].startswith('B-'):
			entity_label = tokens[i]['entity'][2:]
			entity = tokens[i]['word'].replace('##', '')
			i += 1
			while i < len(tokens) and tokens[i]['entity'] == 'I-' + entity_label:
				if '##' in tokens[i]['word']:
					entity += tokens[i]['word'].replace('##', '')
				else:
					entity += ' ' + tokens[i]['word']
				i += 1
			named_entities.append(entity)
			entity_tags[entity] = 'B-' + entity_label
		else:
			i += 1

	return [{'word': entity, 'entity': entity_tags[entity]} for entity in named_entities]


def tratar_lista(items):
	global paramCorpus
	new_items = []

	i = 0
	while i < len(items):
		new_item = ''
		current_item = items[i]

		if current_item['entity'].startswith('B') and i < len(items)-1:
			next_item = items[i+1]
			try:
				next_next_item = items[i+2]
				condicao3 = next_next_item['entity'].startswith('I') and next_next_item['word'].startswith('##') and next_item['entity'][2:] == next_next_item['entity'][2:]
			except:
				next_next_item = 0
				condicao3 = False
			condicao1 = next_item['entity'].startswith('I') and current_item['entity'][2:] == next_item['entity'][2:]
			condicao2 = next_item['word'].startswith('##') and next_item['entity'][2:] == current_item['entity'][2:]


			if condicao1 or condicao2:
				if next_item['word'].startswith('##'):
					new_word = current_item['word']+next_item['word'].replace('##','')
				else:
					new_word = current_item['word']+' '+next_item['word']
				if condicao3:
					new_word = new_word + next_next_item['word'].replace('##','')
					i += 3
				else:
					i += 2
				new_entity = 'B-'+current_item['entity'][2:]
				new_item = {'word': new_word, 'entity': new_entity}
				new_items.append(new_item)
				continue

		new_items.append(current_item)
		i += 1

	return(new_items)


#for id_arquivo, nome_arquivo, texto in result_origem:
for id, texto in result_origem:
	print(str(id))
	#if id < 23: continue #para reiniciar processo já gravado no banco

	# sentenciando para fazer o REN
	for x in nlp(texto).sents:
		if len(x) <= 2:
			continue
		sentenca = x.text.replace("'"," ").replace('"','')
		try:
			res = extrai_entidades(sentenca)
			#print(res)
		except:
			continue
		

		for item in res:
			token = item['word']
			classif = item['entity']

			#sql_insert = "INSERT INTO CorpusPrata (id_documento, token, classificacao, modelo) VALUES ("+str(int(id)+9000)+",'"+token+"','"+classif+"','"+modelo+"');"

			sql_insert = "INSERT INTO "+paramCorpus+" (id_documento, token, classificacao) VALUES ("+str(id)+",'"+token+"','"+classif+"');"	

			if len(sentenca) >0:
				cursor_origem.execute(sql_insert)
				banco_origem.commit()
				
banco_origem.close()