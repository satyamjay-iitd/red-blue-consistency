package tests

import (
	"net"
	"testing"
)

func TestSetCmd(t *testing.T) {
	conn, _ := net.Dial("tcp", "127.0.0.1:8000")
	conn.Close()
	//fmt.Fprintf(conn, "SET k1 v1\n")
	//response, _ := bufio.NewReader(conn).ReadString('\n')
	//if response == "" {
	//	t.Errorf("Bad server response")
	//}

}
