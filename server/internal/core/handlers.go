package core

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"strconv"
	"strings"
)

const OK_STRING = "OK"

var OK = []byte(OK_STRING)

func HandleCommands(
	c io.ReadWriter, command *Command, isMaster bool, slaveConn1, slaveConn2 *net.TCPConn,
) error {
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
		resp = handleHGETALL(command.Args[0], isMaster, slaveConn1, slaveConn2)
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
		resp = handleWIT(command.Args[0], isMaster, slaveConn1, slaveConn2)
	case "BAL":
		if len(command.Args) != 0 {
			return errors.New("BAL command requires 0 arguments")
		}
		resp = handleBAL(isMaster, slaveConn1, slaveConn2)
	case "SETADD":
		if len(command.Args) != 1 {
			return errors.New("SETADD command requires 1 argument")
		}
		resp = handleSETADD(command.Args[0])
	case "SETREM":
		if len(command.Args) != 1 {
			return errors.New("SETREM command requires 1 argument")
		}
		resp = handleSETREM(command.Args[0])
	case "SETREAD":
		if len(command.Args) != 0 {
			return errors.New("SETREM command requires 0 argument")
		}
		resp = handleSETREAD()
	default:
		return errors.New("unknown command")
	}
	_, err := c.Write(resp)
	return err
}

func handleSET(key string, val string) []byte {
	Set(key, NewObject(val, nil, OBJ_TYPE_STRING))
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
		Set(key, NewObject(hset, make(HsetInt), OBJ_TYPE_HASH_INT))
	}
	return OK
}

func handleHGETALL(key string, isMaster bool, conn1 *net.TCPConn, conn2 *net.TCPConn) []byte {
	// This is a RED operation.. hence we need to sync first
	if !isMaster {
		return []byte("Can only get from Master")
	}

	err := startRedOpsAll(conn1, conn2)
	if err != nil {
		return []byte("Error syncing")
	}

	obj := Get(key)
	if obj == nil {
		// key might have been created in a different server
		obj = NewObject(make(HsetInt), make(HsetInt), OBJ_TYPE_HASH_INT)
		// return []byte("Key not found")
	} else if obj.Type != OBJ_TYPE_HASH_INT {
		return []byte("Key is not an int hash")
	}
	hset := obj.Val.(HsetInt)
	lastHset := obj.LastSyncedVal.(HsetInt)

	// Get the data from the slaves
	_, err = conn1.Write([]byte(fmt.Sprintf("SYNC_HGETALL %s", key)))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}
	_, err = conn2.Write([]byte(fmt.Sprintf("SYNC_HGETALL %s", key)))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	data1, err := readCompleteData(conn1)
	if err != nil {
		log.Println(err)
	}
	data2, err := readCompleteData(conn2)
	if err != nil {
		log.Println(err)
	}

	var hset1 HsetInt
	var hset2 HsetInt
	err = json.Unmarshal(data1, &hset1)
	if err != nil {
		log.Println(err)
	}
	err = json.Unmarshal(data2, &hset2)
	if err != nil {
		log.Println(err)
	}

	// Merge the data
	for k, v := range hset1 {
		hset[k] += (v - lastHset[k])
	}
	for k, v := range hset2 {
		hset[k] += (v - lastHset[k])
	}

	// Update the last synced value
	// deep copy the hset
	for k, v := range hset {
		lastHset[k] = v
	}
	Set(key, NewObject(hset, lastHset, OBJ_TYPE_HASH_INT))

	// write the data to the slaves
	_, err = conn1.Write([]byte(fmt.Sprintf("SYNC_HSETALL %s", key)))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}
	_, err = conn2.Write([]byte(fmt.Sprintf("SYNC_HSETALL %s", key)))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	// read and discard OK response
	reply := make([]byte, 1024)
	conn1.Read(reply)
	conn2.Read(reply)

	// Send the data
	response := hset.GetAll()
	_, err = conn1.Write(response)
	if err != nil {
		println("Write to slave failed:", err.Error())
	}
	_, err = conn2.Write(response)
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	// read and discard OK response
	conn1.Read(reply)
	conn2.Read(reply)

	// End RED operation
	err = endRedOpsAll(conn1, conn2)
	if err != nil {
		return []byte("Error syncing cleanup")
	}
	return response
}

func handleDEP(amt string) []byte {
	amtI, err := strconv.Atoi(amt)
	if err != nil {
		log.Println(err)
	}
	bank += float64(amtI)
	return OK
}

func handleAI(rate string) []byte {
	rateI, err := strconv.Atoi(rate)
	if err != nil {
		return []byte("Interest rate must be an int")
	}
	if rateI < 0 || rateI > 10000 {
		return []byte("Interest rate must be between 0 and 10000")
	}
	bank += bank * (float64(rateI) / 10000.0)

	return OK
}

func handleWIT(amt string, isMaster bool, conn1 *net.TCPConn, conn2 *net.TCPConn) []byte {
	if !isMaster {
		return []byte("Can only withdraw from Master")
	}

	// Parse input
	amtI, err := strconv.Atoi(amt)
	if err != nil {
		log.Println(err)
		return []byte("Invalid Amount format")
	}
	amtF := float64(amtI)

	// /////////////////////////// Get values from other servers \\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	_, err = conn1.Write([]byte("SYNC_BANK_READ"))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	_, err = conn2.Write([]byte("SYNC_BANK_READ"))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	reply := make([]byte, 1024)
	n, err := conn1.Read(reply)
	if err != nil {
		println("Read from slave failed:", err.Error())
	}
	val1, err := strconv.ParseFloat(string(reply[:n-1]), 64)
	if err != nil {
		println("Invalid response from slave", err.Error(), string(reply[:n-1]))
	}

	n, err = conn2.Read(reply)
	if err != nil {
		println("Read from slave failed:", err.Error())
	}
	val2, err := strconv.ParseFloat(string(reply[:n-1]), 64)
	if err != nil {
		println("Invalid response from slave", err.Error(), string(reply[:n-1]))
	}

	// //////////////////////////////////// Update local balance \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	bank += val1 + val2 - 2*prevBank

	withdrawSuccess := false
	if bank >= amtF {
		bank -= amtF
		withdrawSuccess = true
	}

	// //////////////////////////////////// Update remote balance \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	_, err = conn1.Write([]byte(fmt.Sprintf("SYNC_BANK_WRITE %s", strconv.FormatFloat(bank, 'f', -1, 64))))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	_, err = conn2.Write([]byte(fmt.Sprintf("SYNC_BANK_WRITE %s", strconv.FormatFloat(bank, 'f', -1, 64))))
	if err != nil {
		println("Write to slave failed:", err.Error())
	}

	_, err = conn1.Read(reply)
	_, err = conn2.Read(reply)

	prevBank = bank
	if withdrawSuccess {
		return OK
	}
	return []byte("Insufficient Balance")
}

func handleBAL(isMaster bool, conn1, conn2 *net.TCPConn) []byte {
	handleWIT("0", isMaster, conn1, conn2) // Shortcut For synchronization
	return []byte(strconv.FormatFloat(bank, 'f', -1, 64))
}

func handleSETADD(item string) []byte {
	set[item] = struct{}{}
	return OK
}

func handleSETREM(item string) []byte {
	// TODO: Synchronize
	delete(set, item)
	return OK
}

func handleSETREAD() []byte {
	keys := make([]string, len(set))

	i := 0
	for k := range set {
		keys[i] = k
		i++
	}

	return []byte(strings.Join(keys, " "))
}
