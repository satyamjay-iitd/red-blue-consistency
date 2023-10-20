package core

import (
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
		return ""
	}
}
