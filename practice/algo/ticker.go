package algo

import (
	"fmt"
	"time"
)

func TickerTest() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		var a int32 = 10
		fmt.Println(int(a))
	}
}
