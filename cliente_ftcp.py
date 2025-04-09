from sys import argv


def request_file_over_udp():
    """
    Esse passo é dividido em duas etapas:

    1. Cliente solicita, via UDP, a transferência de um arquivo
    2. Servidor responde conforme a validade da requisição
        - Se a requisição for válida, retorna a porta do servidor TCP e o arquivo solicitado
        - Caso contrário, retorna uma mensagem de erro, conforme o problema ocorrido
          (e.g. arquivo inexistente)
    """
    pass


def download_file_over_tcp():
    """
    Este passo é dividido em quatro etapas:

    1. Cliente estabelece conexão com o servidor TCP
    2. Cliente solicita o arquivo para transferência
    3. Servidor transfere o arquivo solicitado
    4. Cliente verifica o tamanho da arquivo e retorna um ACK para o servidor
    """
    pass


if __name__ == "__main__":
    requested_file = argv[1]
