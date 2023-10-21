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
	case "HGET":
		if len(command.Args) != 2 {
			return errors.New("HGET command requires 2 arguments")
		}
		resp = handleHGET(command.Args[0], command.Args[1])
	case "HINCRBY":
		if len(command.Args) != 3 {
			return errors.New("HINCRBY command requires 3 arguments")
		}
		resp = handleHINCRBY(command.Args[0], command.Args[1], command.Args[2])
	case "HGETALL":
		if len(command.Args) != 1 {
			return errors.New("HGETALL command requires 1 argument")
		}
		resp = handleHGETALL(command.Args[0])
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

func handleHGET(key string, field string) []byte {
	obj := Get(key)
	if obj == nil {
		return []byte("Key not found")
	} else if obj.Type != OBJ_TYPE_HASH_INT {
		return []byte("Key is not an int hash")
	}
	hset := obj.Val.(HsetInt)
	return []byte(hset.Get(field))
}

func handleHINCRBY(key string, field string, incr string) []byte {
	obj := Get(key)
	var hset HsetInt
	if obj == nil {
		// Create a new hash
		hset = make(HsetInt)
	} else if obj.Type != OBJ_TYPE_HASH_INT {
		return []byte("Key is not an int hash")
	} else {
		hset = obj.Val.(HsetInt)
	}
	hset.Incrby(field, incr)
	if obj == nil {
		// Create a new key if it doesn't exist
		Set(key, NewObject(hset, OBJ_TYPE_HASH_INT))
	}
	return OK
}

func handleHGETALL(key string) []byte {
	obj := Get(key)
	if obj == nil {
		return []byte("Key not found")
	} else if obj.Type != OBJ_TYPE_HASH_INT {
		return []byte("Key is not an int hash")
	}
	hset := obj.Val.(HsetInt)
	return hset.GetAll()
}
