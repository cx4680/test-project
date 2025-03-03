package internal

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func handleInput(rawLine string) []string {
	if len(rawLine) == 0 {
		return []string{}
	}
	var intList []int
	list := strings.Split(rawLine, " ")
	for _, v := range list {
		i, err := strconv.Atoi(v)
		if err != nil {
			return []string{}
		}
		intList = append(intList, i)
	}
	return list
}

func buildSort(strSlice []string) string {
	for i := range strSlice {
		if i >= len(strSlice)-1 {
			break
		}
		if i%2 == 0 && strSlice[i] < strSlice[i+1] {
			strSlice[i], strSlice[i+1] = strSlice[i+1], strSlice[i]
		}
		if i%2 != 0 && strSlice[i] > strSlice[i+1] {
			strSlice[i], strSlice[i+1] = strSlice[i+1], strSlice[i]
		}
	}
	return strings.Join(strSlice, " ")
}

func MainTest2() {
	scanner := bufio.NewScanner(os.Stdin)
	// 持续从标准输入读取多行，直至EOF
	for scanner.Scan() {
		inputLine := scanner.Text()
		inputList := handleInput(inputLine)
		if len(inputList) == 0 {
			fmt.Println("[]")
			continue
		}
		finalPhrase := buildSort(inputList)
		fmt.Println(finalPhrase)
	}
}
