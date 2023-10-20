package core

import (
	"encoding/json"
	"log"
	"strconv"
)

type HsetInt map[string]int

type HsetFloat map[string]float64

func (h HsetInt) Incrby(key string, incr string) {
	// Convert incr to int
	val, err := strconv.Atoi(incr)
	if err != nil {
		log.Println(err)
		return
	}
	// Default is 0 if the value is not present
	h[key] += val
}

func (h HsetInt) Get(key string) string {
	if val, ok := h[key]; ok {
		return strconv.Itoa(val)
	} else {
		// Should we return a proper error in error cases?
		log.Printf("Key %s not found in HsetInt", key)
		return ""
	}
}

func (h HsetInt) GetAll() []byte {
	// var resp []byte
	// for key, val := range h {
	// 	resp = append(resp, []byte(key)...)
	// 	resp = append(resp, []byte(":")...)
	// 	resp = append(resp, []byte(strconv.Itoa(val))...)
	// 	resp = append(resp, []byte("\n")...)
	// }
	// return resp
	resp, err := json.Marshal(h)
	if err != nil {
		log.Println(err)
		return []byte("Error")
	}
	return resp
}
