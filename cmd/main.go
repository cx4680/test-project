package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
	//var number int
	//fmt.Print("请输入一个数字: ")
	//_, err := fmt.Scan(&number)
	//if err != nil {
	//	fmt.Println("输入错误:", err)
	//	return
	//}
	//fmt.Printf("您输入的数字是: %d\n", number)

	//arr := []int{3, 2, 1, 4, 5, 3, 2, 1}
	//fmt.Println(arr)
	////bubbleSort(arr)
	////arr = QuickSort(arr)
	//arr = quickSort(arr)
	//fmt.Println("Sorted array: ", arr)

	engine := gin.Default()
	// 路由分组
	v1 := engine.Group("/v1")
	{
		v1.GET("/hello", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "hello world"})
		})
	}
	// 启动服务
	engine.Run(":8080")
}

func bubbleSort(arr []int) {
	n := len(arr)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			if arr[j] > arr[j+1] {
				arr[j], arr[j+1] = arr[j+1], arr[j]
			}
		}
	}
}

func quickSort(arr []int) []int {
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
	left = quickSort(left)
	right = quickSort(right)
	return append(append(left, pivot), right...)
}
