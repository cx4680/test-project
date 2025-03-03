package internal

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

// acquireSegments 用户将输入行分割成字符串切片，并移除前导0（通过整型转换再转回字符串）
func acquireSegments(rawLine string) []string {
	parts := strings.Split(rawLine, " ")
	var normalized []string
	for _, seg := range parts {
		// 将字符串转为整数，自动去掉前导0
		val, err := strconv.Atoi(seg)
		if err != nil {
			// 如果解析失败，可视需求做特殊处理，这里简单视为0
			val = 0
		}
		// 再将整数转回字符串
		normalized = append(normalized, strconv.Itoa(val))
	}
	return normalized
}

// sortByConcatPriority 使用自定义比较规则进行排序
// 如果a+b > b+a 则说明a应该排在b前面
func sortByConcatPriority(strSlice []string) {
	sort.Slice(strSlice, func(i, j int) bool {
		combination1 := strSlice[i] + strSlice[j]
		combination2 := strSlice[j] + strSlice[i]
		return combination1 > combination2
	})
}

// checkAllZero 判断切片是否全是由“0”组成
func checkAllZero(strSlice []string) bool {
	zeroCount := 0
	for _, val := range strSlice {
		if val == "0" {
			zeroCount++
		}
	}
	return zeroCount == len(strSlice)
}

func MainTest3() {
	scanner := bufio.NewScanner(os.Stdin)
	// 持续从标准输入读取多行，直至EOF
	for scanner.Scan() {
		inputLine := scanner.Text()
		if len(inputLine) == 0 {
			// 跳过空行
			continue
		}
		// 提取并规范化切片（去掉前导0）
		segmentList := acquireSegments(inputLine)
		// 根据自定义拼接规则排序
		sortByConcatPriority(segmentList)
		// 判断是否全是0
		if checkAllZero(segmentList) {
			fmt.Println("0")
		} else {
			// 将排好序的切片拼接成结果
			finalString := strings.Join(segmentList, "")
			fmt.Println(finalString)
		}
	}
}
