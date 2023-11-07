package core

import (
	"encoding/json"
	"errors"
	"io"
	"log"
	"strconv"
)

func HandleSyncCommands(
	c io.ReadWriter, command *Command, isMaster bool,
) error {
	if command == nil {
		return errors.New("Command is empty")
	}
	var resp []byte
	switch command.Name {
	case "SYNC_BANK_READ":
		if len(command.Args) != 0 {
			return errors.New("SYNC_BANK_READ command requires 0 arguments")
		}
		resp = handleSyncBankRead(isMaster)
	case "SYNC_BANK_WRITE":
		if len(command.Args) != 1 {
			return errors.New("SYNC_BANK_WRITE command requires 1 arguments")
		}
		resp = handleSyncBankWrite(isMaster, command.Args[0])
	case "SYNC_HGETALL":
		if len(command.Args) != 1 {
			return errors.New("SYNC_HGETALL command requires 1 argument")
		}
		resp = handleSyncHGETALL(command.Args[0])
	case "SYNC_HSETALL":
		if len(command.Args) != 1 {
			return errors.New("SYNC_HSETALL command requires 1 argument")
		}
		resp = handleSyncHSETALL(command.Args[0], c)
	default:
		return errors.New("unknown command")
	}
	_, err := c.Write(resp)
	return err
}

func handleSyncBankRead(isMaster bool) (resp []byte) {
	if isMaster {
		resp = []byte("Cannot call sync commands on master")
	} else {
		resp = []byte(strconv.FormatFloat(bank, 'f', -1, 64))
	}
	return resp
}

func handleSyncBankWrite(isMaster bool, amt string) []byte {
	if isMaster {
		return []byte("Cannot call sync commands on master")
	}
	amtF, err := strconv.ParseFloat(amt, 64)
	if err != nil {
		log.Println(err)
	}
	bank = amtF
	return OK
}

func handleSyncHGETALL(key string) []byte {
	obj := Get(key)
	if obj == nil {
		hset := make(HsetInt)
		return hset.GetAll()
	} else if obj.Type != OBJ_TYPE_HASH_INT {
		return []byte("Key is not an int hash")
	}
	hset := obj.Val.(HsetInt)
	return hset.GetAll()
}

func handleSyncHSETALL(key string, c io.ReadWriter) []byte {
	obj := Get(key)
	// var hset HsetInt
	if obj == nil {
		// Create a new hash
		// hset = make(HsetInt)
	} else if obj.Type != OBJ_TYPE_HASH_INT {
		return []byte("Key is not an int hash")
	} else {
		// hset = obj.Val.(HsetInt)
	}

	// Respond OK
	_, err := c.Write(OK)
	if err != nil {
		log.Println(err)
	}

	// Read the complete data
	data, err := readCompleteData(c)
	if err != nil {
		log.Println(err)
	}

	var newhset HsetInt
	err = json.Unmarshal(data, &newhset)
	if err != nil {
		log.Println(err)
	}

	Set(key, NewObject(newhset, nil, OBJ_TYPE_HASH_INT))
	return OK
}

func readCompleteData(c io.ReadWriter) ([]byte, error) {
	var buf []byte = make([]byte, 1024)
	var data = make([]byte, 0)
	for {
		n, err := c.Read(buf[:])
		if err != nil && err != io.EOF {
			return nil, err
		}
		data = append(data, buf[:n]...)
		if n < 1024 || err == io.EOF {
			break
		}
	}
	return data, nil
}
