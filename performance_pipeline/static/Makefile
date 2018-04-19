.PHONY: all main clean lint lessc

all: clean lessc lint main

clean:

install:
	npm i


main: install
	webpack


lint:
	jshint --verbose src/*.js


lessc:
	lessc src/style.less css/style.css



