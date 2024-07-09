class ComunicacaoMicrocontrolador:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def ligar_valvula(self):
        self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "ligar_valvula")

    def desligar_valvula(self):
        self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "desligar_valvula")
