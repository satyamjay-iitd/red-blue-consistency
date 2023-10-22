package core

import (
	"errors"
	"io"
	"log"
	"strconv"
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
	case "DEP":
		if len(command.Args) != 1 {
			return errors.New("DEP command requires 1 argument")
		}
		resp = handleDEP(command.Args[0])
	case "AI":
		if len(command.Args) != 1 {
			return errors.New("AI command requires 1 argument")
		}
		resp = handleAI(command.Args[0])
	case "WIT":
		if len(command.Args) != 1 {
			return errors.New("WIT command requires 2 arguments")
		}
		resp = handleWIT(command.Args[0])
	case "BAL":
		if len(command.Args) != 0 {
			return errors.New("BAL command requires 0 arguments")
		}
		resp = handleBAL()
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

func handleDEP(amt string) []byte {
	amtI, err := strconv.Atoi(amt)
	if err != nil {
		log.Println(err)
	}
	bank += float64(amtI)
	return OK
}

func handleWIT(amt string) []byte {
	amtI, err := strconv.Atoi(amt)
	if err != nil {
		log.Println(err)
	}
	amtF := float64(amtI)
	if bank < amtF {
		return withdrawFail()
	}
	return withdrawAck(amtF)
}

func withdrawAck(amt float64) []byte {
	// TODO: Implement Synchronization
	bank -= amt
	return OK
}

func withdrawFail() []byte {
	return []byte("Withdrawing more than Balance")
}

func handleAI(rate string) []byte {
	rateI, err := strconv.Atoi(rate)
	if err != nil {
		return []byte("Interest rate must be an int")
	}
	if rateI < 0 || rateI > 100 {
		return []byte("Interest rate must be between 0 and 100")
	}
	bank += float64(rateI) / 100.0

	return OK
}

func handleBAL() []byte {
	return []byte(strconv.FormatFloat(bank, 'f', -1, 64))
}
