import sys
import os
import subprocess
import importlib.resources as res
import runpy

from RUDLeg.core_magic.CodeTemplateAndFunction import *
from RUDLeg.johnson import Joshua



build_path = res.files("RUDLeg.core_magic").joinpath("build.json")
build = Joshua(str(build_path))
build_data = build.read_data()





def task_run(arguments):
        

    if len(arguments) < 2:
        sys.stdout.write("\033[31mUse the commmand: help\033[0m")
            
    else:
        command = arguments[1]

        #Create config line
        if command == "help":
            sys.stdout.write(
            "\033[33m" 
            "Defined commands are here:\n"
            "\n"
            "Log and flags:\n"
            "\n"
            "\ton-debug : change flag 'debug' to ON\n"
            "\toff-debug : change flag 'debug' to OFF\n"
            "\tlog-flags : show all flags\n"
            "\n"
            "Execute and help commands:\n"
            "\trun : runs program...\n"
            "\tbuild : the command for build and prepare for running...\n"
            "\trun-build : build and execute program...\n"
            "\n"
            "Create config and files commands:\n"
            "\tcreate <dir_name> : creates a config templates with usefull files.\n"
            "\tcreate-tcpu <filename> : creates a test file pygame working on CPU.\n"
            "\tcreate-tgpu <filename> : creates a test file pygame + moderngl.\n"
            "\n"
            "Special and Information commands:\n"
            "\tversion : returns version of that Engine.\n"
            "\tshow : returns all information about that framework.\n"
            "\tnews : shows news about that Engine.\n"
            "\tcommunity : returns discord url\n"
            "\033[0m"
            )
            sys.exit(0)
            


        elif command == "re-load":
            if len(arguments) < 3:
                sys.stderr.write("\033[31mYou must have written dir_name\033[0m")
                sys.exit(1)

            
            dir_name = arguments[2]
            if not os.path.isdir(dir_name):
                sys.stderr.write("\033[31mUndefined config. Please write exists dirs\033[0m")
                sys.exit(1)

            inverter_file = "TheMainGame.py"
            file_path = res.files("RUDLeg.core_magic").joinpath(inverter_file)
            with open(file_path, "r", encoding="UTF-8") as f:
                code_writer = f.read()

            
            if "RGAME" in code_writer:
                code_writer = code_writer.replace("RGAME", f"{dir_name}")

            
            if "RSET" in code_writer:
                code_writer = code_writer.replace(
                    "RSET",
                    f"os.path.join('{dir_name}', 'data', 'YourData.json')"
                )

            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_writer)
            sys.stdout.write(f"\033[32mYour config: {dir_name} succesfully reloaded.\033[0m")
            sys.exit(0)



        elif command == "create":
            #if you forgot write dir_name in < py helper.py create ... >
            if len(arguments) < 3:
                sys.stderr.write("\033[31mYou must have written dir_name\033[0m")
                sys.exit(1)

            #Creates directory in your project
            dir_name = arguments[2]
            dirs_config_name = ["shaders", "objects", "classes", "stuff", "data", "scenes", "assets", "soundmusic"]
            main_file = "SceneManager.py"

            inverter_file = "TheMainGame.py"
            file_dirs = (("Example.vert", "shaders"), ("Example.frag", "shaders"), ("YourData.json", "data"), ("ExampleScene1.py", "scenes", 1), ("ExampleScene2.py", "scenes", 2))
            os.makedirs(dir_name, exist_ok=True)

            #Create dirs
            for dir_config_name in dirs_config_name:
                path = os.path.join(dir_name, dir_config_name)
                os.makedirs(path, exist_ok=True)

            path_main = os.path.join(dir_name, main_file)
            with open(path_main, "w", encoding="UTF-8") as f:
                f.write(scene_code(dir_name=dir_name))


            for file_dir in file_dirs:
                #if that is shader
                if file_dir[1] == "shaders":
                    shader_path = os.path.join(dir_name, "shaders", file_dir[0])
                    with open(shader_path, "w", encoding="UTF-8") as f:
                        if os.path.splitext(shader_path)[1] == ".vert":
                            f.write(example_vert)
                        elif os.path.splitext(shader_path)[1] == ".frag":
                            f.write(example_frag)

                #if that is scene
                elif file_dir[1] == "scenes":
                    scene_path = os.path.join(dir_name, "scenes", file_dir[0])
                    with open(scene_path, "w", encoding="UTF-8") as f:
                        if file_dir[2] == 1:
                            f.write(example_code_1)
                        elif file_dir[2] == 2:
                            f.write(example_code_2)

                #if that is data
                elif file_dir[1] == "data":
                    data_path = os.path.join(dir_name, "data", file_dir[0])
                    with open(data_path, "w", encoding="UTF-8") as f:
                        f.write(example_data)
            

            file_path = res.files("RUDLeg.core_magic").joinpath(inverter_file)
            with open(file_path, "r", encoding="UTF-8") as f:
                code_writer = f.read()

            
            if "RGAME" in code_writer:
                code_writer = code_writer.replace("RGAME", f"{dir_name}")

            
            if "RSET" in code_writer:
                code_writer = code_writer.replace(
                    "RSET",
                    f"os.path.join('{dir_name}', 'data', 'YourData.json')"
                )

            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_writer)

            
            sys.stdout.write(f"\033[32mYour config: {dir_name} succesfully created.\033[0m")
            sys.exit(0)



        elif command in ["create-tcpu", "create-tgpu"]:
            if len(arguments) < 3:
                sys.stderr.write("\033[31mYour forgot write a filename.\033[0m")
                sys.exit(1)

            if command == "create-tcpu":
                test_cpu = arguments[2]
                with open(f"{test_cpu}.py", "w", encoding="UTF-8") as f:
                    f.write(test_code_cpu)
                    sys.stdout.write(f"\033[32mYour file {test_cpu}.py succesfully created.\033[0m")
                    sys.exit(0)

            elif command == "create-tgpu":
                test_gpu = arguments[2]
                with open(f"{test_gpu}.py", "w", encoding="UTF-8") as f:
                    f.write(test_code_gpu)
                    sys.stdout.write(f"\033[32mYour file {test_gpu}.py succesfully created.\033[0m")
                    sys.exit(0)

            sys.exit(0)


            

        elif command in ["create-rd", "create-txt"]:
            if len(arguments) < 3:
                sys.stderr.write("\033[31mYour forgot write a filename.\033[0m")
                sys.exit(1)

            
            if command == "create-rd":
                readme_name = arguments[2]
                with open(f"{readme_name}.md", "w", encoding="UTF-8") as f:
                    sys.stdout.write(f"\033[32mYour file README was created.\033[0m")

            elif command == "create-txt":
                txt_name = arguments[2]
                with open(f"{txt_name}.txt", "w", encoding="UTF-8") as f:
                    sys.stdout.write(f"\033[32mYour file TXT was created.\033[0m")
            sys.exit(0)

                

        #Special line
        elif command == "news":
            sys.stdout.write(f"\033[32mMy first Game Engine: RUDLeg 0.1.0.0 was released!!!\033[0m")
            sys.exit(0)


        elif command == "version":
            sys.stdout.write("\033[32mRUDLeg - 0.1.4.5\033[0m")
            sys.exit(0)

        elif command == "show":
            sys.stdout.write("\033[32mRUDLeg:\n" \
            "version: 0.1.0.0\n" \
            "author: TheDreadMatrix\n" \
            "backend: pygame+moderngl\n" \
            "description: I creates my first ever GameEngine and i m happy!!!\033[0m")
            sys.exit(0)

        elif command == "community":
            sys.stdout.write("\033[32mMy discord server: https://discord.gg/wCex59HJKP\033[0m")
            sys.exit(0)

        elif command == "hello":
            sys.stdout.write("\033[31mRSTAKAPZTV#N\033[0m")
            sys.exit(1)

        


        #Options and information
        elif command == "on-debug":
            if build_data["debug"]:
                sys.stderr.write("\033[33mNothing to do...\033[0m")
                sys.exit(1)
            else:
                build_data["debug"] = True
                build.save_data(build_data)
                sys.stdout.write("\033[32mYou succesfully changed flag debug to ON.\033[0m")

        elif command == "off-debug":
            if not build_data["debug"]:
                sys.stderr.write("\033[33mNothing to do\033[0m")
                sys.exit(1)
            else:
                build_data["debug"] = False
                build.save_data(build_data)
                sys.stdout.write("\033[32mYou succesfully changed flag debug to OFF.\033[0m")


        elif command == "log-flags":
            sys.stdout.write("\033[33mAll flags to write a log\n\033[0m")
            for key, item in build_data.items():
                if key != "build":
                    sys.stdout.write(f"\033[33m{key} - {item}\n\033[0m")
            sys.exit(0)
        


        #Execute command
        elif command == "run":
            if build_data["build"]:
                build_data["build"] = False
                build.save_data(build_data)
  

                if build_data["debug"]:
                      with res.as_file(res.files("RUDLeg.core_magic").joinpath("DebugManager.py")) as debug_file_path:
                        subprocess.Popen([sys.executable, str(debug_file_path)])

                    
                try:
                    from RUDLeg.core_magic.TheMainGame import MyGame
                    MyGame().run()
                except ModuleNotFoundError:
                    sys.stderr.write("\033[31mYou should create project at first.\033[0m]")
                    sys.exit(0)
            else:
                sys.stderr.write("\033[31mYou need to build that config: build or use build-run\033[0m")
                sys.exit(1)

        elif command == "build":
            if len(arguments) < 3:
                sys.stderr.write("\033[31mI expected a dir_name\033[0m")
                sys.exit(1)


            dir_name = arguments[2]
            if not os.path.isdir(dir_name):
                sys.stderr.write("\033[31mUndefined config. Please write exists dirs\033[0m")
                sys.exit(1)


            locate_danger(dir_name=dir_name)

            if not build_data["build"]:
                build_data["build"] = True
                build.save_data(build_data)
                sys.stdout.write("\033[32mYour have built succesfully.\033[0m")
                sys.exit(0)
            else:
                sys.stdout.write("\033[33mYour have built your config again...\033[0m")
                sys.exit(1)



        elif command in ["build-run", "call", "rub"]:
            if len(arguments) < 3:
                sys.stderr.write("\033[31mI expected a dir_name\033[0m")
                sys.exit(1)
            
            dir_name = arguments[2]
            if not os.path.isdir(dir_name):
                sys.stderr.write("\033[31mUndefined config. Please write exists dirs\033[0m")
                sys.exit(1)


            locate_danger(dir_name=dir_name)


            build_data["build"] = False
            build.save_data(build_data)

            if build_data["debug"]:
                with res.as_file(res.files("RUDLeg.core_magic").joinpath("DebugManager.py")) as debug_file_path:
                        subprocess.Popen([sys.executable, str(debug_file_path)])

            try:
                from RUDLeg.core_magic.TheMainGame import MyGame
                MyGame().run()
            except ModuleNotFoundError:
                    sys.stderr.write("\033[31mYou should create project at first.\033[0m")
                    sys.exit(0)



        else:
            sys.stderr.write(f"\033[31mUndefined command as : {command}\033[0m")
            sys.exit(1)


