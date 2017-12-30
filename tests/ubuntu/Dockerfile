FROM ubuntu:17.10

RUN apt update && apt upgrade && apt install -y -q git scons make build-essential libsdl2-dev gtk+3-dev

RUN git clone https://github.com/xyproto/sakemake
RUN cd sakemake && make install && sm version

RUN sm -C sakemake/example/tinyhello small
RUN sm -C sakemake/example/hello run
RUN sm -C sakemake/example/hello/common test
RUN sm -C sakemake/example/sdl2
RUN sm -C sakemake/example/gtk3
