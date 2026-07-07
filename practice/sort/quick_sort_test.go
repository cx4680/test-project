package sort

import (
	"fmt"
	"testing"
)

func TestQuickSort(t *testing.T) {
	fmt.Println(QuickSort([]int{1, 5, 6, 3, 9, 7, 6, 4, 6, 8, 0}))
}

func QuickSort(arr []int) []int {
	if len(arr) <= 1 {
		return arr
	}
	pivot := arr[0]
	var left, right []int
	for _, v := range arr[1:] {
		if v < pivot {
			left = append(left, v)
		} else {
			right = append(right, v)
		}
	}
	left = QuickSort(left)
	right = QuickSort(right)
	return append(append(left, pivot), right...)
}
