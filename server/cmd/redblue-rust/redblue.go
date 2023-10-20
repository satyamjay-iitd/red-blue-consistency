package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"redblue/internal/routes"

	"github.com/gorilla/mux"
)

type Config struct {
	Port string `json:"port"`
}

func configureRoutes(r *mux.Router) {
	r.HandleFunc("/", routes.HelloRoute)
}

func main() {
	// Open the configuration file
	file, err := os.Open("conf/config.json")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	// Decode the configuration file
	decoder := json.NewDecoder(file)
	config := Config{}
	err = decoder.Decode(&config)
	if err != nil {
		log.Fatal(err)
	}

	// Create the router
	r := mux.NewRouter()

	// Configure the routes
	configureRoutes(r)

	// Start the server
	log.Fatal(http.ListenAndServe(":"+config.Port, r))
}
