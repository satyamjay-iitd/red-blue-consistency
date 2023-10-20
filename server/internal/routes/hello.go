package routes

import (
	"fmt"
	"net/http"
)

func HelloRoute(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Hello, World!")
}
