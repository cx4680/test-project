package goroutine

import (
	"fmt"
	"testing"
	"time"
)

func TestRequestWithTimeout(t *testing.T) {
	ch := make(chan string)
	go func() {
		time.Sleep(3 * time.Second)
		ch <- "A支付结果"
	}()

	select {
	case result := <-ch:
		fmt.Println(result, "：支付成功")
	case <-time.After(2 * time.Second):
		fmt.Println("支付超时")
	}
}
