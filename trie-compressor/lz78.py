import argparse

#Objetos do tipo Node serao usados para criacao da trie
class Node:

    def __init__(self, character, number, parent):

        #atributos de um objeto Node
        self.character = character
        self.sons = dict()
        self.number = number
        self.parent = parent


#funcao auxiliar para converter os parametros passados para bytes
def convert_to_bytes(number, character):

    #converte o numero e o caractere para bytes
    num_bytes = number.to_bytes((number.bit_length()-1)//8 + 1, "little")
    chr_bytes = bytes(character, encoding = "utf8")

    #gera-se mais um byte para que se saiba quantos bytes foram
    #necessarios para guardar o numero e o caractere
    if number == 0:
        info = len(bytes(character, encoding = "utf8"))
    else:
        info = ((number.bit_length()-1)//8 + 1)*16 + len(bytes(character, encoding = "utf8"))
        
    info_bytes = info.to_bytes(1, "little")
    
    return info_bytes, num_bytes, chr_bytes


#funcao que comprime o texto passado por meio de uma trie 
def create_trie_and_encoding(text, filename):

    #variaveis para realizacao do processamento
    root = Node("", 0, -1)
    actual_node = root
    number, tam, character = 1, len(text), ""

    #abertura do arquivo
    arq = open(filename, "wb")

    #iteracao sobre os caracteres do texto
    for i in range(tam):
        
        character = text[i]

        #se o no atual nao possuir um filho com o caractere, foi encontrado um novo prefixo no texto
        if character not in actual_node.sons:
            
            actual_node.sons[character] = Node(character, number, actual_node.number)

            #escreve-se os valores correspondentes ao novo prefixo no arquivo binario
            info, num, charac = convert_to_bytes(actual_node.number, character)
            arq.write(info)
            arq.write(num)
            arq.write(charac)

            #retorna-se para a raiz para procura de um novo prefixo
            actual_node = root
            number += 1

        #se o no atual ja possuir um filho com o caractere
        #esse filho se torna o novo no atual
        else:
            actual_node = actual_node.sons[character]

    #se o texto terminar no meio de um prefixo que ja esta na trie
    #deve-se escrever no arquivo os valores das variaveis atuais para
    #que se possa reconstruir o final do texto na etapa de descompressao
    if actual_node != root:
        
        info, num, charac = convert_to_bytes(actual_node.number, "")
        arq.write(info)
        arq.write(num)

    #fechameto do arquivo
    arq.close()
    
    return root

#funcao para descomprimir um arquivo 
def decoding(filename, output_filename):

    #abertura dos arquivos
    arq = open(filename, "rb")
    arq_output = open(output_filename, "w", encoding = "utf8")

    #variaveis utilizadas para descompressao
    byte = arq.read(1)
    characters = [""]
    parents = [0]
    
    while byte:

        #leitura dos bytes para decodificacao
        text = ""
        info = int.from_bytes(byte, "little")
        
        num_bytes= info // 16
        chr_bytes = info % 16
        
        byte = arq.read(num_bytes)
        index = int.from_bytes(byte, "little")
        
        byte = arq.read(chr_bytes)
        charac = byte.decode("utf8")

        #novos dados lidos sao adicionados nas listas
        #para realizar futuras decodificacoes
        characters.append(charac)
        parents.append(index)

        #decodificando um trecho do texto origianl
        while(index != 0):
            text = characters[index] + text
            index = parents[index]

        #escreve-se o trecho no arquivo
        text += charac
        arq_output.write(text)

        #leitura do proximo byte para a iteracao seguinte 
        byte = arq.read(1)

    #fechamento dos arquivos
    arq.close()
    arq_output.close()


def main():

    #etapa necessaria para capturar parametros da linha de comando
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--compressing', action='store_true')
    group.add_argument('-x', '--decompressing', action='store_true')
    parser.add_argument('filename', type=str, help='Input filename')
    parser.add_argument('-o','--output', help='Optional output file name')
    args = parser.parse_args()

    filename = args.filename

    #condicao para executar a funcao de compressao
    if args.compressing:
        arq = open(filename, "r", encoding = "utf8")
        text = arq.read()
            
        if args.output == None:
            tree = create_trie_and_encoding(text, filename.split(".")[0] + ".z78")
        else:
            tree = create_trie_and_encoding(text, args.output)

        arq.close()

    #condicao para executar a funcao de descompressao
    elif args.decompressing:
        if args.output == None:
            decoding(filename, filename.split(".")[0] + ".txt")
        else:
            decoding(filename, args.output)

    
main()






