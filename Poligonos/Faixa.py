# ************************************************
#   Faixa.py
#   Define as classes Faixa e ConjuntoDeFaixas
#   Autor: Márcio Sarroglia Pinho
#   pinho@pucrs.br
#   Abril 2021
# ************************************************
class Faixa:
# Esta classe armazena uma lista de inteiros, que representa as arestas
# que estao dentro de uma certa faixa
    def __init__(self):
        self.ArestasNaFaixa = [] # atributo do objeto

    def getNroDeArestas(self):
        return len(self.ArestasNaFaixa)

    def CadastraAresta(self, a):
        self.ArestasNaFaixa += [a]

    def getAresta(self, i):
        return self.ArestasNaFaixa[i]

class ConjuntoDeFaixas:
# Esta classe armazena uma lista de Faixa
    def __init__(self):
        self.TodasAsFaixas = [] # atributo do objeto

    def CadastraArestaNaFaixa(self, f, a):
        self.TodasAsFaixas[f].CadastraAresta(a)

    def CriaFaixas(self, qtdDeFaixas): # pode ser substituida por uma construtora
        for i in range(qtdDeFaixas):
            self.TodasAsFaixas += [Faixa()]

    def getFaixa(self, f):
        return self.TodasAsFaixas[f]


