package internal

import (
	"bufio"
	"fmt"
	"os"
	"regexp"
	"sort"
	"strings"
)

// gatherProvisions 用于从标准输入中读取两行文本
func gatherProvisions() (string, string) {
	scanner := bufio.NewScanner(os.Stdin)

	// 第一行：含有英文单词和标点的字符串
	scanner.Scan()
	primeLine := scanner.Text()

	// 第二行：前缀
	scanner.Scan()
	prefixLine := scanner.Text()

	return primeLine, prefixLine
}

// refineVerbiage 将撇号替换为空格，并将所有非英文字母的字符替换为单个空格
func refineVerbiage(rawLine string) string {
	// 中间变量：先把撇号统一替换为空格
	replacedApostrophe := strings.ReplaceAll(rawLine, "'", " ")

	// 再把非英文字母字符替换成空格
	re := regexp.MustCompile(`[^a-zA-Z]+`)
	purified := re.ReplaceAllString(replacedApostrophe, " ")
	return purified
}

// unifyTokens 将字符串拆分为单子并去重
func unifyTokens(cleanLine string) []string {
	splitted := strings.Fields(cleanLine)

	// 利用map来去重
	uniqueContainer := make(map[string]bool)
	for _, w := range splitted {
		if w != "" {
			uniqueContainer[w] = true
		}
	}

	// 将去重后的结果放入切片
	var result []string
	for token := range uniqueContainer {
		result = append(result, token)
	}

	return result
}

// selectPrefixed 根据前缀在单词列表中进行筛选
func selectPrefixed(words []string, prefix string) []string {
	var matched []string
	for _, w := range words {
		if strings.HasPrefix(w, prefix) { // 区分大小写
			matched = append(matched, w)
		}
	}
	return matched
}

func MainTest1() {
	// 1.读取输入
	primeLine, prefixLine := gatherProvisions()

	// 2.预处理字符串
	intermediateLine := refineVerbiage(primeLine)

	// 3.分割并去重
	extractedTokens := unifyTokens(intermediateLine)

	// 4.根据前缀筛选
	selectedTokens := selectPrefixed(extractedTokens, prefixLine)

	// 5.输出结果
	if len(selectedTokens) == 0 {
		fmt.Println(prefixLine)
	} else {
		// 按字典序排序
		sort.Strings(selectedTokens)
		finalPhrase := strings.Join(selectedTokens, " ")
		fmt.Println(finalPhrase)
	}
}
