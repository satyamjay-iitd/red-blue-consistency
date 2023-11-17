package server

import (
	"redblue/internal/core"
)

func processRedOps(s Socket) error {
	//log.Println("Processing redop")

	// Send OK to master
	_, err := s.Write(core.OK)
	if err != nil {
		return err
	}

	// keep reading commands and process them synchronously
	for {
		cmd, err := readCommand(s)
		if err != nil {
			return err
		}
		//log.Println(cmd.Name)

		if cmd.Name == "END_REDOP" {
			_, err = s.Write(core.OK)
			if err != nil {
				return err
			}
			break
		}

		err = respond(s, cmd)
		if err != nil {
			return err
		}
	}

	return nil
}
