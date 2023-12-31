package server

import "syscall"

type Socket struct {
	Fd int
}

func (s Socket) Write(b []byte) (int, error) {
	return syscall.Write(s.Fd, append(b, '\n'))
}

func (s Socket) Read(b []byte) (int, error) {
	return syscall.Read(s.Fd, b)
}
