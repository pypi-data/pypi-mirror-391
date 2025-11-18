import sys, os
import pygame as pg
import socket as sock
import json

pg.init()
screen = pg.display.set_mode((600, 350), flags=pg.RESIZABLE)
pg.display.set_caption("RudlEngine: Debug Mode")

BLACK = (0, 0, 0)
HOST_DEBUG = "127.0.0.1"
PORT_DEBUG = 5050


font = pg.font.Font(None, 36)

server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
server.bind((HOST_DEBUG, PORT_DEBUG))
server.listen(1)

server.settimeout(2.5)

try:
    conn, addr = server.accept()
except sock.timeout:
    pg.display.message_box("Sorry! But you need to create config")
    sys.exit(1)


run = True
clock = pg.time.Clock()
buffer = ""
counter = 0

while run:
    screen.fill(BLACK)
    clock.tick(60)

    try:
        data = conn.recv(1024)
        if not data:
            break

        buffer += data.decode("utf-8")

        while "\n" in buffer:
            json_str, buffer = buffer.split("\n", 1)
            if not json_str.strip():
                continue
            try:
                json_data = json.loads(json_str)
                x = screen.get_width() * 0.2
                y = 20
                offset_y = 25

                for i, (key, value) in enumerate(json_data.items()):
                    text_surface = font.render(f"{key}: {value}", True, (255, 255, 255))
                    screen.blit(text_surface, (x, y + i * offset_y))
            except json.JSONDecodeError as e:
                pass

    except ConnectionResetError:
        conn.close()
        conn, addr = server.accept()
        buffer = ""

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            run = False

        

    pg.display.flip()

pg.quit()
conn.close()
server.close()
sys.exit(0)
