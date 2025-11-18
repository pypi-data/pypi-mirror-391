import pygame as pg
import socket as sock
import moderngl as mgl
import glm
import os, sys
import json
import importlib.resources as res


from RUDLeg.johnson import Joshua

from RGAME.SceneManager import SceneManager




HOST_DEBUG = "127.0.0.1"
PORT_DEBUG = 5050



SV = "0.1.0.0"


class MyGame:
	screen: pg.Surface
	delta_time: float


	def __init__(self):
		pg.init()
		build_path = res.files("RUDLeg.core_magic").joinpath("build.json")
		self.__build = Joshua(str(build_path))
		self.__build_data = self.__build.read_data()

		self.data = Joshua(path=RSET)
		self.data_read = self.data.read_data()

		#debug-client connection
		if self.__build_data.get("debug"):
			try:
				self.__debug_client = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
				self.__debug_client.connect((HOST_DEBUG, PORT_DEBUG))
				self.__debug_dict = {"run": True}
			except ConnectionRefusedError:
				pass



		#Window Manager
		pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
		pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
		pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
		pg.display.gl_set_attribute(pg.GL_MULTISAMPLEBUFFERS, 1)
		pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, 4)
		self.__screen = pg.display.set_mode(self.data_read["window-size"], flags=pg.DOUBLEBUF|pg.OPENGL|pg.RESIZABLE)


		#GPU context
		self.ctx = mgl.create_context()
		self.ctx.enable(mgl.BLEND)
		self.ctx.gc_mode = 'auto'
		self.ctx.line_width = 3.0
		self.ctx.point_size = 10.0
		self.ctx.viewport = (0, 0, self.__screen.get_width(), self.__screen.get_height())


		self.verticles_2d = glm.array(glm.float32,
			0.0, 0.0, 0.0, 1.0,
			1.0, 0.0, 1.0, 1.0,
			1.0, 1.0, 1.0, 0.0,
			0.0, 1.0, 0.0, 0.0
		)

		self.indices = glm.array(glm.uint32, 0, 1, 2, 2, 3, 0)

		#Attributes
		self.__is_run = True
		self.clock = pg.time.Clock()
		self.delta_time = 0


		pg.display.set_caption(f"The RudlEngine: {SV}", f"The RudlEngine: {SV}")
		icon_path = res.files("RUDLeg.stuff.stuff").joinpath("icon.png")
		pg.display.set_icon(pg.image.load(str(icon_path)))
		self.init_on()

	def init_on(self):
		try:
			self.scene = SceneManager(self)
		except Exception as error:
			if self.__build_data["debug"]:
				pg.display.message_box("Look! Its an error!", f"{error} in that scene: {self.get_scene} from init")
			sys.exit(1)



	def close_game(self):
		self.__is_run = False


	def switch_scene(self, scene_name_anotation: str):
		self.data_read["game-state"] = scene_name_anotation



	def change_data(self, key_d, value_d):
		if key_d in self.data_read:
			self.data_read[key_d] = value_d



	def debug_sendall(self, dict_debug):
		try:
			self.__debug_dict.update(dict_debug)

			json_data = json.dumps(self.__debug_dict).encode("utf-8") + b"\n"
			try:
				self.__debug_client.sendall(json_data)
			except (ConnectionResetError, BrokenPipeError):
				pass

		except AttributeError:
			pass




	@property
	def get_scene(self): return self.data_read["game-state"]
	
	@property
	def width(self): return self.__screen.get_width()

	@property
	def height(self): return self.__screen.get_height()

			
			

	def handler_update(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.close_game()
			if event.type == pg.VIDEORESIZE:
				width, height = event.size
				self.ctx.viewport = (0, 0, width, height)
			self.scene.handler_event(event=event)
		self.scene.update()


	def render(self):
		self.ctx.clear(0.9, 0.9, 0.9) 
		self.scene.render()
		pg.display.flip()


	def run(self):
		while self.__is_run:
			self.delta_time = min(self.clock.tick(self.data_read["fps"]) / 1000.0, 0.05)
			self.debug_sendall({"fps": int(self.clock.get_fps())})

			try:
				self.handler_update()
				self.render()
			except Exception as error:
				if self.__build_data["debug"]:
					pg.display.message_box("Look! Its an error!", f"{error} in that scene: {self.get_scene} from update")
				sys.exit(1)
				


			
		if self.data_read["need-to-save"]:
			self.data.save_data(self.data_read)


		try:
			self.__debug_client.close()
		except AttributeError:
			pass


		pg.quit()
		sys.exit(0)

