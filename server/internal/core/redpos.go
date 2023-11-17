package core

import (
	"errors"
	"net"
	"sync"
)

func startRedOps(conn *net.TCPConn, wg *sync.WaitGroup) error {
	_, err := conn.Write([]byte("START_REDOP"))
	if err != nil {
		wg.Done()
		return err
	}

	reply := make([]byte, 1024)
	n, err := conn.Read(reply)
	if err != nil {
		wg.Done()
		return err
	}

	if string(reply[:n-1]) != OK_STRING {
		wg.Done()
		return errors.New("invalid response from slave")
	}

	wg.Done()
	return nil
}

func endRedOps(conn *net.TCPConn, wg *sync.WaitGroup) error {
	_, err := conn.Write([]byte("END_REDOP"))
	if err != nil {
		wg.Done()
		return err
	}

	reply := make([]byte, 1024)
	n, err := conn.Read(reply)
	if err != nil {
		wg.Done()
		return err
	}

	if string(reply[:n-1]) != OK_STRING {
		wg.Done()
		return errors.New("invalid response from slave")
	}

	wg.Done()
	return nil
}

func startRedOpsAll(conn1 *net.TCPConn, conn2 *net.TCPConn) error {
	var wg sync.WaitGroup

	// err := startRedOps(conn1)
	// if err != nil {
	// 	return err
	// }

	// err = startRedOps(conn2)
	// if err != nil {
	// 	endRedOps(conn1)
	// 	return err
	// }
	wg.Add(2)
	go startRedOps(conn1, &wg)
	go startRedOps(conn2, &wg)

	wg.Wait()

	return nil
}

func endRedOpsAll(conn1 *net.TCPConn, conn2 *net.TCPConn) error {
	var wg sync.WaitGroup

	// err := endRedOps(conn1)
	// if err != nil {
	// 	return err
	// }

	// err = endRedOps(conn2)
	// if err != nil {
	// 	return err
	// }

	wg.Add(2)
	go endRedOps(conn1, &wg)
	go endRedOps(conn2, &wg)

	wg.Wait()

	return nil
}
