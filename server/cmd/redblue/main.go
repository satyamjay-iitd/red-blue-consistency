package main

import (
	"fmt"
	"os"
	"redblue/internal/server"
	"strconv"
)

func main() {
	switch numArgs := len(os.Args); numArgs {
	case 1:
		err := server.StartTcpServer(false, 7379, "", "")
		panic(err)
	case 2:
		port, _ := strconv.Atoi(os.Args[1])
		err := server.StartTcpServer(false, port, "", "")
		panic(err)
	case 5:
		slaveHost1 := os.Args[1]
		slavePort1, err := strconv.Atoi(os.Args[2])
		slaveHost2 := os.Args[3]
		slavePort2, err := strconv.Atoi(os.Args[4])
		if err != nil {
			panic("Invalid arguments")
		}
		err = server.StartTcpServer(
			true,
			7379,
			fmt.Sprintf("%s:%d", slaveHost1, slavePort1),
			fmt.Sprintf("%s:%d", slaveHost2, slavePort2),
		)
	default:
		panic("Invalid number of arguments")
	}
}
