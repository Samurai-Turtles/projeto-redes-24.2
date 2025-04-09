import socket
from sys import argv

SERVER_IP = "127.0.0.1"
UDP_PORT = "5035"  # Alterar posteriormente


def request_file_over_udp(filename: str):
    """
    Esse passo é dividido em duas etapas:

    1. Cliente solicita, via UDP, a transferência de um arquivo
    2. Servidor responde conforme a validade da requisição
        - Se a requisição for válida, retorna a porta do servidor TCP e o arquivo solicitado
        - Caso contrário, retorna uma mensagem de erro, conforme o problema ocorrido
          (e.g. arquivo inexistente)
    """

    server_address = (SERVER_IP, UDP_PORT)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request_msg = f"REQUEST,TCP,{filename}"

    udp_socket.sendto(request_msg, server_address)
    data, _ = udp_socket.recvfrom(1024)

    print(data)


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
