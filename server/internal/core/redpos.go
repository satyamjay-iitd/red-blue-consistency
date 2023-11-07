package core

import (
	"errors"
	"net"
)

func startRedOps(conn *net.TCPConn) error {
	_, err := conn.Write([]byte("START_REDOP"))
	if err != nil {
		return err
	}

	reply := make([]byte, 1024)
	n, err := conn.Read(reply)
	if err != nil {
		return err
	}

	if string(reply[:n-1]) != OK_STRING {
		return errors.New("invalid response from slave")
	}

	return nil
}

func endRedOps(conn *net.TCPConn) error {
	_, err := conn.Write([]byte("END_REDOP"))
	if err != nil {
		return err
	}

	reply := make([]byte, 1024)
	n, err := conn.Read(reply)
	if err != nil {
		return err
	}

	if string(reply[:n-1]) != OK_STRING {
		return errors.New("invalid response from slave")
	}

	return nil
}

func startRedOpsAll(conn1 *net.TCPConn, conn2 *net.TCPConn) error {
	err := startRedOps(conn1)
	if err != nil {
		return err
	}

	err = startRedOps(conn2)
	if err != nil {
		endRedOps(conn1)
		return err
	}

	return nil
}

func endRedOpsAll(conn1 *net.TCPConn, conn2 *net.TCPConn) error {
	err := endRedOps(conn1)
	if err != nil {
		return err
	}

	err = endRedOps(conn2)
	if err != nil {
		return err
	}

	return nil
}
