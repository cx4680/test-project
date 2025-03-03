package internal

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func engine() {
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
