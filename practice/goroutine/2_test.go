package goroutine

import (
	"fmt"
	"sync"
	"testing"
)

func TestAlternatingPrintAB(t *testing.T) {
	chA := make(chan int)
	chB := make(chan int)
	var wg = &sync.WaitGroup{}
	wg.Add(2)

	go worker(wg, chA, chB)
	go worker(wg, chB, chA)

	chA <- 1

	wg.Wait()
	close(chA)
	close(chB)
}

func worker(wg *sync.WaitGroup, chA, chB chan int) {
	defer wg.Done()
	for {
		num := <-chA
		fmt.Println(num)
		if num >= 10 {
			return
		}
		next := num + 1
		chB <- next
		if next >= 10 {
			return
		}
	}
}
