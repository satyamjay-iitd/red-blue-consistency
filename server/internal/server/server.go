package server

import (
	"encoding/json"
	"io"
	"log"
	"net"
	"os"
	"syscall"
)

type Config struct {
	Port int `json:"port"`
}

func getConfig() Config {
	file, err := os.Open("conf/config.json")
	if err != nil {
		log.Fatal(err)
		panic(err)
	}
	defer file.Close()

	// Decode the configuration file
	decoder := json.NewDecoder(file)
	config := Config{}
	err = decoder.Decode(&config)
	if err != nil {
		log.Fatal(err)
		panic(err)
	}
	return config
}

func readCommand(c io.ReadWriter) (string, error) {
	var buf []byte = make([]byte, 512) //
	n, err := c.Read(buf[:])
	if err != nil {
		return "", err
	}
	return string(buf[:n]), nil
}

func respond(c io.ReadWriter, response string) error {
	_, err := c.Write([]byte(response))
	return err
}

func StartTcpServer() error {
	log.Println("Starting TCP server...")
	config := getConfig()

	maxClients := 1000

	var events []syscall.EpollEvent = make([]syscall.EpollEvent, maxClients)

	serverFd, err := syscall.Socket(syscall.AF_INET, syscall.O_NONBLOCK|syscall.SOCK_STREAM, 0)
	if err != nil {
		return err
	}

	if err = syscall.SetNonblock(serverFd, true); err != nil {
		return err
	}

	ip := net.ParseIP("0.0.0.0")
	if err = syscall.Bind(serverFd, &syscall.SockaddrInet4{
		Port: config.Port,
		Addr: [4]byte{ip[0], ip[1], ip[2], ip[3]}}); err != nil {
		return err
	}

	if err = syscall.Listen(serverFd, maxClients); err != nil {
		return err
	}

	epollFd, err := syscall.EpollCreate1(0)
	if err != nil {
		log.Fatal(err)
		return err
	}
	defer syscall.Close(epollFd)

	var event syscall.EpollEvent = syscall.EpollEvent{
		Events: syscall.EPOLLIN,
		Fd:     int32(serverFd),
	}

	if err = syscall.EpollCtl(epollFd, syscall.EPOLL_CTL_ADD, serverFd, &event); err != nil {
		log.Fatal(err)
		return err
	}

	for {
		nevents, e := syscall.EpollWait(epollFd, events[:], -1)
		if e != nil {
			continue
		}

		for ev := 0; ev < nevents; ev++ {
			if int(events[ev].Fd) == serverFd {
				fd, _, err := syscall.Accept(serverFd)
				if err != nil {
					log.Println(err)
					continue
				}

				syscall.SetNonblock(serverFd, true) // TODO: check error - should it be fd?

				var event syscall.EpollEvent = syscall.EpollEvent{
					Events: syscall.EPOLLIN,
					Fd:     int32(fd),
				}
				if err = syscall.EpollCtl(epollFd, syscall.EPOLL_CTL_ADD, fd, &event); err != nil {
					log.Fatal(err)
				}
			} else {
				fd := int(events[ev].Fd)
				// log.Println("Got event from fd:", fd)
				s := Socket{Fd: fd}
				cmd, err := readCommand(s)
				if err != nil {
					syscall.Close(fd)
					continue
				}

				err = respond(s, cmd)
				if err != nil {
					log.Println(err)
				}
			}
		}
	}
}