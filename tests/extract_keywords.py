import spacy

# carregar modelo em português (precisa rodar: python -m spacy download pt_core_news_sm)
nlp = spacy.load("pt_core_news_sm")


def extrair_palavras_chave(texto):
    doc = nlp(texto)
    palavras_chave = [
        token.text
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop
    ]
    return list(set(palavras_chave))


prompt = "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?"
print(extrair_palavras_chave(prompt))
