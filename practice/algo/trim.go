package algo

import (
	"fmt"
	"strings"
)

func Trim() {
	path := "//path//"
	fmt.Println(path)
	fmt.Println(strings.TrimPrefix(path, "/"))
	fmt.Println(strings.TrimSuffix(path, "/"))
	fmt.Println(strings.TrimLeft(path, "/"))
	fmt.Println(strings.TrimRight(path, "/"))
}
