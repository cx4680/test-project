package main

import "my-test/internal/router"

func main() {
	r := router.Setup()
	r.Run(":8080")
}
