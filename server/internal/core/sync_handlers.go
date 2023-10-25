package core

import (
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
	default:
		return errors.New("unknown command")
	}
	_, err := c.Write(resp)
	return err
}

func handleSyncBankRead(isMaster bool) (resp []byte) {
	if isMaster {
		resp = []byte("Cannot call sync commands on master")
	}
	resp = []byte(strconv.FormatFloat(bank, 'f', -1, 64))

	return
}

func handleSyncBankWrite(isMaster bool, amt string) []byte {
	if isMaster {
		return []byte("Cannot call sync commands on master")
	}
	amtI, err := strconv.Atoi(amt)
	if err != nil {
		log.Println(err)
	}
	bank += float64(amtI)
	return OK
}
