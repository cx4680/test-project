package algo

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

// acquireSegments 将输入行分割成字符串切片，并移除前导0
func acquireSegments(rawLine string) []string {
	parts := strings.Split(rawLine, " ")
	var normalized []string
	for _, seg := range parts {
		val, err := strconv.Atoi(seg)
		if err != nil {
			val = 0
		}
		normalized = append(normalized, strconv.Itoa(val))
	}
	return normalized
}

// sortByConcatPriority 使用自定义比较规则排序：a+b > b+a 则 a 排在 b 前
func sortByConcatPriority(strSlice []string) {
	sort.Slice(strSlice, func(i, j int) bool {
		combination1 := strSlice[i] + strSlice[j]
		combination2 := strSlice[j] + strSlice[i]
		return combination1 > combination2
	})
}

// checkAllZero 判断切片是否全由 "0" 组成
func checkAllZero(strSlice []string) bool {
	for _, val := range strSlice {
		if val != "0" {
			return false
		}
	}
	return true
}

func MainTest3() {
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		inputLine := scanner.Text()
		if len(inputLine) == 0 {
			continue
		}
		segmentList := acquireSegments(inputLine)
		sortByConcatPriority(segmentList)
		if checkAllZero(segmentList) {
			fmt.Println("0")
		} else {
			finalString := strings.Join(segmentList, "")
			fmt.Println(finalString)
		}
	}
}
