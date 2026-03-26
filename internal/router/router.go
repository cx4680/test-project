package router

import (
	"my-test/internal/handler"

	"github.com/gin-gonic/gin"
)

func Setup() *gin.Engine {
	r := gin.Default()

	v1 := r.Group("/v1")
	{
		v1.GET("/hello", handler.Hello)
	}

	return r
}
