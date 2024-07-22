import pygame, json, time, random, sys

import socket, threading

pygame.init()


class Game:
    def __init__(self):
        self.configs = json.load(open("configs.json", "r"))
        self.tela = pygame.display.set_mode(self.configs['tela-configs']['size'])
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.configs['tela-configs']['caption'])

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 1234))

        threading.Thread(target=self.lenRequests, args=(self.client_socket,)).start()
        playerx = random.randrange(0, int((self.configs['tela-configs']['size'][0] - 200) / self.configs['server-configs']['scale-players'])) * self.configs['server-configs']['scale-players']
        playery = random.randrange(0, int(self.configs['tela-configs']['size'][1] / self.configs['server-configs']['scale-players'])) * self.configs['server-configs']['scale-players']
        self.player = {
            "_id":str(self.client_socket.getsockname()),
            "position":[playerx, playery],
            "score":0,
            "direcao":"parado"
        }
        self.server_infos = {
            "fruit-position":[],
            "other-players":{}
        }

        

    def lenRequests(self, sock):
        while True:
            try:
                message = sock.recv(2048).decode('utf-8')
                if message:
                    
                    try:
                        self.server_infos = json.loads(message)
                        self.player.update(self.server_infos['other-players'][self.player['_id']])
                    except:
                        pass
            except Exception as e:
                print(e)
    
                print("Conexão perdida com o servidor.")
                sock.close()
                break

    def drawPlayer(self):
        # Other Players
        for player in self.server_infos['other-players'].keys():
            if player != self.player['_id']:
                pygame.draw.rect(self.tela, (211, 211, 211), pygame.Rect(self.server_infos['other-players'][player]['position'][0], self.server_infos['other-players'][player]['position'][1], self.configs['server-configs']['scale-players'], self.configs['server-configs']['scale-players']))

        pygame.draw.rect(self.tela, (0, 255, 255), pygame.Rect(self.player['position'][0], self.player['position'][1], self.configs['server-configs']['scale-players'], self.configs['server-configs']['scale-players']))


    def drawScore(self):
        fonte = pygame.font.SysFont('comicsans', 13)
        text = fonte.render(f"Pontos: {self.player['score']}", True, (0, 0, 0))
        self.tela.blit(text, [0, 0])



    def drawFruit(self):
        try:
            pygame.draw.rect(self.tela, (0, 255, 0), pygame.Rect(self.server_infos['fruit-position'][0], self.server_infos['fruit-position'][1], self.configs['server-configs']['scale-players'], self.configs['server-configs']['scale-players']))      
        except IndexError: pass

    def drawRanking(self):
        fonte = pygame.font.SysFont('comicsans', 13)
        text = fonte.render("Ranking:", True, (0, 0, 0))
        pygame.draw.rect(self.tela, (100, 100, 100), pygame.Rect(400, 0, 200, 200))
        self.tela.blit(text, [410, 0])
        ranking = sorted(self.server_infos['other-players'].items(), key=lambda item: item[1]["score"], reverse=True)
        pos = 18
        for i, (name, data) in enumerate(ranking, 1):
            if name == self.player['_id']: cor = (0, 255, 0)
            else: cor = (0, 0, 0)
            text = fonte.render(f"{i}. {name} - {data['score']}", True, cor)
            self.tela.blit(text, [420, pos])
            pos += 18
                
    def run(self):
        while True:
            self.tela.fill('white')
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.client_socket.close()
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.player['direcao'] = 'direita'
                    if event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.player['direcao'] = 'esquerda'
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.player['direcao'] = 'cima'
                    if event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.player['direcao'] = 'baixo'

       
            self.client_socket.send(json.dumps(self.player).encode('utf-8'))
            
            self.drawFruit()
            self.drawPlayer()            
            self.drawScore()
            self.drawRanking()
            
            pygame.display.update()
            self.clock.tick(15)



            
            
Game().run()