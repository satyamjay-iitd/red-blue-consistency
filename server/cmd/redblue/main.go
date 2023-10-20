package main

import (
	"log"
	"redblue/internal/server"
)

func main() {
	log.Println("Starting the RedBlue server...")
	server.StartTcpServer()
}
