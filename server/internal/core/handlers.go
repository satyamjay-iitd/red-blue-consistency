package core

import (
	"errors"
	"io"
)

const OK_STRING = "OK"

var OK = []byte(OK_STRING)

func HandleCommands(c io.ReadWriter, command *Command) error {
	if command == nil {
		return errors.New("Command is empty")
	}
	var resp []byte
	switch command.Name {
	case "SET":
		if len(command.Args) != 2 {
			return errors.New("SET command requires 2 arguments")
		}
		resp = handleSET(command.Args[0], command.Args[1])
	case "GET":
		if len(command.Args) != 1 {
			return errors.New("GET command requires 1 argument")
		}
		resp = handleGET(command.Args[0])
	default:
		return errors.New("unknown command")
	}
	_, err := c.Write(resp)
	return err
}

func handleSET(key string, val string) []byte {
	Set(key, NewObject(val, OBJ_TYPE_STRING))
	return OK
}

func handleGET(key string) []byte {
	obj := Get(key)
	if obj == nil {
		return []byte("Key not found")
	}
	return []byte(obj.Val.(string))
}
