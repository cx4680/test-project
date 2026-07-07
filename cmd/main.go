package main

import (
	"test-project/internal/router"
)

func main() {
	r := router.Setup()
	r.Run(":8080")
}
