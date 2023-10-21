package tests

import (
	"bufio"
	"fmt"
	"net"
	"testing"
)

func TestSetCmd(t *testing.T) {
	conn, _ := net.Dial("tcp", "127.0.0.1:7380")
	fmt.Fprintf(conn, "SET k1 v1")
	response, _ := bufio.NewReader(conn).ReadString('\n')
	conn.Close()
	fmt.Println(response)
}
